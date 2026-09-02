#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync } from 'node:fs';
import { mkdir, rm, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { homedir, tmpdir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { spawn } from 'node:child_process';

const [, , urlArg, outputDirArg] = process.argv;

if (!urlArg || !outputDirArg) {
  console.error('Usage: node scripts/capture-reference.mjs <url> <output-dir>');
  process.exit(2);
}

const url = new URL(urlArg).toString();
const outputDir = resolve(outputDirArg);
const outputFile = join(outputDir, 'page.mhtml');
const readmeFile = join(outputDir, 'README.md');
const settleMs = Number(process.env.CAPTURE_SETTLE_MS ?? 8000);
const headful = process.env.CAPTURE_HEADFUL === '1';

function browserCandidates() {
  const candidates = [
    process.env.BROWSER_PATH,
    process.env.EDGE_PATH,
    process.env.CHROME_PATH,
  ].filter(Boolean);

  if (process.platform === 'win32') {
    const pf = process.env.ProgramFiles || process.env.PROGRAMFILES;
    const pfx86 = process.env['ProgramFiles(x86)'] || process.env['PROGRAMFILES(X86)'];
    const local = process.env.LOCALAPPDATA;
    for (const base of [pf, pfx86, local].filter(Boolean)) {
      candidates.push(
        join(base, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
        join(base, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      );
    }
  } else if (process.platform === 'darwin') {
    candidates.push(
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      join(homedir(), 'Applications', 'Google Chrome.app', 'Contents', 'MacOS', 'Google Chrome'),
    );
  } else {
    candidates.push(
      '/usr/bin/microsoft-edge',
      '/usr/bin/microsoft-edge-stable',
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
    );
  }

  return [...new Set(candidates)];
}

function findBrowser() {
  const path = browserCandidates().find((candidate) => existsSync(candidate));
  if (!path) {
    throw new Error(
      'No Chromium browser found. Install Microsoft Edge/Google Chrome or set BROWSER_PATH to the executable.',
    );
  }
  return path;
}

async function getFreePort() {
  return new Promise((resolvePort, reject) => {
    const server = createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      const port = typeof address === 'object' && address ? address.port : null;
      server.close((error) => {
        if (error) reject(error);
        else if (!port) reject(new Error('Unable to allocate a local debugging port.'));
        else resolvePort(port);
      });
    });
  });
}

const sleep = (ms) => new Promise((resolveSleep) => setTimeout(resolveSleep, ms));

async function waitForJson(url, timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
      lastError = new Error(`${response.status} ${response.statusText}`);
    } catch (error) {
      lastError = error;
    }
    await sleep(200);
  }
  throw new Error(`Timed out waiting for Chrome DevTools endpoint: ${lastError?.message ?? 'unknown error'}`);
}

class CdpClient {
  constructor(webSocketUrl) {
    this.ws = new WebSocket(webSocketUrl);
    this.nextId = 1;
    this.pending = new Map();
  }

  async open() {
    await new Promise((resolveOpen, reject) => {
      this.ws.addEventListener('open', resolveOpen, { once: true });
      this.ws.addEventListener('error', () => reject(new Error('CDP WebSocket connection failed.')), { once: true });
    });

    this.ws.addEventListener('message', (event) => {
      const message = JSON.parse(event.data);
      if (!message.id) return;
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(`${message.error.code}: ${message.error.message}`));
      else pending.resolve(message.result ?? {});
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolveSend, reject) => {
      this.pending.set(id, { resolve: resolveSend, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  close() {
    this.ws.close();
  }
}

async function waitForReadyState(cdp, timeoutMs = 30000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const result = await cdp.send('Runtime.evaluate', {
        expression: 'document.readyState',
        returnByValue: true,
      });
      if (result?.result?.value === 'complete') return;
    } catch {
      // The execution context can briefly disappear during navigation.
    }
    await sleep(250);
  }
  throw new Error('Timed out waiting for document.readyState=complete.');
}

async function warmLazyContent(cdp) {
  const expression = String.raw`(async () => {
    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const maxScroll = Math.max(document.documentElement.scrollHeight, document.body?.scrollHeight || 0);
    const step = Math.max(500, Math.floor(window.innerHeight * 0.8));
    for (let y = 0; y < maxScroll; y += step) {
      window.scrollTo(0, y);
      await wait(180);
    }
    window.scrollTo(0, maxScroll);
    await wait(700);
    window.scrollTo(0, 0);
    await wait(500);
    return maxScroll;
  })()`;

  await cdp.send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
}

function makeReadme({ sourceUrl, capturedAt, sha256, browserPath, bytes }) {
  return `# Portfolio Visualizer Backtest Reference\n\n` +
    `- Source URL: ${sourceUrl}\n` +
    `- Captured at: ${capturedAt}\n` +
    `- Artifact: \`page.mhtml\`\n` +
    `- SHA-256: \`${sha256}\`\n` +
    `- Size: ${bytes} bytes\n` +
    `- Browser: ${basename(browserPath)}\n\n` +
    `## Scope\n\n` +
    `This is an external, non-normative reference captured from Portfolio Visualizer. ` +
    `It is for feature, layout, and interaction research only. It is not the implementation source of truth, ` +
    `a financial calculation contract, an acceptance criterion, or a golden test fixture.\n`;
}

let browserProcess;
let profileDir;
let cdp;

try {
  const browserPath = findBrowser();
  const port = await getFreePort();
  profileDir = join(tmpdir(), `portfolio-reference-capture-${process.pid}-${Date.now()}`);
  await mkdir(profileDir, { recursive: true });
  await mkdir(dirname(outputFile), { recursive: true });

  const args = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-extensions',
    '--window-size=1440,1200',
  ];
  if (!headful) args.push('--headless=new');
  args.push('about:blank');

  browserProcess = spawn(browserPath, args, {
    stdio: ['ignore', 'ignore', 'pipe'],
    windowsHide: !headful,
  });

  let browserStderr = '';
  browserProcess.stderr?.on('data', (chunk) => {
    browserStderr += chunk.toString();
  });

  browserProcess.once('error', (error) => {
    console.error(`Browser launch error: ${error.message}`);
  });

  const targets = await waitForJson(`http://127.0.0.1:${port}/json/list`);
  const pageTarget = targets.find((target) => target.type === 'page' && target.webSocketDebuggerUrl);
  if (!pageTarget) throw new Error(`No debuggable page target found. ${browserStderr}`);

  cdp = new CdpClient(pageTarget.webSocketDebuggerUrl);
  await cdp.open();
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Page.navigate', { url });
  await waitForReadyState(cdp);
  await sleep(settleMs);
  await warmLazyContent(cdp);
  await sleep(2000);

  const snapshot = await cdp.send('Page.captureSnapshot', { format: 'mhtml' });
  if (!snapshot.data) throw new Error('CDP Page.captureSnapshot returned no data.');

  const mhtml = snapshot.data;
  const sha256 = createHash('sha256').update(mhtml, 'utf8').digest('hex');
  const capturedAt = new Date().toISOString();
  const bytes = Buffer.byteLength(mhtml, 'utf8');

  await writeFile(outputFile, mhtml, 'utf8');
  await writeFile(
    readmeFile,
    makeReadme({ sourceUrl: url, capturedAt, sha256, browserPath, bytes }),
    'utf8',
  );

  console.log(`Captured: ${outputFile}`);
  console.log(`Metadata: ${readmeFile}`);
  console.log(`SHA-256: ${sha256}`);
  console.log(`Bytes: ${bytes}`);
} finally {
  try {
    cdp?.close();
  } catch {}
  try {
    browserProcess?.kill();
  } catch {}
  if (profileDir) {
    try {
      await rm(profileDir, { recursive: true, force: true });
    } catch {}
  }
}

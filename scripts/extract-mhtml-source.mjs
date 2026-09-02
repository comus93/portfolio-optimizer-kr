#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFile, rm, mkdir, writeFile } from 'node:fs/promises';
import { basename, extname, join, resolve } from 'node:path';

const [, , inputArg, outputArg] = process.argv;

if (!inputArg || !outputArg) {
  console.error('Usage: node scripts/extract-mhtml-source.mjs <page.mhtml> <output-dir>');
  process.exit(2);
}

const inputFile = resolve(inputArg);
const outputDir = resolve(outputArg);
const maxCharsPerFile = Number(process.env.MHTML_SOURCE_CHUNK_CHARS ?? 240000);

function parseHeaders(raw) {
  const unfolded = raw.replace(/\r?\n[ \t]+/g, ' ');
  const headers = new Map();
  for (const line of unfolded.split(/\r?\n/)) {
    const idx = line.indexOf(':');
    if (idx <= 0) continue;
    headers.set(line.slice(0, idx).trim().toLowerCase(), line.slice(idx + 1).trim());
  }
  return headers;
}

function getBoundary(contentType) {
  const match = /boundary=(?:"([^"]+)"|([^;\s]+))/i.exec(contentType ?? '');
  if (!match) throw new Error('MHTML multipart boundary was not found.');
  return match[1] ?? match[2];
}

function decodeQuotedPrintable(raw) {
  const text = raw.replace(/=\r?\n/g, '');
  const bytes = [];
  for (let i = 0; i < text.length; i += 1) {
    if (text[i] === '=' && /^[0-9A-Fa-f]{2}$/.test(text.slice(i + 1, i + 3))) {
      bytes.push(Number.parseInt(text.slice(i + 1, i + 3), 16));
      i += 2;
      continue;
    }
    const encoded = Buffer.from(text[i], 'utf8');
    for (const byte of encoded) bytes.push(byte);
  }
  return Buffer.from(bytes);
}

function decodeBody(body, transferEncoding) {
  const encoding = (transferEncoding ?? '').toLowerCase();
  if (encoding === 'base64') {
    return Buffer.from(body.replace(/\s+/g, ''), 'base64');
  }
  if (encoding === 'quoted-printable') {
    return decodeQuotedPrintable(body);
  }
  return Buffer.from(body, 'utf8');
}

function charsetFor(contentType) {
  const match = /charset=(?:"([^"]+)"|([^;\s]+))/i.exec(contentType ?? '');
  return (match?.[1] ?? match?.[2] ?? 'utf-8').toLowerCase();
}

function decodeText(buffer, charset) {
  if (['iso-8859-1', 'latin1', 'windows-1252'].includes(charset)) {
    return buffer.toString('latin1');
  }
  return buffer.toString('utf8');
}

function classify(contentType) {
  const mime = (contentType ?? '').split(';', 1)[0].trim().toLowerCase();
  if (mime === 'text/html' || mime === 'application/xhtml+xml') return { kind: 'html', ext: '.html' };
  if (mime === 'text/css') return { kind: 'style', ext: '.css' };
  if (['application/javascript', 'text/javascript', 'application/x-javascript'].includes(mime)) {
    return { kind: 'script', ext: '.js' };
  }
  if (mime === 'application/json' || mime.endsWith('+json')) return { kind: 'data', ext: '.json' };
  if (mime === 'image/svg+xml' || mime.endsWith('+xml') || mime === 'text/xml' || mime === 'application/xml') {
    return { kind: 'xml', ext: mime === 'image/svg+xml' ? '.svg' : '.xml' };
  }
  if (mime.startsWith('text/')) return { kind: 'text', ext: '.txt' };
  return null;
}

function sha256(buffer) {
  return createHash('sha256').update(buffer).digest('hex');
}

function safeBaseName(location) {
  if (!location) return null;
  try {
    const url = new URL(location);
    const candidate = basename(url.pathname);
    return candidate || null;
  } catch {
    return null;
  }
}

function splitText(text, maxChars) {
  if (text.length <= maxChars) return [text];
  const chunks = [];
  let offset = 0;
  while (offset < text.length) {
    let end = Math.min(offset + maxChars, text.length);
    if (end < text.length) {
      const newline = text.lastIndexOf('\n', end);
      if (newline > offset + Math.floor(maxChars * 0.7)) end = newline + 1;
    }
    chunks.push(text.slice(offset, end));
    offset = end;
  }
  return chunks;
}

const raw = await readFile(inputFile, 'utf8');
const firstBreak = raw.search(/\r?\n\r?\n/);
if (firstBreak < 0) throw new Error('Invalid MHTML: top-level header terminator was not found.');

const topHeadersRaw = raw.slice(0, firstBreak);
const topHeaders = parseHeaders(topHeadersRaw);
const boundary = getBoundary(topHeaders.get('content-type'));
const boundaryMarker = `--${boundary}`;
const rawParts = raw.split(boundaryMarker).slice(1);

await rm(outputDir, { recursive: true, force: true });
await mkdir(outputDir, { recursive: true });

const counters = new Map();
const manifest = {
  source_mhtml: basename(inputFile),
  source_sha256: sha256(Buffer.from(raw, 'utf8')),
  generated_at: new Date().toISOString(),
  extraction: 'Mechanical MIME-part extraction only. No summarization or semantic rewriting.',
  chunk_chars: maxCharsPerFile,
  parts: [],
};

let extractedCount = 0;
let omittedCount = 0;

for (const rawPart of rawParts) {
  let part = rawPart;
  if (part.startsWith('--')) break;
  part = part.replace(/^\r?\n/, '').replace(/\r?\n$/, '');
  if (!part.trim()) continue;

  const headerBreak = part.search(/\r?\n\r?\n/);
  if (headerBreak < 0) continue;

  const partHeadersRaw = part.slice(0, headerBreak);
  let body = part.slice(headerBreak).replace(/^\r?\n\r?\n/, '');
  body = body.replace(/\r?\n$/, '');

  const headers = parseHeaders(partHeadersRaw);
  const contentType = headers.get('content-type') ?? 'application/octet-stream';
  const transferEncoding = headers.get('content-transfer-encoding') ?? '';
  const contentLocation = headers.get('content-location') ?? null;
  const decoded = decodeBody(body, transferEncoding);
  const category = classify(contentType);

  const entry = {
    index: manifest.parts.length + 1,
    content_type: contentType,
    content_location: contentLocation,
    transfer_encoding: transferEncoding || null,
    decoded_bytes: decoded.length,
    decoded_sha256: sha256(decoded),
    outputs: [],
  };

  if (!category) {
    entry.status = 'omitted-non-text';
    omittedCount += 1;
    manifest.parts.push(entry);
    continue;
  }

  const charset = charsetFor(contentType);
  const text = decodeText(decoded, charset);
  const chunks = splitText(text, maxCharsPerFile);
  const n = (counters.get(category.kind) ?? 0) + 1;
  counters.set(category.kind, n);

  let stem;
  if (category.kind === 'html' && n === 1) {
    stem = 'page';
  } else {
    stem = `${category.kind}-${String(n).padStart(3, '0')}`;
  }

  const originalName = safeBaseName(contentLocation);
  if (originalName && extname(originalName) === category.ext && category.kind !== 'html') {
    entry.original_name = originalName;
  }

  for (let i = 0; i < chunks.length; i += 1) {
    const suffix = chunks.length === 1 ? '' : `.part-${String(i + 1).padStart(3, '0')}`;
    const filename = `${stem}${suffix}${category.ext}`;
    await writeFile(join(outputDir, filename), chunks[i], 'utf8');
    entry.outputs.push(filename);
  }

  entry.status = 'extracted';
  entry.charset = charset;
  extractedCount += 1;
  manifest.parts.push(entry);
}

await writeFile(join(outputDir, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');

console.log(`Input: ${inputFile}`);
console.log(`Output: ${outputDir}`);
console.log(`Extracted text parts: ${extractedCount}`);
console.log(`Omitted non-text parts: ${omittedCount}`);
console.log(`Manifest: ${join(outputDir, 'manifest.json')}`);

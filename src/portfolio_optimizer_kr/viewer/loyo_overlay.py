from __future__ import annotations

from pathlib import Path


_LOYO_OVERLAY = r"""
<style id="loyo-analysis-style">
#loyo-robustness .loyo-block { margin-top: 20px; }
#loyo-robustness .loyo-block:first-of-type { margin-top: 8px; }
#loyo-robustness .loyo-block h3 { margin: 0 0 7px; font-size: 15px; color: #243b64; }
#loyo-robustness .loyo-help { margin: 0 0 10px; color: #65748b; font-size: 12px; line-height: 1.45; }
#loyo-robustness .loyo-scroll { overflow-x: auto; }
#loyo-robustness table.loyo-matrix { width: max-content; min-width: 100%; border-collapse: collapse; font-size: 12px; }
#loyo-robustness .loyo-matrix th,
#loyo-robustness .loyo-matrix td { border: 1px solid #e4eaf3; padding: 7px 9px; white-space: nowrap; }
#loyo-robustness .loyo-matrix thead th { background: #f1f5fb; color: #334155; text-align: center; vertical-align: bottom; }
#loyo-robustness .loyo-year { background: #f8fafc; color: #1e365d; font-weight: 700; text-align: center; vertical-align: middle; min-width: 54px; }
#loyo-robustness .loyo-metric { background: #fbfcfe; color: #475569; font-weight: 600; text-align: left; min-width: 172px; }
#loyo-robustness .loyo-year-band-alt .loyo-year { background: #edf2f7; }
#loyo-robustness .loyo-year-band-alt .loyo-metric { background: #f1f5f9; }
#loyo-robustness .loyo-value { text-align: right; min-width: 86px; font-variant-numeric: tabular-nums; }
#loyo-robustness .loyo-delta-row .loyo-metric,
#loyo-robustness .loyo-delta-row .loyo-value { font-weight: 700; }
#loyo-robustness .loyo-year-start > * { border-top-width: 2px; border-top-color: #cbd5e1; }
#loyo-robustness .loyo-asset-head { min-width: 112px; }
#loyo-robustness .loyo-asset-name { display: block; max-width: 148px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }
#loyo-robustness .loyo-asset-ticker { display: block; margin-top: 2px; color: #64748b; font-size: 11px; font-weight: 700; }
#loyo-robustness .loyo-summary th:first-child,
#loyo-robustness .loyo-summary td:first-child,
#loyo-robustness .loyo-allocation th:first-child,
#loyo-robustness .loyo-allocation td:first-child { text-align: left; }
#loyo-robustness .loyo-summary td,
#loyo-robustness .loyo-allocation td { text-align: right; font-variant-numeric: tabular-nums; }
#loyo-robustness .loyo-baseline-row td { background: #f8fafc; font-weight: 700; }
#loyo-robustness .loyo-asset-legend { display: flex; flex-wrap: wrap; gap: 5px 18px; margin-top: 10px; color: #64748b; font-size: 11px; line-height: 1.4; }
#loyo-robustness .loyo-asset-legend span { white-space: nowrap; }
#loyo-robustness .loyo-asset-legend strong { color: #475569; }
</style>
<script id="loyo-analysis-overlay">
(() => {
  const finite = value => value !== null && value !== undefined && Number.isFinite(Number(value));
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
  const pct = value => finite(value) ? `${Number(value).toFixed(2)}%` : 'N/A';
  const signedPp = value => {
    if (!finite(value)) return 'N/A';
    const number = Number(value);
    const sign = number > 0 ? '+' : '';
    return `${sign}${number.toFixed(2)}%p`;
  };
  const signedNumber = value => {
    if (!finite(value)) return 'N/A';
    const number = Number(value);
    const sign = number > 0 ? '+' : '';
    return `${sign}${number.toFixed(2)}`;
  };
  const maxAbs = values => Math.max(
    ...values.filter(finite).map(value => Math.abs(Number(value))),
    1e-12,
  );
  const maxPositive = values => Math.max(
    ...values.filter(finite).map(Number),
    1e-12,
  );
  const background = (value, kind, scale) => {
    if (!finite(value)) return '';
    const number = Number(value);
    const ratio = Math.min(1, Math.abs(number) / Math.max(scale, 1e-12));
    if (kind === 'weight') {
      const alpha = 0.035 + ratio * 0.17;
      return `background:rgba(37,99,235,${alpha.toFixed(3)});`;
    }
    const positive = number >= 0;
    const strong = kind === 'delta';
    const alpha = (strong ? 0.055 : 0.035) + ratio * (strong ? 0.38 : 0.25);
    return positive
      ? `background:rgba(37,99,235,${alpha.toFixed(3)});`
      : `background:rgba(220,38,38,${alpha.toFixed(3)});`;
  };

  const render = () => {
    const data = window.PORTFOLIO_REPORT_DATA || {};
    const tables = data.tables || {};
    const influence = tables.asset_year_influence || [];
    const loyo = tables.loyo_robustness || [];
    const host = document.getElementById('loyo-robustness');
    if (!host || !influence.length || !loyo.length) return;

    const portfolioMetrics = document.getElementById('portfolio-metrics');
    const monthlyReturns = document.getElementById('monthly-returns');
    if (portfolioMetrics && monthlyReturns && host.parentNode === monthlyReturns.parentNode) {
      monthlyReturns.parentNode.insertBefore(host, monthlyReturns);
    }

    const optimizationRows = tables.optimization_results || [];
    const assetNames = new Map(
      optimizationRows
        .map(row => [String(row.ticker || ''), String(row.name || '')])
        .filter(([ticker]) => ticker)
    );
    const assets = optimizationRows.map(row => String(row.ticker || '')).filter(Boolean);
    influence.forEach(row => {
      const ticker = String(row.ticker || '');
      if (ticker && !assets.includes(ticker)) assets.push(ticker);
    });
    const assetHeader = ticker => {
      const name = assetNames.get(ticker) || ticker;
      return `<th class="loyo-asset-head"><span class="loyo-asset-name">${esc(name)}</span>`
        + `<span class="loyo-asset-ticker">${esc(ticker)}</span></th>`;
    };
    const years = [...new Set(influence.map(row => Number(row.year)).filter(Number.isFinite))]
      .sort((a,b) => a - b);
    const influenceByKey = new Map(
      influence.map(row => [`${Number(row.year)}|${String(row.ticker)}`, row])
    );

    const annualScale = maxAbs(influence.map(row => row.asset_annual_return_pct));
    const baselineScale = maxPositive(influence.map(row => row.baseline_weight_pct));
    const excludedScale = maxPositive(influence.map(row => row.excluded_year_weight_pct));
    const deltaScale = maxAbs(influence.map(row => row.delta_weight_pct));

    const metrics = [
      ['구성자산 해당년도 수익률', 'asset_annual_return_pct', 'return', annualScale, pct],
      ['전체기간 최적비중', 'baseline_weight_pct', 'weight', baselineScale, pct],
      ['해당년도 제외 최적비중', 'excluded_year_weight_pct', 'weight', excludedScale, pct],
      ['비중 변화', 'delta_weight_pct', 'delta', deltaScale, signedPp],
    ];

    const influenceBody = years.map((year, yearIndex) => metrics.map((metric, index) => {
      const [label, key, kind, scale, formatter] = metric;
      const cells = assets.map(asset => {
        const row = influenceByKey.get(`${year}|${asset}`) || {};
        const value = row[key];
        return `<td class="loyo-value" style="${background(value, kind, scale)}">${esc(formatter(value))}</td>`;
      }).join('');
      const bandClass = yearIndex % 2 === 1 ? 'loyo-year-band-alt ' : '';
      return `<tr class="${bandClass}${index === 0 ? 'loyo-year-start ' : ''}${kind === 'delta' ? 'loyo-delta-row' : ''}">`
        + (index === 0 ? `<th class="loyo-year" rowspan="4">${year}</th>` : '')
        + `<th class="loyo-metric">${esc(label)}</th>${cells}</tr>`;
    }).join('')).join('');

    const influenceTable = `
      <div class="loyo-block">
        <h3>Asset-Year Influence</h3>
        <p class="loyo-help">특정 연도의 구성자산 성과와, 그 연도를 제외했을 때 같은 자산의 최적비중 변화를 함께 본다. 배경 농도는 각 metric 안에서 값의 크기를 비교하기 위한 보조 표시이며 인과관계 판정은 아니다.</p>
        <div class="loyo-scroll"><table class="loyo-matrix loyo-influence">
          <thead><tr><th>Year</th><th>Metric</th>${assets.map(assetHeader).join('')}</tr></thead>
          <tbody>${influenceBody}</tbody>
        </table></div>
      </div>`;

    const deltaKeys = [...new Set(loyo.flatMap(row => Object.keys(row)))]
      .filter(key => key.startsWith('delta_weight_') && key.endsWith('_pct'));
    const shifts = row => deltaKeys
      .map(key => ({
        asset: key.slice('delta_weight_'.length, -'_pct'.length),
        value: row[key],
      }))
      .filter(item => finite(item.value))
      .sort((a,b) => Math.abs(Number(b.value)) - Math.abs(Number(a.value)))
      .slice(0,3);
    const abnormal = loyo.some(row =>
      row.feasible === false || !['optimal','optimal_inaccurate'].includes(String(row.status || ''))
    );
    const summaryHead = [
      'Excluded Year', 'Δ Return', 'Δ Sharpe', 'Reallocation',
      '1st Allocation Shift', '2nd Allocation Shift', '3rd Allocation Shift',
      ...(abnormal ? ['Status', 'Reason'] : []),
    ];
    const summaryBody = [...loyo]
      .sort((a,b) => Number(a.excluded_year) - Number(b.excluded_year))
      .map(row => {
        const top = shifts(row);
        const shiftCells = [0,1,2].map(index => {
          const item = top[index];
          return `<td>${item ? `${esc(item.asset)} ${esc(signedPp(item.value))}` : 'N/A'}</td>`;
        }).join('');
        const reallocation = finite(row.allocation_turnover)
          ? pct(Number(row.allocation_turnover) * 100)
          : 'N/A';
        const extra = abnormal
          ? `<td>${esc(row.status || 'N/A')}</td><td>${esc(row.message || '')}</td>`
          : '';
        return `<tr><td>${esc(row.excluded_year)}</td>`
          + `<td>${esc(signedPp(row.delta_expected_return_pct))}</td>`
          + `<td>${esc(signedNumber(row.delta_sharpe))}</td>`
          + `<td>${esc(reallocation)}</td>${shiftCells}${extra}</tr>`;
      }).join('');
    const assetLegend = `<div class="loyo-asset-legend" aria-label="Asset legend">${assets.map(asset => {
      const name = assetNames.get(asset) || asset;
      return `<span><strong>${esc(asset)}</strong> · ${esc(name)}</span>`;
    }).join('')}</div>`;
    const summaryTable = `
      <div class="loyo-block">
        <h3>LOYO Summary</h3>
        <p class="loyo-help">Reallocation은 전체기간 최적비중에서 해당 연도 제외 최적비중으로 다시 배치해야 하는 자본 비율이다. Allocation Shift는 절대 변화폭이 큰 순서의 signed 비중 변화다.</p>
        <div class="loyo-scroll"><table class="loyo-matrix loyo-summary">
          <thead><tr>${summaryHead.map(label => `<th>${esc(label)}</th>`).join('')}</tr></thead>
          <tbody>${summaryBody}</tbody>
        </table></div>
        ${assetLegend}
      </div>`;

    const firstYear = years[0];
    const baselineCells = assets.map(asset => {
      const row = influenceByKey.get(`${firstYear}|${asset}`) || {};
      return `<td>${esc(pct(row.baseline_weight_pct))}</td>`;
    }).join('');
    const allocationRows = years.map(year => {
      const cells = assets.map(asset => {
        const row = influenceByKey.get(`${year}|${asset}`) || {};
        if (!finite(row.excluded_year_weight_pct)) return '<td>N/A</td>';
        return `<td>${esc(pct(row.excluded_year_weight_pct))} (${esc(signedPp(row.delta_weight_pct))})</td>`;
      }).join('');
      return `<tr><td>${year}</td>${cells}</tr>`;
    }).join('');
    const allocationTable = `
      <div class="loyo-block">
        <h3>Allocation Changes</h3>
        <p class="loyo-help">괄호 안은 전체기간 최적비중 대비 변화폭이다.</p>
        <div class="loyo-scroll"><table class="loyo-matrix loyo-allocation">
          <thead><tr><th>Excluded Year</th>${assets.map(assetHeader).join('')}</tr></thead>
          <tbody><tr class="loyo-baseline-row"><td>Full Sample</td>${baselineCells}</tr>${allocationRows}</tbody>
        </table></div>
      </div>`;

    host.innerHTML = '<h2>Leave-One-Year-Out Robustness</h2>'
      + influenceTable + summaryTable + allocationTable;
  };

  if (document.readyState === 'complete') setTimeout(render, 120);
  else window.addEventListener('load', () => setTimeout(render, 120), {once:true});
})();
</script>
"""


def apply_loyo_analysis_overlay(output_path: str | Path) -> Path:
    path = Path(output_path)
    if not path.is_file():
        return path
    html = path.read_text(encoding="utf-8")
    if 'id="loyo-analysis-overlay"' in html:
        return path
    marker = "</body>"
    html = (
        html.replace(marker, f"{_LOYO_OVERLAY}\n{marker}", 1)
        if marker in html
        else f"{html}\n{_LOYO_OVERLAY}"
    )
    path.write_text(html, encoding="utf-8")
    return path

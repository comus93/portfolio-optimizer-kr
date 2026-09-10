from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


_START = "<!-- FRONTIER_RISK_DASHBOARD_START -->"
_END = "<!-- FRONTIER_RISK_DASHBOARD_END -->"


def _json_number(value: Any) -> float | int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    number = float(value)
    if not math.isfinite(number):
        return None
    if isinstance(value, int):
        return value
    return number


def build_frontier_interactive_payload(
    frontier: pd.DataFrame,
    overlay: pd.DataFrame,
    portfolio_returns: pd.DataFrame,
    symbols: list[str],
) -> dict[str, Any]:
    """Build a compact columnar payload for the static interactive report."""
    ordered_frontier = frontier.sort_values("point").reset_index(drop=True)
    ordered_overlay = overlay.sort_values("point").reset_index(drop=True)
    points = [int(value) for value in ordered_overlay["point"].tolist()]

    if points != [int(value) for value in ordered_frontier["point"].tolist()]:
        raise ValueError("frontier and overlay point identities do not match")
    if points != [int(value) for value in portfolio_returns.columns.tolist()]:
        raise ValueError("portfolio return matrix point identities do not match")

    metric_columns = [
        "cagr_pct",
        "ex_post_sharpe",
        "monthly_gain_to_pain_ratio",
        "pain_ratio",
        "maximum_drawdown_pct",
        "mdd_depth_pct",
        "tuw_pct",
        "pain_index_pct",
        "max_underwater_months",
        "expected_return_pct",
        "volatility_pct",
    ]
    metrics = {
        column: [_json_number(value) for value in ordered_overlay[column].tolist()]
        for column in metric_columns
    }

    weights_pct = []
    for _, row in ordered_frontier.iterrows():
        weights_pct.append(
            [_json_number(row[f"weight_{symbol}_pct"]) for symbol in symbols]
        )

    monthly_returns_pct = []
    for point in points:
        monthly_returns_pct.append(
            [_json_number(value * 100.0) for value in portfolio_returns[point].tolist()]
        )

    max_index = ordered_overlay["ex_post_sharpe"].idxmax()
    default_point = int(ordered_overlay.loc[max_index, "point"])

    return {
        "schema_version": 1,
        "frequency": "monthly",
        "dates": [timestamp.date().isoformat() for timestamp in portfolio_returns.index],
        "points": points,
        "symbols": symbols,
        "weights_pct": weights_pct,
        "monthly_returns_pct": monthly_returns_pct,
        "metrics": metrics,
        "segments": ordered_overlay["segment"].astype(str).tolist(),
        "default_point": default_point,
        "definitions": {
            "pain_index_pct": "Average percentage distance below the prior portfolio peak across all monthly observations.",
            "pain_ratio": "Annualized excess CAGR divided by Pain Index.",
            "monthly_gain_to_pain_ratio": "Arithmetic sum of all monthly returns divided by the absolute arithmetic sum of losing-month returns.",
            "tuw_pct": "Percentage of monthly observations below the prior portfolio peak.",
        },
    }


def write_frontier_interactive_payload(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )


def inject_frontier_risk_dashboard(report_path: Path, payload: dict[str, Any]) -> None:
    """Inject a self-contained client-side frontier dashboard into report.html."""
    html = report_path.read_text(encoding="utf-8")

    start = html.find(_START)
    end = html.find(_END)
    if start >= 0 and end >= start:
        html = html[:start] + html[end + len(_END) :]

    payload_json = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")

    block = f'''{_START}
<style id="frontier-risk-dashboard-style">
#frontier-risk-dashboard .fr-note{{margin:-4px 0 14px;color:#65748b;font-size:13px;line-height:1.5}}
#frontier-risk-dashboard .fr-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
#frontier-risk-dashboard .fr-card{{border:1px solid #e2e8f2;border-radius:9px;padding:11px;background:#fbfdff;cursor:crosshair}}
#frontier-risk-dashboard .fr-card-head{{display:flex;justify-content:space-between;gap:8px;align-items:baseline}}
#frontier-risk-dashboard .fr-label{{font-size:12px;font-weight:700;color:#334155}}
#frontier-risk-dashboard .fr-value{{font-size:18px;font-weight:750;color:#172033}}
#frontier-risk-dashboard .fr-help{{min-height:30px;margin:4px 0 2px;color:#718096;font-size:11px;line-height:1.35}}
#frontier-risk-dashboard .fr-spark{{width:100%;height:92px;display:block;background:#fff}}
#frontier-risk-dashboard .fr-selected{{display:grid;grid-template-columns:minmax(280px,.8fr) minmax(420px,1.4fr);gap:16px;margin-top:18px}}
#frontier-risk-dashboard .fr-panel{{border:1px solid #e2e8f2;border-radius:9px;padding:13px;background:#fff}}
#frontier-risk-dashboard .fr-panel h3{{margin:0 0 6px}}
#frontier-risk-dashboard .fr-meta{{color:#65748b;font-size:12px;margin-bottom:10px}}
#frontier-risk-dashboard .fr-weight-table{{width:100%;border-collapse:collapse;font-size:12px}}
#frontier-risk-dashboard .fr-weight-table td,#frontier-risk-dashboard .fr-weight-table th{{padding:6px 7px;border:1px solid #e4eaf3}}
#frontier-risk-dashboard .fr-weight-table th{{text-align:left;background:#f1f5fb}}
#frontier-risk-dashboard .fr-weight-table td:last-child{{text-align:right}}
#frontier-risk-dashboard .fr-dd{{width:100%;height:220px;display:block;background:#fff}}
#frontier-risk-dashboard .fr-foot{{margin-top:8px;color:#718096;font-size:11px;line-height:1.45}}
@media(max-width:780px){{#frontier-risk-dashboard .fr-selected{{grid-template-columns:1fr}}}}
</style>
<section id="frontier-risk-dashboard">
  <h2>Frontier Risk Trade-off</h2>
  <p class="fr-note">Each mini-chart shows all efficient-frontier points. Click anywhere on a chart to select the nearest point. The selected portfolio, metrics, weights, and drawdown path update together. No sweet-spot rule is applied.</p>
  <div class="fr-grid" id="fr-metric-grid"></div>
  <div class="fr-selected">
    <div class="fr-panel">
      <h3 id="fr-selected-title">Selected Frontier Point</h3>
      <div class="fr-meta" id="fr-selected-meta"></div>
      <div id="fr-weight-table"></div>
    </div>
    <div class="fr-panel">
      <h3>Selected Point Drawdown</h3>
      <div class="fr-meta" id="fr-drawdown-meta"></div>
      <div id="fr-drawdown-chart"></div>
      <div class="fr-foot">Pain Index: average distance below the prior peak across the full sample. Monthly Gain-to-Pain: net arithmetic monthly return sum divided by the absolute sum of losing months.</div>
    </div>
  </div>
</section>
<script id="frontier-risk-dashboard-data" type="application/json">{payload_json}</script>
<script id="frontier-risk-dashboard-script">
(() => {{
  const dataEl = document.getElementById('frontier-risk-dashboard-data');
  const root = document.getElementById('frontier-risk-dashboard');
  if (!dataEl || !root) return;
  const data = JSON.parse(dataEl.textContent);
  const points = data.points || [];
  const metrics = data.metrics || {{}};
  if (!points.length) return;

  const configs = [
    ['cagr_pct','CAGR','Annualized compound growth','pct'],
    ['ex_post_sharpe','Sharpe Ratio','Realized excess return per unit of volatility','ratio'],
    ['monthly_gain_to_pain_ratio','Monthly Gain-to-Pain','Net monthly return sum per unit of losing-month return','ratio'],
    ['pain_ratio','Pain Ratio','Excess CAGR per unit of Pain Index','ratio'],
    ['maximum_drawdown_pct','Maximum Drawdown','Deepest realized peak-to-trough loss','pct'],
    ['tuw_pct','Time Under Water','Share of months below the prior peak','pct'],
    ['pain_index_pct','Pain Index','Average distance below the prior peak across all months','pct'],
    ['max_underwater_months','Max Underwater','Longest consecutive time below the prior peak','months'],
  ];

  const fmt = (value, kind) => {{
    if (value === null || value === undefined || !Number.isFinite(Number(value))) return 'N/A';
    const v = Number(value);
    if (kind === 'pct') return `${{v.toFixed(2)}}%`;
    if (kind === 'months') return `${{Math.round(v)}} mo`;
    return v.toFixed(3);
  }};

  const pointIndex = point => points.indexOf(Number(point));
  const hashMatch = location.hash.match(/frontier-point=(\d+)/);
  let selected = hashMatch ? pointIndex(hashMatch[1]) : pointIndex(data.default_point);
  if (selected < 0) selected = 0;

  const nearestIndex = (event, svg, padding, width) => {{
    const rect = svg.getBoundingClientRect();
    const local = (event.clientX - rect.left) / Math.max(rect.width, 1) * width;
    const share = Math.min(1, Math.max(0, (local - padding) / Math.max(width - 2 * padding, 1)));
    return Math.round(share * Math.max(points.length - 1, 0));
  }};

  const renderMetricCard = (config, index) => {{
    const [key,label,help,kind] = config;
    const values = (metrics[key] || []).map(v => v === null ? null : Number(v));
    const card = document.createElement('div');
    card.className = 'fr-card';
    const head = document.createElement('div');
    head.className = 'fr-card-head';
    head.innerHTML = `<span class="fr-label">${{label}}</span><span class="fr-value">${{fmt(values[index],kind)}}</span>`;
    card.appendChild(head);
    const hint = document.createElement('div');
    hint.className = 'fr-help';
    hint.textContent = help;
    card.appendChild(hint);

    const valid = values.filter(v => Number.isFinite(v));
    if (!valid.length) return card;
    let min = Math.min(...valid), max = Math.max(...valid);
    if (min === max) {{ min -= 1; max += 1; }}
    const w=320,h=92,p=10;
    const x=i=>p+i*(w-2*p)/Math.max(points.length-1,1);
    const y=v=>h-p-(v-min)*(h-2*p)/(max-min);
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox',`0 0 ${{w}} ${{h}}`);
    svg.setAttribute('class','fr-spark');
    const zero = key === 'maximum_drawdown_pct' && min < 0 && max > 0;
    if (zero) {{
      const z=document.createElementNS(ns,'line');
      z.setAttribute('x1',p);z.setAttribute('x2',w-p);z.setAttribute('y1',y(0));z.setAttribute('y2',y(0));z.setAttribute('stroke','#e2e8f0');svg.appendChild(z);
    }}
    const pts=[];
    values.forEach((v,i)=>{{if(Number.isFinite(v))pts.push(`${{x(i)}},${{y(v)}}`)}});
    const line=document.createElementNS(ns,'polyline');
    line.setAttribute('points',pts.join(' '));line.setAttribute('fill','none');line.setAttribute('stroke','#2563eb');line.setAttribute('stroke-width','2');svg.appendChild(line);
    const marker=document.createElementNS(ns,'line');
    marker.setAttribute('x1',x(index));marker.setAttribute('x2',x(index));marker.setAttribute('y1',p);marker.setAttribute('y2',h-p);marker.setAttribute('stroke','#ef4444');marker.setAttribute('stroke-width','1.3');svg.appendChild(marker);
    if (Number.isFinite(values[index])) {{
      const dot=document.createElementNS(ns,'circle');
      dot.setAttribute('cx',x(index));dot.setAttribute('cy',y(values[index]));dot.setAttribute('r','3.5');dot.setAttribute('fill','#ef4444');svg.appendChild(dot);
    }}
    svg.addEventListener('click', event => select(nearestIndex(event, svg, p, w)));
    card.appendChild(svg);
    return card;
  }};

  const drawdownSeries = index => {{
    const returns = (data.monthly_returns_pct[index] || []).map(v => Number(v) / 100);
    let wealth=1, peak=1;
    return returns.map(r => {{
      wealth *= (1+r); peak = Math.max(peak, wealth); return (wealth/peak-1)*100;
    }});
  }};

  const renderDrawdown = index => {{
    const slot=document.getElementById('fr-drawdown-chart');
    const meta=document.getElementById('fr-drawdown-meta');
    const values=drawdownSeries(index);
    if(!slot || !values.length) return;
    const min=Math.min(...values, -0.01), max=0;
    const w=800,h=220,p=34,ns='http://www.w3.org/2000/svg';
    const x=i=>p+i*(w-2*p)/Math.max(values.length-1,1);
    const y=v=>p+(max-v)*(h-2*p)/(max-min);
    const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 ${{w}} ${{h}}`);svg.setAttribute('class','fr-dd');
    const zero=document.createElementNS(ns,'line');zero.setAttribute('x1',p);zero.setAttribute('x2',w-p);zero.setAttribute('y1',y(0));zero.setAttribute('y2',y(0));zero.setAttribute('stroke','#94a3b8');svg.appendChild(zero);
    const line=document.createElementNS(ns,'polyline');line.setAttribute('points',values.map((v,i)=>`${{x(i)}},${{y(v)}}`).join(' '));line.setAttribute('fill','none');line.setAttribute('stroke','#dc2626');line.setAttribute('stroke-width','2');svg.appendChild(line);
    const minIndex=values.indexOf(Math.min(...values));
    const dot=document.createElementNS(ns,'circle');dot.setAttribute('cx',x(minIndex));dot.setAttribute('cy',y(values[minIndex]));dot.setAttribute('r','4');dot.setAttribute('fill','#dc2626');svg.appendChild(dot);
    const start=document.createElementNS(ns,'text');start.setAttribute('x',p);start.setAttribute('y',h-8);start.setAttribute('font-size','11');start.setAttribute('fill','#64748b');start.textContent=data.dates[0]||'';svg.appendChild(start);
    const end=document.createElementNS(ns,'text');end.setAttribute('x',w-p);end.setAttribute('y',h-8);end.setAttribute('font-size','11');end.setAttribute('text-anchor','end');end.setAttribute('fill','#64748b');end.textContent=data.dates[data.dates.length-1]||'';svg.appendChild(end);
    slot.innerHTML='';slot.appendChild(svg);
    if(meta) meta.textContent=`MDD ${{fmt(metrics.maximum_drawdown_pct[index],'pct')}} · TUW ${{fmt(metrics.tuw_pct[index],'pct')}} · Pain ${{fmt(metrics.pain_index_pct[index],'pct')}} · Max underwater ${{fmt(metrics.max_underwater_months[index],'months')}}`;
  }};

  const renderWeights = index => {{
    const slot=document.getElementById('fr-weight-table'); if(!slot) return;
    const rows=data.symbols.map((symbol,i)=>[symbol,Number(data.weights_pct[index][i]||0)]).sort((a,b)=>b[1]-a[1]);
    slot.innerHTML=`<table class="fr-weight-table"><thead><tr><th>Asset</th><th>Weight</th></tr></thead><tbody>${{rows.map(row=>`<tr><td>${{row[0]}}</td><td>${{row[1].toFixed(2)}}%</td></tr>`).join('')}}</tbody></table>`;
  }};

  const render = () => {{
    const grid=document.getElementById('fr-metric-grid'); if(!grid) return;
    grid.innerHTML=''; configs.forEach(config=>grid.appendChild(renderMetricCard(config,selected)));
    const point=points[selected];
    const title=document.getElementById('fr-selected-title');
    if(title) title.textContent=`Frontier Point ${{point}}${{point===Number(data.default_point)?' · Maximum Sharpe':''}}`;
    const meta=document.getElementById('fr-selected-meta');
    if(meta) meta.textContent=`Expected return ${{fmt(metrics.expected_return_pct[selected],'pct')}} · Volatility ${{fmt(metrics.volatility_pct[selected],'pct')}} · ${{data.segments[selected]||''}}`;
    renderWeights(selected); renderDrawdown(selected);
  }};

  const select = index => {{
    selected=Math.min(points.length-1,Math.max(0,index));
    history.replaceState(null,'',`${{location.pathname}}${{location.search}}#frontier-point=${{points[selected]}}`);
    render();
  }};

  render();
}})();
</script>
{_END}'''

    anchor = '<section id="efficient-frontier"'
    section_start = html.find(anchor)
    if section_start >= 0:
        section_end = html.find("</section>", section_start)
        if section_end >= 0:
            insert_at = section_end + len("</section>")
            html = html[:insert_at] + "\n" + block + "\n" + html[insert_at:]
        else:
            section_start = -1
    if section_start < 0:
        main_end = html.rfind("</main>")
        if main_end < 0:
            raise ValueError("report.html has no insertion anchor")
        html = html[:main_end] + block + "\n" + html[main_end:]

    report_path.write_text(html, encoding="utf-8")

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


def _drawdown_pct(series: pd.Series) -> list[float | int | None]:
    clean = series.astype(float)
    wealth = (1.0 + clean).cumprod()
    drawdown = wealth.div(wealth.cummax()).sub(1.0).mul(100.0)
    return [_json_number(value) for value in drawdown.tolist()]


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
    drawdown_pct = []
    for point in points:
        series = portfolio_returns[point]
        monthly_returns_pct.append(
            [_json_number(value * 100.0) for value in series.tolist()]
        )
        drawdown_pct.append(_drawdown_pct(series))

    max_index = ordered_overlay["ex_post_sharpe"].idxmax()
    default_point = int(ordered_overlay.loc[max_index, "point"])

    return {
        "schema_version": 2,
        "frequency": "monthly",
        "dates": [timestamp.date().isoformat() for timestamp in portfolio_returns.index],
        "points": points,
        "symbols": symbols,
        "weights_pct": weights_pct,
        "monthly_returns_pct": monthly_returns_pct,
        "drawdown_pct": drawdown_pct,
        "metrics": metrics,
        "segments": ordered_overlay["segment"].astype(str).tolist(),
        "default_point": default_point,
        "definitions": {
            "cagr_pct": "연복리 수익률 (%)",
            "ex_post_sharpe": "샤프지수",
            "monthly_gain_to_pain_ratio": "손실이 난 달들의 총 손실 1단위당, 최종적으로 얼마의 순수익을 남겼는가",
            "pain_ratio": "전고점 아래에서 겪은 낙폭 부담 1단위당 최종적으로 얼마의 연환산 초과수익을 얻었는가 (낙폭 부담은 하락의 깊이와 지속기간을 함께 반영)",
            "maximum_drawdown_pct": "낙폭 (%)",
            "tuw_pct": "이전 최고점을 회복하지 못하는 기간(물려있는 기간)",
            "pain_index_pct": "평균 낙폭 (깊이와 지속시간 반영)",
            "max_underwater_months": "최장 미회복 기간 (개월)",
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

    template = r'''
<style id="frontier-risk-dashboard-style">
#frontier-risk-dashboard .fr-note{margin:-4px 0 14px;color:#65748b;font-size:13px;line-height:1.55}
#frontier-risk-dashboard .fr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
#frontier-risk-dashboard .fr-card{position:relative;border:1px solid #e2e8f2;border-radius:9px;padding:11px;background:#fbfdff;cursor:crosshair}
#frontier-risk-dashboard .fr-card-head{display:flex;justify-content:space-between;gap:8px;align-items:baseline}
#frontier-risk-dashboard .fr-label{font-size:12px;font-weight:700;color:#334155}
#frontier-risk-dashboard .fr-value{font-size:18px;font-weight:750;color:#172033}
#frontier-risk-dashboard .fr-help{min-height:44px;margin:4px 0 4px;color:#5f6f84;font-size:11px;line-height:1.42}
#frontier-risk-dashboard .fr-spark{width:100%;height:158px;display:block;background:#fff}
#frontier-risk-dashboard .fr-tooltip{position:absolute;z-index:4;display:none;pointer-events:none;padding:5px 7px;border:1px solid #cbd5e1;border-radius:6px;background:rgba(255,255,255,.97);box-shadow:0 2px 8px rgba(15,23,42,.12);font-size:10px;line-height:1.35;color:#334155;white-space:nowrap}
#frontier-risk-dashboard .fr-selected{display:grid;grid-template-columns:minmax(280px,.8fr) minmax(420px,1.4fr);gap:16px;margin-top:18px}
#frontier-risk-dashboard .fr-panel{border:1px solid #e2e8f2;border-radius:9px;padding:13px;background:#fff}
#frontier-risk-dashboard .fr-panel h3{margin:0 0 6px}
#frontier-risk-dashboard .fr-meta{color:#65748b;font-size:12px;margin-bottom:10px}
#frontier-risk-dashboard .fr-weight-table{width:100%;border-collapse:collapse;font-size:12px}
#frontier-risk-dashboard .fr-weight-table td,#frontier-risk-dashboard .fr-weight-table th{padding:6px 7px;border:1px solid #e4eaf3}
#frontier-risk-dashboard .fr-weight-table th{text-align:left;background:#f1f5fb}
#frontier-risk-dashboard .fr-weight-table td:last-child{text-align:right}
#frontier-risk-dashboard .fr-dd{width:100%;height:250px;display:block;background:#fff}
#frontier-risk-dashboard .fr-foot{margin-top:8px;color:#718096;font-size:11px;line-height:1.45}
@media(max-width:780px){#frontier-risk-dashboard .fr-selected{grid-template-columns:1fr}}
</style>
<section id="frontier-risk-dashboard">
  <h2>Frontier Risk Trade-off</h2>
  <p class="fr-note">Efficient Frontier의 모든 포트폴리오를 실제 연환산 변동성(가로축) 순서로 비교합니다. 어느 차트에서든 점을 선택하면 8개 지표, 자산 비중, Drawdown 경로가 같은 포트폴리오로 함께 바뀝니다. 자동 Sweet Spot 판정은 적용하지 않습니다.</p>
  <div class="fr-grid" id="fr-metric-grid"></div>
  <div class="fr-selected">
    <div class="fr-panel">
      <h3 id="fr-selected-title">선택한 Frontier Point</h3>
      <div class="fr-meta" id="fr-selected-meta"></div>
      <div id="fr-weight-table"></div>
    </div>
    <div class="fr-panel">
      <h3>선택 포트폴리오 Drawdown</h3>
      <div class="fr-meta" id="fr-drawdown-meta"></div>
      <div id="fr-drawdown-chart"></div>
      <div class="fr-foot">Pain Index는 전체 기간에서 전고점 대비 평균 낙폭을 측정해 깊이와 지속시간을 함께 반영합니다. Monthly Gain-to-Pain은 손실이 난 달들의 총 손실에 비해 최종적으로 남긴 순수익을 측정합니다.</div>
    </div>
  </div>
</section>
<script id="frontier-risk-dashboard-data" type="application/json">__PAYLOAD__</script>
<script id="frontier-risk-dashboard-script">
(() => {
  const dataEl = document.getElementById('frontier-risk-dashboard-data');
  const root = document.getElementById('frontier-risk-dashboard');
  if (!dataEl || !root) return;
  const data = JSON.parse(dataEl.textContent);
  const points = data.points || [];
  const metrics = data.metrics || {};
  const volatility = (metrics.volatility_pct || []).map(Number);
  if (!points.length || !volatility.length) return;

  const configs = [
    ['cagr_pct','CAGR','연복리 수익률 (%)','연복리 수익률 (%)','pct'],
    ['ex_post_sharpe','Sharpe Ratio','샤프지수','샤프지수','ratio'],
    ['monthly_gain_to_pain_ratio','Monthly Gain-to-Pain','손실이 난 달들의 총 손실 1단위당, 최종적으로 얼마의 순수익을 남겼는가','Gain-to-Pain','ratio'],
    ['pain_ratio','Pain Ratio','전고점 아래에서 겪은 낙폭 부담 1단위당 최종적으로 얼마의 연환산 초과수익을 얻었는가 (낙폭 부담은 하락의 깊이와 지속기간을 함께 반영)','Pain Ratio','ratio'],
    ['maximum_drawdown_pct','Maximum Drawdown','낙폭 (%)','낙폭 (%)','pct'],
    ['tuw_pct','Time Under Water','이전 최고점을 회복하지 못하는 기간(물려있는 기간)','미회복 기간 비율 (%)','pct'],
    ['pain_index_pct','Pain Index','평균 낙폭 (깊이와 지속시간 반영)','평균 낙폭 (%)','pct'],
    ['max_underwater_months','Max Underwater','최장 미회복 기간 (개월)','최장 미회복 기간 (개월)','months'],
  ];

  const fmt = (value, kind) => {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) return 'N/A';
    const v = Number(value);
    if (kind === 'pct') return `${v.toFixed(2)}%`;
    if (kind === 'months') return `${Math.round(v)}개월`;
    return v.toFixed(3);
  };

  const axisFmt = (value, kind) => {
    if (!Number.isFinite(Number(value))) return '';
    const v = Number(value);
    if (kind === 'months') return `${Math.round(v)}`;
    if (kind === 'ratio') return Math.abs(v) >= 10 ? v.toFixed(1) : v.toFixed(2);
    return v.toFixed(1);
  };

  const pointIndex = point => points.indexOf(Number(point));
  const hashMatch = location.hash.match(/frontier-point=(\d+)/);
  let selected = hashMatch ? pointIndex(hashMatch[1]) : pointIndex(data.default_point);
  if (selected < 0) selected = 0;

  const extentWithPadding = values => {
    const valid = values.filter(v => Number.isFinite(v));
    if (!valid.length) return [0, 1];
    let min = Math.min(...valid), max = Math.max(...valid);
    if (min === max) {
      const pad = Math.abs(min) > 1e-12 ? Math.abs(min) * 0.08 : 1;
      return [min - pad, max + pad];
    }
    const pad = (max - min) * 0.08;
    return [min - pad, max + pad];
  };

  const xDomain = extentWithPadding(volatility);

  const nearestIndexByVol = (event, svg, paddingLeft, paddingRight, width) => {
    const rect = svg.getBoundingClientRect();
    const local = (event.clientX - rect.left) / Math.max(rect.width, 1) * width;
    const plotWidth = width - paddingLeft - paddingRight;
    const clipped = Math.min(width - paddingRight, Math.max(paddingLeft, local));
    const targetVol = xDomain[0] + (clipped - paddingLeft) / Math.max(plotWidth, 1) * (xDomain[1] - xDomain[0]);
    let best = 0, bestDistance = Infinity;
    volatility.forEach((value, index) => {
      const d = Math.abs(value - targetVol);
      if (d < bestDistance) { bestDistance = d; best = index; }
    });
    return best;
  };

  const svgText = (ns, x, y, text, attrs={}) => {
    const node = document.createElementNS(ns,'text');
    node.setAttribute('x',x); node.setAttribute('y',y); node.textContent=text;
    Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,v));
    return node;
  };

  const renderMetricCard = (config, index) => {
    const [key,label,help,yLabel,kind] = config;
    const values = (metrics[key] || []).map(v => v === null ? null : Number(v));
    const card = document.createElement('div');
    card.className = 'fr-card';

    const head = document.createElement('div');
    head.className = 'fr-card-head';
    head.innerHTML = `<span class="fr-label">${label}</span><span class="fr-value">${fmt(values[index],kind)}</span>`;
    card.appendChild(head);

    const hint = document.createElement('div');
    hint.className = 'fr-help';
    hint.textContent = help;
    card.appendChild(hint);

    const valid = values.filter(v => Number.isFinite(v));
    if (!valid.length) return card;

    const [yMin,yMax] = extentWithPadding(valid);
    const w=360,h=158,left=48,right=12,top=18,bottom=38;
    const plotW=w-left-right, plotH=h-top-bottom;
    const x=v=>left+(Number(v)-xDomain[0])*plotW/Math.max(xDomain[1]-xDomain[0],1e-12);
    const y=v=>top+(yMax-Number(v))*plotH/Math.max(yMax-yMin,1e-12);
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox',`0 0 ${w} ${h}`);
    svg.setAttribute('class','fr-spark');

    const xTicks=[xDomain[0],(xDomain[0]+xDomain[1])/2,xDomain[1]];
    const yTicks=[yMin,(yMin+yMax)/2,yMax];

    xTicks.forEach(tick=>{
      const gx=x(tick);
      const grid=document.createElementNS(ns,'line');
      grid.setAttribute('x1',gx);grid.setAttribute('x2',gx);grid.setAttribute('y1',top);grid.setAttribute('y2',h-bottom);
      grid.setAttribute('stroke','#eef2f7');svg.appendChild(grid);
      svg.appendChild(svgText(ns,gx,h-20,`${tick.toFixed(1)}%`,{'font-size':'9','fill':'#64748b','text-anchor':'middle'}));
    });

    yTicks.forEach(tick=>{
      const gy=y(tick);
      const grid=document.createElementNS(ns,'line');
      grid.setAttribute('x1',left);grid.setAttribute('x2',w-right);grid.setAttribute('y1',gy);grid.setAttribute('y2',gy);
      grid.setAttribute('stroke','#eef2f7');svg.appendChild(grid);
      svg.appendChild(svgText(ns,left-5,gy+3,axisFmt(tick,kind),{'font-size':'9','fill':'#64748b','text-anchor':'end'}));
    });

    svg.appendChild(svgText(ns,left,10,yLabel,{'font-size':'9','fill':'#64748b'}));
    svg.appendChild(svgText(ns,left+plotW/2,h-5,'연환산 변동성 (%)',{'font-size':'9','fill':'#64748b','text-anchor':'middle'}));

    const pts=[];
    values.forEach((v,i)=>{
      if(Number.isFinite(v) && Number.isFinite(volatility[i])) pts.push(`${x(volatility[i])},${y(v)}`);
    });
    const line=document.createElementNS(ns,'polyline');
    line.setAttribute('points',pts.join(' '));line.setAttribute('fill','none');line.setAttribute('stroke','#2563eb');line.setAttribute('stroke-width','2');svg.appendChild(line);

    const marker=document.createElementNS(ns,'line');
    marker.setAttribute('x1',x(volatility[index]));marker.setAttribute('x2',x(volatility[index]));marker.setAttribute('y1',top);marker.setAttribute('y2',h-bottom);
    marker.setAttribute('stroke','#ef4444');marker.setAttribute('stroke-width','1.3');svg.appendChild(marker);

    if (Number.isFinite(values[index])) {
      const dot=document.createElementNS(ns,'circle');
      dot.setAttribute('cx',x(volatility[index]));dot.setAttribute('cy',y(values[index]));dot.setAttribute('r','3.8');dot.setAttribute('fill','#ef4444');
      const title=document.createElementNS(ns,'title');
      title.textContent=`Point ${points[index]} · 변동성 ${volatility[index].toFixed(2)}% · ${label} ${fmt(values[index],kind)}`;
      dot.appendChild(title);svg.appendChild(dot);
    }

    const tooltip=document.createElement('div');
    tooltip.className='fr-tooltip';
    card.appendChild(tooltip);

    svg.addEventListener('pointermove', event => {
      const hover=nearestIndexByVol(event,svg,left,right,w);
      tooltip.textContent=`Point ${points[hover]} · 변동성 ${volatility[hover].toFixed(2)}% · ${label} ${fmt(values[hover],kind)}`;
      const rect=card.getBoundingClientRect();
      tooltip.style.left=`${Math.min(event.clientX-rect.left+8, Math.max(rect.width-230, 4))}px`;
      tooltip.style.top=`${Math.max(event.clientY-rect.top-30, 4)}px`;
      tooltip.style.display='block';
    });
    svg.addEventListener('pointerleave',()=>{tooltip.style.display='none';});
    svg.addEventListener('click', event => select(nearestIndexByVol(event, svg, left, right, w)));
    card.appendChild(svg);
    return card;
  };

  const renderDrawdown = index => {
    const slot=document.getElementById('fr-drawdown-chart');
    const meta=document.getElementById('fr-drawdown-meta');
    const values=((data.drawdown_pct || [])[index] || []).map(Number);
    if(!slot || !values.length) return;

    const min=Math.min(...values, -0.01), max=0;
    const w=800,h=250,left=48,right=16,top=18,bottom=42;
    const plotW=w-left-right,plotH=h-top-bottom;
    const x=i=>left+i*plotW/Math.max(values.length-1,1);
    const y=v=>top+(max-v)*plotH/Math.max(max-min,1e-12);
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox',`0 0 ${w} ${h}`);svg.setAttribute('class','fr-dd');

    const yTicks=[0,min/2,min];
    yTicks.forEach(tick=>{
      const gy=y(tick);
      const grid=document.createElementNS(ns,'line');
      grid.setAttribute('x1',left);grid.setAttribute('x2',w-right);grid.setAttribute('y1',gy);grid.setAttribute('y2',gy);grid.setAttribute('stroke','#e2e8f0');svg.appendChild(grid);
      svg.appendChild(svgText(ns,left-6,gy+4,`${tick.toFixed(1)}%`,{'font-size':'10','fill':'#64748b','text-anchor':'end'}));
    });

    const dateTicks=[0,Math.floor((values.length-1)/2),values.length-1];
    dateTicks.forEach(i=>{
      svg.appendChild(svgText(ns,x(i),h-22,data.dates[i]||'',{'font-size':'10','fill':'#64748b','text-anchor':i===0?'start':i===values.length-1?'end':'middle'}));
    });
    svg.appendChild(svgText(ns,left,10,'낙폭 (%)',{'font-size':'10','fill':'#64748b'}));
    svg.appendChild(svgText(ns,left+plotW/2,h-6,'기간',{'font-size':'10','fill':'#64748b','text-anchor':'middle'}));

    const line=document.createElementNS(ns,'polyline');
    line.setAttribute('points',values.map((v,i)=>`${x(i)},${y(v)}`).join(' '));line.setAttribute('fill','none');line.setAttribute('stroke','#dc2626');line.setAttribute('stroke-width','2');svg.appendChild(line);

    const minIndex=values.indexOf(Math.min(...values));
    const dot=document.createElementNS(ns,'circle');
    dot.setAttribute('cx',x(minIndex));dot.setAttribute('cy',y(values[minIndex]));dot.setAttribute('r','4');dot.setAttribute('fill','#dc2626');svg.appendChild(dot);

    slot.innerHTML='';slot.appendChild(svg);
    if(meta) meta.textContent=`MDD ${fmt(metrics.maximum_drawdown_pct[index],'pct')} · TUW ${fmt(metrics.tuw_pct[index],'pct')} · Pain Index ${fmt(metrics.pain_index_pct[index],'pct')} · 최장 미회복 ${fmt(metrics.max_underwater_months[index],'months')}`;
  };

  const renderWeights = index => {
    const slot=document.getElementById('fr-weight-table'); if(!slot) return;
    const rows=data.symbols.map((symbol,i)=>[symbol,Number(data.weights_pct[index][i]||0)]).sort((a,b)=>b[1]-a[1]);
    slot.innerHTML=`<table class="fr-weight-table"><thead><tr><th>자산</th><th>비중</th></tr></thead><tbody>${rows.map(row=>`<tr><td>${row[0]}</td><td>${row[1].toFixed(2)}%</td></tr>`).join('')}</tbody></table>`;
  };

  const render = () => {
    const grid=document.getElementById('fr-metric-grid'); if(!grid) return;
    grid.innerHTML=''; configs.forEach(config=>grid.appendChild(renderMetricCard(config,selected)));
    const point=points[selected];
    const title=document.getElementById('fr-selected-title');
    if(title) title.textContent=`Frontier Point ${point}${point===Number(data.default_point)?' · Maximum Sharpe':''}`;
    const meta=document.getElementById('fr-selected-meta');
    if(meta) meta.textContent=`기대수익률 ${fmt(metrics.expected_return_pct[selected],'pct')} · 연환산 변동성 ${fmt(metrics.volatility_pct[selected],'pct')} · ${data.segments[selected]||''}`;
    renderWeights(selected); renderDrawdown(selected);
  };

  const select = index => {
    selected=Math.min(points.length-1,Math.max(0,index));
    history.replaceState(null,'',`${location.pathname}${location.search}#frontier-point=${points[selected]}`);
    render();
  };

  render();
})();
</script>
'''
    block = _START + "\n" + template.replace("__PAYLOAD__", payload_json) + "\n" + _END

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

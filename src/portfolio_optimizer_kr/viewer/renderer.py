from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .builder import build_report_model
from .report_model import ReportModel

_REPORT_DATA_TOKEN = "__REPORT_DATA_JSON__"

_VISUAL_IDENTITY_SCRIPT = r"""
<script id="report-legend-identity">
(() => {
  const data = window.PORTFOLIO_REPORT_DATA || {};
  const BLUE = '#2563eb';
  const PURPLE = '#7c3aed';
  const GRAY = '#64748b';
  const ORANGE = '#f97316';
  const GREEN = '#22c55e';
  const RED = '#e11d48';
  const TEAL = '#0891b2';
  const GOLD = '#ca8a04';
  const INDIGO = '#4f46e5';
  const ASSET_PALETTE = [BLUE, ORANGE, GREEN, RED, PURPLE, TEAL, GOLD, INDIGO];
  const NS = 'h' + 'ttp://www.w3.org/2000/svg';

  const paintLegend = (legend, colorList) => {
    if (!legend) return;
    legend.querySelectorAll('span').forEach((span, index) => {
      const color = colorList[index];
      if (color) span.style.setProperty('--color', color);
    });
  };

  const paintSectionLegends = (sectionId, colorList) => {
    document.querySelectorAll(`#${sectionId} .legend`).forEach(
      legend => paintLegend(legend, colorList),
    );
  };

  // Keep legacy identity guarantees. Enhanced renderers below replace the
  // affected DOM after these locks have been applied.
  paintSectionLegends('annual-returns', [BLUE, PURPLE, GRAY]);
  paintSectionLegends('annualized-active-return', [BLUE, PURPLE]);
  paintSectionLegends('rolling-active-return', [BLUE, ORANGE]);
  paintSectionLegends('up-down-market', [BLUE, RED]);
  paintSectionLegends('annual-asset-returns', [BLUE]);

  const frontierAssets = new Set(
    (data.frontier_assets || []).map(asset => String(asset.symbol)),
  );
  document.querySelectorAll('#efficient-frontier .legend span').forEach(span => {
    const label = (span.textContent || '').trim();
    const color = label === 'Efficient Frontier'
      ? BLUE
      : frontierAssets.has(label)
        ? GRAY
        : RED;
    span.style.setProperty('--color', color);
  });

  const style = document.createElement('style');
  style.textContent = `
    .allocation-layout{display:grid;grid-template-columns:minmax(240px,320px) 1fr;gap:22px;align-items:center}
    .allocation-donut{width:190px;height:190px;border-radius:50%;margin:8px auto;position:relative}
    .allocation-donut::after{content:'';position:absolute;inset:45px;border-radius:50%;background:#fff}
    .allocation-key{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:5px 10px;font-size:12px;margin-top:10px}
    .allocation-key span::before{content:'';display:inline-block;width:9px;height:9px;background:var(--color);margin-right:5px;border-radius:2px}
    .golden-chart svg{height:300px}
    .golden-panel{margin-top:12px}
    .golden-panel svg{width:100%;height:280px;display:block}
    .axis-label{fill:#334155;font-size:11px}
    .tick-label{fill:#64748b;font-size:10px}
    .grid-line{stroke:#e5eaf2;stroke-width:1}
    .axis-line{stroke:#94a3b8;stroke-width:1}
    .point-label{fill:#475569;font-size:10px}
    @media (max-width:760px){.allocation-layout{grid-template-columns:1fr}.allocation-donut{width:160px;height:160px}}
  `;
  document.head.appendChild(style);

  const finite = value => value !== null && value !== undefined && Number.isFinite(Number(value));
  const number = value => finite(value) ? Number(value) : null;
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;',
  }[c]));
  const pct = value => finite(value) ? `${Number(value).toFixed(2)}%` : 'N/A';
  const money = value => finite(value)
    ? Number(value).toLocaleString(undefined,{style:'currency',currency:'USD',maximumFractionDigits:0})
    : 'N/A';
  const section = id => document.querySelector(`#${id}`);
  const chartRoot = id => section(id)?.querySelector('.chart');
  const removeLegends = id => section(id)?.querySelectorAll('.legend').forEach(node => node.remove());

  const assetRows = data.tables?.optimization_results || [];
  const assetOrder = assetRows.map(row => String(row.ticker));
  const assetColors = new Map(assetOrder.map((ticker, index) => [
    ticker,
    ASSET_PALETTE[index % ASSET_PALETTE.length],
  ]));
  const assetColor = ticker => assetColors.get(String(ticker)) || ASSET_PALETTE[assetColors.size % ASSET_PALETTE.length];

  const tip = document.querySelector('.tooltip');
  const showTip = (event, html) => {
    if (!tip) return;
    tip.innerHTML = html;
    tip.style.display = 'block';
    tip.style.left = `${event.clientX + 14}px`;
    tip.style.top = `${event.clientY + 14}px`;
  };
  const hideTip = () => { if (tip) tip.style.display = 'none'; };

  const svgEl = (tag, attrs={}, text='') => {
    const el = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, String(value)));
    if (text !== '') el.textContent = String(text);
    return el;
  };

  const addLegend = (id, entries) => {
    const root = chartRoot(id);
    if (!root || !entries.length) return;
    removeLegends(id);
    const legend = document.createElement('div');
    legend.className = 'legend';
    legend.innerHTML = entries.map(entry =>
      `<span style="--color:${entry.color}">${esc(entry.label)}</span>`
    ).join('');
    root.before(legend);
  };

  const linearTicks = (min, max, count=5) => {
    if (!Number.isFinite(min) || !Number.isFinite(max)) return [];
    if (min === max) return [min];
    return Array.from({length:count}, (_, index) => min + (max - min) * index / (count - 1));
  };

  const addCartesianFrame = (svg, {
    width, height, left, right, top, bottom,
    xTicks=[], yTicks=[], xScale, yScale,
    xFormat=value=>String(value), yFormat=value=>String(value),
    xTitle='', yTitle='',
  }) => {
    const x0 = left;
    const x1 = width - right;
    const y0 = height - bottom;
    const y1 = top;

    yTicks.forEach(value => {
      const y = yScale(value);
      svg.appendChild(svgEl('line',{x1:x0,y1:y,x2:x1,y2:y,class:'grid-line'}));
      svg.appendChild(svgEl('text',{x:x0-7,y:y+3,'text-anchor':'end',class:'tick-label'},yFormat(value)));
    });
    xTicks.forEach(({value,label}) => {
      const x = xScale(value);
      svg.appendChild(svgEl('line',{x1:x,y1:y1,x2:x,y2:y0,class:'grid-line'}));
      svg.appendChild(svgEl('text',{x,y:y0+16,'text-anchor':'middle',class:'tick-label'},label ?? xFormat(value)));
    });

    svg.appendChild(svgEl('line',{x1:x0,y1:y0,x2:x1,y2:y0,class:'axis-line'}));
    svg.appendChild(svgEl('line',{x1:x0,y1:y1,x2:x0,y2:y0,class:'axis-line'}));
    if (xTitle) svg.appendChild(svgEl('text',{
      x:(x0+x1)/2,y:height-5,'text-anchor':'middle',class:'axis-label',
    },xTitle));
    if (yTitle) svg.appendChild(svgEl('text',{
      x:14,y:(y0+y1)/2,transform:`rotate(-90 14 ${(y0+y1)/2})`,
      'text-anchor':'middle',class:'axis-label',
    },yTitle));
  };

  const renderAllocationSummary = (id, weightKey) => {
    const target = section(id);
    const slot = target?.querySelector('.table-slot');
    if (!target || !slot) return;

    const rows = assetRows
      .filter(row => finite(row[weightKey]) && Number(row[weightKey]) > 0.00005)
      .map(row => ({
        ticker:String(row.ticker),
        name:row.name || '',
        allocation:Number(row[weightKey]),
        min:finite(row.min_weight_pct) ? Number(row.min_weight_pct) : null,
        max:finite(row.max_weight_pct) ? Number(row.max_weight_pct) : null,
      }));
    if (!rows.length) return;

    const stops = [];
    let cumulative = 0;
    rows.forEach(row => {
      const start = cumulative;
      cumulative += row.allocation;
      stops.push(`${assetColor(row.ticker)} ${start}% ${cumulative}%`);
    });

    const old = target.querySelector('.allocation-layout');
    if (old) old.remove();
    slot.style.display = 'none';

    const layout = document.createElement('div');
    layout.className = 'allocation-layout';
    layout.innerHTML = `
      <div>
        <div class="allocation-donut" style="background:conic-gradient(${stops.join(',')})"></div>
        <div class="allocation-key">
          ${rows.map(row =>
            `<span style="--color:${assetColor(row.ticker)}">${esc(row.ticker)} ${pct(row.allocation)}</span>`
          ).join('')}
        </div>
      </div>
      <div class="table-slot">
        <table>
          <thead><tr><th>Ticker</th><th>Asset</th><th>Allocation</th><th>Min</th><th>Max</th></tr></thead>
          <tbody>
            ${rows.map(row => `
              <tr>
                <td>${esc(row.ticker)}</td>
                <td>${esc(row.name)}</td>
                <td>${pct(row.allocation)}</td>
                <td>${pct(row.min)}</td>
                <td>${pct(row.max)}</td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
    slot.after(layout);
  };

  const renderGroupedBars = ({
    id, rows, series, labelKey='year', xTitle='Year', yTitle='Return %',
  }) => {
    const root = chartRoot(id);
    if (!root || !rows?.length || !series?.length) return;
    root.classList.add('golden-chart');
    root.innerHTML = '';

    const values = series.flatMap(item =>
      rows.map(row => number(row[item.key])).filter(value => value !== null)
    );
    if (!values.length) return;
    let min = Math.min(0, ...values);
    let max = Math.max(0, ...values);
    if (min === max) { min -= 1; max += 1; }

    const width=1000,height=300,left=58,right=24,top=16,bottom=48;
    const plotWidth = width-left-right;
    const plotHeight = height-top-bottom;
    const yScale = value => top + (max-value) * plotHeight / (max-min);
    const groupWidth = plotWidth / Math.max(rows.length,1);
    const barWidth = Math.max(2, Math.min(18, groupWidth / (series.length + 0.8)));
    const xCenter = index => left + groupWidth * (index + 0.5);
    const svg = svgEl('svg',{viewBox:`0 0 ${width} ${height}`});

    const step = Math.max(1, Math.ceil(rows.length / 10));
    const xTicks = rows
      .map((row,index)=>({row,index}))
      .filter(({index}) => index % step === 0 || index === rows.length-1)
      .map(({row,index}) => ({value:index,label:String(row[labelKey])}));
    const xTickScale = index => xCenter(index);

    addCartesianFrame(svg,{
      width,height,left,right,top,bottom,
      xTicks,
      yTicks:linearTicks(min,max,5),
      xScale:xTickScale,
      yScale,
      yFormat:value=>`${value.toFixed(0)}%`,
      xTitle,yTitle,
    });

    const zeroY = yScale(0);
    svg.appendChild(svgEl('line',{x1:left,y1:zeroY,x2:width-right,y2:zeroY,stroke:'#94a3b8','stroke-width':'1.2'}));

    rows.forEach((row,index) => {
      series.forEach((item,seriesIndex) => {
        const value = number(row[item.key]);
        if (value === null) return;
        const x = xCenter(index)
          - (series.length * barWidth) / 2
          + seriesIndex * barWidth;
        const y = value >= 0 ? yScale(value) : zeroY;
        const rect = svgEl('rect',{
          x,y,width:barWidth*0.82,height:Math.max(1,Math.abs(yScale(value)-zeroY)),
          fill:item.color,
        });
        rect.addEventListener('mousemove',event => showTip(
          event,
          `<b>${esc(row[labelKey])} · ${esc(item.label)}</b><br>${yTitle}: ${pct(value)}`
        ));
        rect.addEventListener('mouseleave',hideTip);
        svg.appendChild(rect);
      });
    });

    root.appendChild(svg);
    addLegend(id, series.map(item=>({label:item.label,color:item.color})));
  };

  const renderPortfolioGrowth = () => {
    const id = 'portfolio-growth';
    const root = chartRoot(id);
    const rows = (data.portfolio_growth || []).filter(row => row.date);
    if (!root || !rows.length) return;
    root.classList.add('golden-chart');
    root.innerHTML = '';

    const series = [
      {key:'provided_balance',label:'Provided',color:BLUE},
      {key:'optimized_balance',label:'Optimized',color:PURPLE},
      {key:'benchmark_balance',label:'Benchmark',color:GRAY},
    ].filter(item => rows.some(row => finite(row[item.key])));
    const shaped = rows.map(row => ({
      ...row,
      time:new Date(`${row.date}T00:00:00`).getTime(),
      provided_balance:finite(row.provided_balance)?Number(row.provided_balance)*10000:null,
      optimized_balance:finite(row.optimized_balance)?Number(row.optimized_balance)*10000:null,
      benchmark_balance:finite(row.benchmark_balance)?Number(row.benchmark_balance)*10000:null,
    }));
    const values = series.flatMap(item =>
      shaped.map(row=>number(row[item.key])).filter(value=>value!==null)
    );
    const times = shaped.map(row=>row.time).filter(Number.isFinite);
    if (!values.length || !times.length) return;

    let min=Math.min(...values),max=Math.max(...values);
    const pad=Math.max((max-min)*0.04,100);
    min-=pad;max+=pad;
    const minTime=Math.min(...times),maxTime=Math.max(...times);
    const width=1000,height=300,left=66,right=24,top=16,bottom=48;
    const xScale=value=>left+(value-minTime)*(width-left-right)/(maxTime-minTime||1);
    const yScale=value=>top+(max-value)*(height-top-bottom)/(max-min||1);
    const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`});

    const years=[...new Set(shaped.map(row=>new Date(row.time).getFullYear()))];
    const yearStep=Math.max(1,Math.ceil(years.length/10));
    const xTicks=years
      .filter((_,index)=>index%yearStep===0 || index===years.length-1)
      .map(year=>({value:new Date(`${year}-01-01T00:00:00`).getTime(),label:String(year)}))
      .filter(tick=>tick.value>=minTime && tick.value<=maxTime);

    addCartesianFrame(svg,{
      width,height,left,right,top,bottom,
      xTicks,yTicks:linearTicks(min,max,5),xScale,yScale,
      yFormat:value=>money(value),xTitle:'Year',yTitle:'Balance ($)',
    });

    series.forEach(item => {
      let segment=[];
      const flush=()=>{
        if(segment.length>1) svg.appendChild(svgEl('polyline',{
          points:segment.join(' '),fill:'none',stroke:item.color,'stroke-width':2.4,
        }));
        segment=[];
      };
      shaped.forEach(row=>{
        const value=number(row[item.key]);
        if(value===null){flush();return;}
        segment.push(`${xScale(row.time)},${yScale(value)}`);
      });
      flush();
    });

    shaped.forEach(row=>{
      const hit=svgEl('circle',{cx:xScale(row.time),cy:yScale(
        series.map(item=>number(row[item.key])).find(value=>value!==null) ?? min
      ),r:7,fill:'transparent'});
      hit.addEventListener('mousemove',event=>showTip(event,
        `<b>${esc(row.date)}</b><br>`+
        series.map(item=>`${esc(item.label)}: ${money(row[item.key])}`).join('<br>')
      ));
      hit.addEventListener('mouseleave',hideTip);
      svg.appendChild(hit);
    });

    root.appendChild(svg);
    addLegend(id,series.map(item=>({label:item.label,color:item.color})));
  };

  const renderAnnualReturns = () => renderGroupedBars({
    id:'annual-returns',
    rows:data.annual_returns || [],
    series:[
      {key:'provided_return_pct',label:'Provided',color:BLUE},
      {key:'optimized_return_pct',label:'Optimized',color:PURPLE},
      {key:'benchmark_return_pct',label:'Benchmark',color:GRAY},
    ],
    labelKey:'year',
    xTitle:'Year',
    yTitle:'Annual Return %',
  });

  const renderAnnualizedActiveReturn = () => renderGroupedBars({
    id:'annualized-active-return',
    rows:data.annualized_active_returns || [],
    series:[
      {key:'provided_active_return_pct',label:'Provided',color:BLUE},
      {key:'optimized_active_return_pct',label:'Optimized',color:PURPLE},
    ],
    labelKey:'year',
    xTitle:'Year',
    yTitle:'Active Return %',
  });

  const renderAnnualAssetReturns = () => {
    const rows = (data.annual_asset_returns || []).map(point => ({
      year:point.year,
      ...(point.returns_pct || {}),
    }));
    const tickers = [...new Set(
      (data.annual_asset_returns || []).flatMap(point => Object.keys(point.returns_pct || {}))
    )];
    renderGroupedBars({
      id:'annual-asset-returns',
      rows,
      series:tickers.map(ticker=>({key:ticker,label:ticker,color:assetColor(ticker)})),
      labelKey:'year',
      xTitle:'Year',
      yTitle:'Asset Return %',
    });
  };

  const renderEfficientFrontier = () => {
    const id='efficient-frontier';
    const root=chartRoot(id);
    const frontier=(data.efficient_frontier || [])
      .filter(row=>finite(row.volatility_pct)&&finite(row.expected_return_pct))
      .map(row=>({...row,x:Number(row.volatility_pct),y:Number(row.expected_return_pct)}))
      .sort((a,b)=>a.x-b.x);
    const assets=(data.frontier_assets || [])
      .filter(row=>finite(row.standard_deviation_pct)&&finite(row.expected_return_pct))
      .map(row=>({...row,x:Number(row.standard_deviation_pct),y:Number(row.expected_return_pct)}));
    const landmarks=(data.frontier_landmarks || [])
      .filter(row=>finite(row.volatility_pct)&&finite(row.expected_return_pct))
      .map(row=>({...row,x:Number(row.volatility_pct),y:Number(row.expected_return_pct)}));
    const all=[...frontier,...assets,...landmarks];
    if(!root || !all.length) return;
    root.classList.add('golden-chart');
    root.innerHTML='';

    let minX=Math.min(...all.map(row=>row.x)),maxX=Math.max(...all.map(row=>row.x));
    let minY=Math.min(...all.map(row=>row.y)),maxY=Math.max(...all.map(row=>row.y));
    const xPad=Math.max((maxX-minX)*0.03,0.2),yPad=Math.max((maxY-minY)*0.05,0.2);
    minX-=xPad;maxX+=xPad;minY-=yPad;maxY+=yPad;
    const width=1000,height=320,left=64,right=24,top=16,bottom=50;
    const xScale=value=>left+(value-minX)*(width-left-right)/(maxX-minX||1);
    const yScale=value=>top+(maxY-value)*(height-top-bottom)/(maxY-minY||1);
    const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`});

    addCartesianFrame(svg,{
      width,height,left,right,top,bottom,
      xTicks:linearTicks(minX,maxX,5).map(value=>({value,label:`${value.toFixed(1)}%`})),
      yTicks:linearTicks(minY,maxY,5),
      xScale,yScale,yFormat:value=>`${value.toFixed(1)}%`,
      xTitle:'Standard Deviation %',yTitle:'Expected Return %',
    });

    if(frontier.length>1) svg.appendChild(svgEl('polyline',{
      points:frontier.map(row=>`${xScale(row.x)},${yScale(row.y)}`).join(' '),
      fill:'none',stroke:BLUE,'stroke-width':2.8,
    }));

    assets.forEach(row=>{
      const circle=svgEl('circle',{cx:xScale(row.x),cy:yScale(row.y),r:4.5,fill:GRAY});
      circle.addEventListener('mousemove',event=>showTip(event,
        `<b>${esc(row.symbol)}</b><br>Std Dev: ${pct(row.x)}<br>Expected Return: ${pct(row.y)}<br>Sharpe: ${finite(row.sharpe_ratio)?Number(row.sharpe_ratio).toFixed(2):'N/A'}`
      ));
      circle.addEventListener('mouseleave',hideTip);
      svg.appendChild(circle);
      svg.appendChild(svgEl('text',{
        x:xScale(row.x)+7,y:yScale(row.y)-6,class:'point-label',
      },row.symbol));
    });

    landmarks.forEach(row=>{
      const circle=svgEl('circle',{cx:xScale(row.x),cy:yScale(row.y),r:5.5,fill:RED});
      circle.addEventListener('mousemove',event=>showTip(event,
        `<b>${esc(row.label || row.kind)}</b><br>Std Dev: ${pct(row.x)}<br>Expected Return: ${pct(row.y)}`
      ));
      circle.addEventListener('mouseleave',hideTip);
      svg.appendChild(circle);
      svg.appendChild(svgEl('text',{
        x:xScale(row.x)+7,y:yScale(row.y)+12,class:'point-label',
      },row.label || row.kind));
    });

    root.appendChild(svg);
    addLegend(id,[
      {label:'Efficient Frontier',color:BLUE},
      {label:'Individual Assets',color:GRAY},
      {label:'Portfolio / Benchmark Landmarks',color:RED},
    ]);
  };

  const renderTransitionMap = () => {
    const id='frontier-transition';
    const root=chartRoot(id);
    const rows=(data.efficient_frontier || [])
      .filter(row=>finite(row.volatility_pct))
      .slice()
      .sort((a,b)=>Number(a.volatility_pct)-Number(b.volatility_pct));
    if(!root || !rows.length) return;
    root.classList.add('golden-chart');
    root.innerHTML='';

    const tickers=[...new Set(rows.flatMap(row=>Object.keys(row.weights_pct || {})))];
    const minX=Math.min(...rows.map(row=>Number(row.volatility_pct)));
    const maxX=Math.max(...rows.map(row=>Number(row.volatility_pct)));
    const width=1000,height=320,left=64,right=24,top=16,bottom=50;
    const xScale=value=>left+(value-minX)*(width-left-right)/(maxX-minX||1);
    const yScale=value=>top+(100-value)*(height-top-bottom)/100;
    const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`});

    addCartesianFrame(svg,{
      width,height,left,right,top,bottom,
      xTicks:linearTicks(minX,maxX,5).map(value=>({value,label:`${value.toFixed(1)}%`})),
      yTicks:[0,25,50,75,100],
      xScale,yScale,yFormat:value=>`${value.toFixed(0)}%`,
      xTitle:'Standard Deviation %',yTitle:'Allocation %',
    });

    let base=rows.map(()=>0);
    tickers.forEach(ticker=>{
      const topValues=rows.map((row,index)=>base[index]+(finite(row.weights_pct?.[ticker])?Number(row.weights_pct[ticker]):0));
      const points=[
        ...rows.map((row,index)=>`${xScale(Number(row.volatility_pct))},${yScale(topValues[index])}`),
        ...rows.slice().reverse().map((row,reverseIndex)=>{
          const index=rows.length-1-reverseIndex;
          return `${xScale(Number(row.volatility_pct))},${yScale(base[index])}`;
        }),
      ].join(' ');
      const area=svgEl('polygon',{
        points,fill:assetColor(ticker),'fill-opacity':0.68,stroke:'none',
      });
      area.addEventListener('mousemove',event=>{
        const rect=svg.getBoundingClientRect();
        const localX=(event.clientX-rect.left)*width/rect.width;
        const ratio=Math.min(1,Math.max(0,(localX-left)/(width-left-right)));
        const volatility=minX+ratio*(maxX-minX);
        const row=rows.reduce((best,item)=>
          Math.abs(Number(item.volatility_pct)-volatility)<Math.abs(Number(best.volatility_pct)-volatility)
            ? item : best,
          rows[0],
        );
        showTip(event,
          `<b>Std Dev: ${pct(row.volatility_pct)}</b><br>`+
          tickers.map(name=>`${esc(name)}: ${pct(row.weights_pct?.[name])}`).join('<br>')
        );
      });
      area.addEventListener('mouseleave',hideTip);
      svg.appendChild(area);
      base=topValues;
    });

    // Redraw axes/tick text over the translucent areas.
    addCartesianFrame(svg,{
      width,height,left,right,top,bottom,
      xTicks:linearTicks(minX,maxX,5).map(value=>({value,label:`${value.toFixed(1)}%`})),
      yTicks:[0,25,50,75,100],
      xScale,yScale,yFormat:value=>`${value.toFixed(0)}%`,
      xTitle:'Standard Deviation %',yTitle:'Allocation %',
    });

    root.appendChild(svg);
    addLegend(id,tickers.map(ticker=>({label:ticker,color:assetColor(ticker)})));
  };

  const renderUpDown = () => {
    const id='up-down-market';
    const host=chartRoot(id);
    if(!host) return;
    const panels=[
      ['Provided Portfolio',data.up_down_scatter_provided || []],
      ['Optimized Portfolio',data.up_down_scatter_optimized || []],
    ];
    host.innerHTML='';
    removeLegends(id);

    panels.forEach(([label,rows])=>{
      const valid=rows.filter(row=>finite(row.benchmark_return_pct)&&finite(row.portfolio_return_pct));
      const holder=document.createElement('div');
      holder.className='golden-panel';
      holder.innerHTML=`<h3>${esc(label)}</h3>`;
      host.appendChild(holder);
      if(!valid.length) return;

      const values=valid.flatMap(row=>[
        Number(row.benchmark_return_pct),Number(row.portfolio_return_pct),
      ]);
      let min=Math.min(...values),max=Math.max(...values);
      const pad=Math.max((max-min)*0.05,0.5);min-=pad;max+=pad;
      const width=1000,height=280,left=60,right=24,top=16,bottom=48;
      const xScale=value=>left+(value-min)*(width-left-right)/(max-min||1);
      const yScale=value=>top+(max-value)*(height-top-bottom)/(max-min||1);
      const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`});
      const ticks=linearTicks(min,max,5);

      addCartesianFrame(svg,{
        width,height,left,right,top,bottom,
        xTicks:ticks.map(value=>({value,label:`${value.toFixed(1)}%`})),
        yTicks:ticks,xScale,yScale,yFormat:value=>`${value.toFixed(1)}%`,
        xTitle:'Benchmark Monthly Return %',yTitle:'Portfolio Monthly Return %',
      });
      svg.appendChild(svgEl('line',{
        x1:xScale(min),y1:yScale(min),x2:xScale(max),y2:yScale(max),
        stroke:'#94a3b8','stroke-dasharray':'5 4',
      }));
      valid.forEach(row=>{
        const color=row.market_type==='down'?RED:BLUE;
        const circle=svgEl('circle',{
          cx:xScale(Number(row.benchmark_return_pct)),
          cy:yScale(Number(row.portfolio_return_pct)),
          r:4,fill:color,'fill-opacity':0.72,
        });
        circle.addEventListener('mousemove',event=>showTip(event,
          `<b>${esc(label)}</b><br>Date: ${esc(row.date)}<br>`+
          `Benchmark: ${pct(row.benchmark_return_pct)}<br>`+
          `Portfolio: ${pct(row.portfolio_return_pct)}<br>`+
          `Active: ${pct(row.active_return_pct)}`
        ));
        circle.addEventListener('mouseleave',hideTip);
        svg.appendChild(circle);
      });
      holder.appendChild(svg);
    });

    const firstPanel=host.querySelector('.golden-panel');
    if(firstPanel){
      const legend=document.createElement('div');
      legend.className='legend';
      legend.innerHTML=`
        <span style="--color:${BLUE}">Up benchmark month</span>
        <span style="--color:${RED}">Down benchmark month</span>`;
      firstPanel.before(legend);
    }

    const slot=section(id)?.querySelector('.table-slot');
    const rows=data.tables?.up_down_market_performance || [];
    if(slot && rows.length){
      const labelMap={
        portfolio:'Portfolio',
        market_type:'Market',
        occurrences:'Months',
        above_benchmark_count:'Above Benchmark',
        below_benchmark_count:'Below Benchmark',
        total_count:'Total',
        pct_above_benchmark:'% Above Benchmark',
        above_active_return_pct:'Avg Active Return When Above',
        below_active_return_pct:'Avg Active Return When Below',
        overall_active_return_pct:'Overall Avg Active Return',
      };
      const cols=Object.keys(labelMap).filter(key=>rows.some(row=>row[key]!==undefined));
      slot.innerHTML=`<table><thead><tr>${
        cols.map(key=>`<th>${esc(labelMap[key])}</th>`).join('')
      }</tr></thead><tbody>${
        rows.map(row=>`<tr>${
          cols.map(key=>{
            const value=row[key];
            const isPct=key.includes('pct') || key.includes('return');
            return `<td>${isPct && finite(value) ? pct(value) : esc(value ?? '')}</td>`;
          }).join('')
        }</tr>`).join('')
      }</tbody></table>`;
    }
  };

  renderAllocationSummary('provided-portfolio','provided_weight_pct');
  renderAllocationSummary('optimized-portfolio','optimized_weight_pct');
  renderPortfolioGrowth();
  renderAnnualReturns();
  renderAnnualizedActiveReturn();
  renderAnnualAssetReturns();
  renderEfficientFrontier();
  renderTransitionMap();
  renderUpDown();
})();
</script>
""".strip()


def _json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def default_template_path() -> Path:
    return Path(__file__).resolve().parents[3] / "site" / "report-template.html"


def _inject_visual_identity_script(html: str) -> str:
    closing_body = "</body>"
    if closing_body not in html:
        raise ValueError("report template missing closing body tag")
    return html.replace(
        closing_body,
        f"  {_VISUAL_IDENTITY_SCRIPT}\n{closing_body}",
        1,
    )


def render_report(
    model: ReportModel,
    output_path: str | Path,
    *,
    template_path: str | Path | None = None,
) -> Path:
    template_file = Path(template_path) if template_path is not None else default_template_path()
    template = template_file.read_text(encoding="utf-8")
    if _REPORT_DATA_TOKEN not in template:
        raise ValueError(f"report template missing token: {_REPORT_DATA_TOKEN}")

    payload = json.dumps(
        _json_safe(model.to_dict()),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    html = template.replace(_REPORT_DATA_TOKEN, payload)
    html = _inject_visual_identity_script(html)

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target


def generate_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> Path:
    directory = Path(run_dir)
    model = build_report_model(directory)
    target = Path(output_path) if output_path is not None else directory / "report.html"
    return render_report(model, target, template_path=template_path)

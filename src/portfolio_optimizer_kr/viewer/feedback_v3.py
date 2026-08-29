from __future__ import annotations

from pathlib import Path

from .renderer import generate_report as _base_generate_report
from .renderer import render_report as _base_render_report
from .report_model import ReportModel


_USER_FEEDBACK_V3_SCRIPT = r"""
<script id="report-user-feedback-v3">
(() => {
  const run = () => {
    const data = window.PORTFOLIO_REPORT_DATA || {};
    const NS = 'h' + 'ttp://www.w3.org/2000/svg';
    const BLUE = '#2563eb';
    const PURPLE = '#7c3aed';
    const GRAY = '#64748b';
    const RED = '#e11d48';
    const MINT = '#50d8b0';
    const PALETTE = [BLUE, '#f97316', '#22c55e', RED, PURPLE, '#0891b2', '#ca8a04', '#4f46e5'];

    const finite = value => value !== null && value !== undefined && Number.isFinite(Number(value));
    const number = value => finite(value) ? Number(value) : null;
    const pct = value => finite(value) ? `${Number(value).toFixed(2)}%` : 'N/A';
    const ratio = value => finite(value) ? Number(value).toFixed(2) : 'N/A';
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;',
    }[c]));
    const section = id => document.querySelector(`#${id}`);
    const chart = id => section(id)?.querySelector('.chart');
    const tableSlot = id => section(id)?.querySelector('.table-slot');
    const records = name => data.tables?.[name] || [];
    const tip = document.querySelector('.tooltip') || (() => {
      const el = document.createElement('div');
      el.className = 'tooltip';
      document.body.appendChild(el);
      return el;
    })();
    const showTip = (event, html) => {
      tip.innerHTML = html;
      tip.style.display = 'block';
      tip.style.left = `${event.clientX + 14}px`;
      tip.style.top = `${event.clientY + 14}px`;
    };
    const hideTip = () => { tip.style.display = 'none'; };
    const svgEl = (tag, attrs={}, text='') => {
      const el = document.createElementNS(NS, tag);
      Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, String(value)));
      if (text !== '') el.textContent = String(text);
      return el;
    };

    const optRows = records('optimization_results');
    const optByTicker = new Map(optRows.map(row => [String(row.ticker), row]));
    const assetOrder = optRows.map(row => String(row.ticker));
    const assetColors = new Map(assetOrder.map((ticker, index) => [ticker, PALETTE[index % PALETTE.length]]));
    const assetColor = ticker => assetColors.get(String(ticker)) || GRAY;
    const assetName = ticker => optByTicker.get(String(ticker))?.name || String(ticker);
    const optimizedLabel = data.objective_name || 'Optimized Portfolio';
    const benchmarkLabel = data.benchmark_name || data.benchmark_symbol || 'Benchmark';

    const style = document.createElement('style');
    style.id = 'report-user-feedback-v3-style';
    style.textContent = `
      .v3-axis{stroke:#94a3b8;stroke-width:1}.v3-grid{stroke:#e5eaf2;stroke-width:1}
      .v3-tick{fill:#64748b;font-size:10px}.v3-axis-label{fill:#334155;font-size:11px}
      .v3-point-label{fill:#475569;font-size:10px}.v3-bar-title{text-align:center;font-weight:600;margin:14px 0 2px}
      .v3-bar-subtitle{text-align:center;color:#475569;font-size:11px;margin-bottom:4px}
      .v3-chart-legend{display:flex;justify-content:center;gap:18px;flex-wrap:wrap;font-size:11px;margin:7px 0 0}
      .v3-chart-legend span::before{content:'';display:inline-block;width:10px;height:10px;background:var(--color);margin-right:5px;border-radius:50%}
      .v3-updown-panel{margin:12px 0 30px}.v3-updown-panel .table-slot{margin-bottom:8px}
      .v3-updown-panel svg{height:390px}.v3-frontier-hidden{margin-top:14px}
    `;
    document.head.appendChild(style);

    const niceStep = (span, target=12) => {
      if (!(span > 0)) return 1;
      const raw = span / Math.max(1, target);
      const power = 10 ** Math.floor(Math.log10(raw));
      const fraction = raw / power;
      const nice = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 2.5 ? 2.5 : fraction <= 5 ? 5 : 10;
      return nice * power;
    };
    const outwardDomain = (min, max, {lowerPad=0, upperPad=0, target=12}={}) => {
      const rawMin = min - lowerPad;
      const rawMax = max + upperPad;
      const step = niceStep(rawMax - rawMin, target);
      return {
        min: Math.floor(rawMin / step) * step,
        max: Math.ceil(rawMax / step) * step,
        step,
      };
    };
    const ticksFor = domain => {
      const ticks = [];
      for (let value=domain.min; value<=domain.max + domain.step*0.1 && ticks.length<30; value+=domain.step) {
        ticks.push(Math.abs(value) < 1e-10 ? 0 : Number(value.toFixed(10)));
      }
      return ticks;
    };
    const addFrame = (svg, {width,height,left,right,top,bottom,xDomain,yDomain,xScale,yScale,xTitle,yTitle}) => {
      ticksFor(yDomain).forEach(value => {
        const y = yScale(value);
        svg.appendChild(svgEl('line',{x1:left,y1:y,x2:width-right,y2:y,class:'v3-grid'}));
        svg.appendChild(svgEl('text',{x:left-7,y:y+3,'text-anchor':'end',class:'v3-tick'},`${value.toFixed(1)}%`));
      });
      ticksFor(xDomain).forEach(value => {
        const x = xScale(value);
        svg.appendChild(svgEl('line',{x1:x,y1:top,x2:x,y2:height-bottom,class:'v3-grid'}));
        svg.appendChild(svgEl('text',{x,y:height-bottom+17,'text-anchor':'middle',class:'v3-tick'},`${value.toFixed(1)}%`));
      });
      svg.appendChild(svgEl('line',{x1:left,y1:height-bottom,x2:width-right,y2:height-bottom,class:'v3-axis'}));
      svg.appendChild(svgEl('line',{x1:left,y1:top,x2:left,y2:height-bottom,class:'v3-axis'}));
      svg.appendChild(svgEl('text',{x:(left+width-right)/2,y:height-5,'text-anchor':'middle',class:'v3-axis-label'},xTitle));
      svg.appendChild(svgEl('text',{x:14,y:(top+height-bottom)/2,transform:`rotate(-90 14 ${(top+height-bottom)/2})`,'text-anchor':'middle',class:'v3-axis-label'},yTitle));
    };

    const renderTable = (id, rows, cols) => {
      const slot = tableSlot(id);
      if (!slot || !rows.length) return;
      slot.style.display = '';
      slot.innerHTML = `<table class="feedback-table"><thead><tr>${cols.map(col=>`<th>${esc(col.label)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${cols.map(col=>{
        const value = typeof col.value === 'function' ? col.value(row) : row[col.key];
        return `<td>${col.format ? col.format(value,row) : esc(value ?? '')}</td>`;
      }).join('')}</tr>`).join('')}</tbody></table>`;
    };

    // Regression fix: restore the specification-required Min/Max Weight columns.
    const frontierAssets = (data.frontier_assets || []).map(asset => {
      const limits = optByTicker.get(String(asset.symbol)) || {};
      return {
        ...asset,
        name: asset.name || assetName(asset.symbol),
        min_weight_pct: finite(asset.min_weight_pct) ? asset.min_weight_pct : limits.min_weight_pct,
        max_weight_pct: finite(asset.max_weight_pct) ? asset.max_weight_pct : limits.max_weight_pct,
      };
    });
    renderTable('efficient-frontier-assets', frontierAssets, [
      {key:'name',label:'Name'},
      {key:'symbol',label:'Ticker'},
      {key:'expected_return_pct',label:'Expected Return',format:pct},
      {key:'standard_deviation_pct',label:'Std Dev',format:pct},
      {key:'sharpe_ratio',label:'Sharpe Ratio',format:ratio},
      {key:'min_weight_pct',label:'Min Weight',format:pct},
      {key:'max_weight_pct',label:'Max Weight',format:pct},
    ]);

    // Frontier viewport is anchored on the curve, but deliberately leaves context around it.
    // Outsider classification is based on the final snapped display domain, never the raw curve extrema.
    const renderFrontier = () => {
      const root = chart('efficient-frontier');
      const points = (data.efficient_frontier || [])
        .filter(point => finite(point.volatility_pct) && finite(point.expected_return_pct))
        .slice()
        .sort((a,b) => Number(a.volatility_pct) - Number(b.volatility_pct));
      if (!root || !points.length) return;

      const curveX = points.map(point => Number(point.volatility_pct));
      const curveY = points.map(point => Number(point.expected_return_pct));
      const curveMinX = Math.min(...curveX), curveMaxX = Math.max(...curveX);
      const curveMinY = Math.min(...curveY), curveMaxY = Math.max(...curveY);
      const xSpan = curveMaxX - curveMinX;
      const ySpan = curveMaxY - curveMinY;
      const xDomain = outwardDomain(curveMinX, curveMaxX, {
        lowerPad: Math.max(xSpan * 0.10, 2.0),
        upperPad: Math.max(xSpan * 0.20, 4.0),
        target: 14,
      });
      const yDomain = outwardDomain(curveMinY, curveMaxY, {
        lowerPad: Math.max(ySpan * 0.25, 4.5),
        upperPad: Math.max(ySpan * 0.12, 2.0),
        target: 12,
      });

      const width=1000,height=360,left=68,right=28,top=18,bottom=54;
      const x = value => left + (value-xDomain.min) * (width-left-right) / (xDomain.max-xDomain.min || 1);
      const y = value => top + (yDomain.max-value) * (height-top-bottom) / (yDomain.max-yDomain.min || 1);
      const svg = svgEl('svg',{viewBox:`0 0 ${width} ${height}`});
      addFrame(svg,{width,height,left,right,top,bottom,xDomain,yDomain,xScale:x,yScale:y,xTitle:'Standard Deviation %',yTitle:'Expected Return %'});

      svg.appendChild(svgEl('polyline',{
        points:points.map(point=>`${x(Number(point.volatility_pct))},${y(Number(point.expected_return_pct))}`).join(' '),
        fill:'none',stroke:BLUE,'stroke-width':3,
      }));
      const curveHit = svgEl('polyline',{
        points:points.map(point=>`${x(Number(point.volatility_pct))},${y(Number(point.expected_return_pct))}`).join(' '),
        fill:'none',stroke:'transparent','stroke-width':20,'pointer-events':'stroke',
      });
      curveHit.addEventListener('mousemove', event => {
        const rect = svg.getBoundingClientRect();
        const localX = (event.clientX-rect.left) * width / rect.width;
        const volatility = xDomain.min + (localX-left) * (xDomain.max-xDomain.min) / (width-left-right);
        const nearest = points.reduce((best, point) =>
          Math.abs(Number(point.volatility_pct)-volatility) < Math.abs(Number(best.volatility_pct)-volatility) ? point : best,
          points[0],
        );
        showTip(event, `<b>Efficient Frontier</b><br>`+
          `Expected Return: ${pct(nearest.expected_return_pct)}<br>`+
          `Standard Deviation: ${pct(nearest.volatility_pct)}<br>`+
          `Sharpe Ratio: ${ratio(nearest.sharpe_ratio)}<br><br>`+
          Object.entries(nearest.weights_pct || {}).map(([ticker,weight])=>
            `${esc(assetName(ticker))} (${esc(ticker)}): ${pct(weight)}`
          ).join('<br>'));
      });
      curveHit.addEventListener('mouseleave', hideTip);
      svg.appendChild(curveHit);

      const inside = (vx, vy) => vx >= xDomain.min && vx <= xDomain.max && vy >= yDomain.min && vy <= yDomain.max;
      const hidden = [];
      const visibleLabels = [];
      frontierAssets.forEach((asset,index) => {
        const vx = number(asset.standard_deviation_pct), vy = number(asset.expected_return_pct);
        if (vx === null || vy === null) return;
        if (!inside(vx,vy)) { hidden.push(asset); return; }
        const circle = svgEl('circle',{cx:x(vx),cy:y(vy),r:5,fill:assetColor(asset.symbol)});
        circle.addEventListener('mousemove', event => showTip(event,
          `<b>${esc(asset.name)} (${esc(asset.symbol)})</b><br>`+
          `Expected Return: ${pct(vy)}<br>Std Dev: ${pct(vx)}<br>Sharpe Ratio: ${ratio(asset.sharpe_ratio)}`
        ));
        circle.addEventListener('mouseleave', hideTip);
        svg.appendChild(circle);
        const dx = index % 2 === 0 ? 7 : -7;
        const anchor = dx > 0 ? 'start' : 'end';
        const label = svgEl('text',{x:x(vx)+dx,y:y(vy)-6,'text-anchor':anchor,class:'v3-point-label'},asset.symbol);
        svg.appendChild(label);
        visibleLabels.push(label);
      });

      (data.frontier_landmarks || []).forEach((landmark,index) => {
        const vx = number(landmark.volatility_pct), vy = number(landmark.expected_return_pct);
        if (vx === null || vy === null || !inside(vx,vy)) return;
        const circle = svgEl('circle',{cx:x(vx),cy:y(vy),r:5.5,fill:RED});
        circle.addEventListener('mousemove', event => showTip(event,
          `<b>${esc(landmark.label)}</b><br>`+
          `Expected Return: ${pct(vy)}<br>Std Dev: ${pct(vx)}<br>Sharpe Ratio: ${ratio(landmark.sharpe_ratio)}`+
          (Object.keys(landmark.weights_pct || {}).length ? '<br><br>' + Object.entries(landmark.weights_pct).map(([ticker,weight])=>
            `${esc(assetName(ticker))} (${esc(ticker)}): ${pct(weight)}`
          ).join('<br>') : '')
        ));
        circle.addEventListener('mouseleave', hideTip);
        svg.appendChild(circle);
        const label = svgEl('text',{x:x(vx)+7,y:y(vy)+(index%2?13:-7),class:'v3-point-label'},landmark.label || landmark.kind || 'Portfolio');
        svg.appendChild(label);
        visibleLabels.push(label);
      });

      root.innerHTML = '';
      root.appendChild(svg);
      section('efficient-frontier')?.querySelectorAll('.legend').forEach(node=>node.remove());
      const legend = document.createElement('div');
      legend.className = 'legend';
      legend.innerHTML = `<span style="--color:${BLUE}">Efficient Frontier</span><span style="--color:${GRAY}">Assets</span><span style="--color:${RED}">Portfolio / Benchmark</span>`;
      root.before(legend);

      // Replace the prior renderer's raw-curve outsider table; it used a
      // pre-v3 classification and can contradict the snapped display domain.
      section('efficient-frontier')?.querySelectorAll('.frontier-hidden, .v3-frontier-hidden').forEach(node=>node.remove());
      if (hidden.length) {
        const wrap = document.createElement('div');
        wrap.className = 'v3-frontier-hidden table-slot';
        wrap.innerHTML = `<h3>Assets outside chart scale</h3><table class="feedback-table"><thead><tr><th>Name</th><th>Ticker</th><th>Std Dev</th><th>Expected Return</th><th>Sharpe Ratio</th></tr></thead><tbody>${hidden.map(asset=>
          `<tr><td>${esc(asset.name)}</td><td>${esc(asset.symbol)}</td><td>${pct(asset.standard_deviation_pct)}</td><td>${pct(asset.expected_return_pct)}</td><td>${ratio(asset.sharpe_ratio)}</td></tr>`
        ).join('')}</tbody></table>`;
        section('efficient-frontier')?.appendChild(wrap);
      }
    };
    renderFrontier();

    // Regression fix: render Annual Asset Returns as seven actual ticker series, not one generic return_pct series.
    const renderAnnualAssetReturns = () => {
      const root = chart('annual-asset-returns');
      const rows = (data.annual_asset_returns || []).map(point => ({year:point.year,...(point.returns_pct || {})}));
      const tickers = assetOrder.filter(ticker => rows.some(row => finite(row[ticker])));
      if (!root || !rows.length || !tickers.length) return;
      const values = rows.flatMap(row => tickers.map(ticker=>number(row[ticker])).filter(value=>value!==null));
      let min = Math.min(0,...values), max = Math.max(0,...values);
      if (min === max) { min -= 1; max += 1; }
      const yDomain = outwardDomain(min,max,{lowerPad:0,upperPad:0,target:8});
      if (yDomain.min > 0) yDomain.min = 0;
      if (yDomain.max < 0) yDomain.max = 0;
      const width=1000,height=330,left=58,right=24,top=16,bottom=48;
      const groupWidth=(width-left-right)/rows.length;
      const barWidth=Math.max(2,Math.min(12,groupWidth/(tickers.length+1)));
      const y=value=>top+(yDomain.max-value)*(height-top-bottom)/(yDomain.max-yDomain.min||1);
      const zero=y(0);
      const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`});
      ticksFor(yDomain).forEach(value=>{
        const yy=y(value);
        svg.appendChild(svgEl('line',{x1:left,y1:yy,x2:width-right,y2:yy,class:'v3-grid'}));
        svg.appendChild(svgEl('text',{x:left-7,y:yy+3,'text-anchor':'end',class:'v3-tick'},`${value.toFixed(0)}%`));
      });
      rows.forEach((row,index)=>{
        const center=left+groupWidth*(index+0.5);
        svg.appendChild(svgEl('text',{x:center,y:height-bottom+17,'text-anchor':'middle',class:'v3-tick'},row.year));
        tickers.forEach((ticker,seriesIndex)=>{
          const value=number(row[ticker]); if(value===null)return;
          const x=center-(tickers.length*barWidth)/2+seriesIndex*barWidth;
          svg.appendChild(svgEl('rect',{
            x,y:value>=0?y(value):zero,width:barWidth*.82,height:Math.max(1,Math.abs(y(value)-zero)),fill:assetColor(ticker),
          }));
        });
        const hit=svgEl('rect',{x:left+groupWidth*index,y:top,width:groupWidth,height:height-top-bottom,fill:'transparent','pointer-events':'all'});
        hit.addEventListener('mousemove',event=>showTip(event,`<b>${esc(row.year)}</b><br>${tickers.filter(t=>finite(row[t])).map(t=>
          `<span style="color:${assetColor(t)}">●</span> ${esc(assetName(t))} (${esc(t)}): ${pct(row[t])}`
        ).join('<br>')}`));
        hit.addEventListener('mouseleave',hideTip);
        svg.appendChild(hit);
      });
      svg.appendChild(svgEl('line',{x1:left,y1:zero,x2:width-right,y2:zero,class:'v3-axis'}));
      svg.appendChild(svgEl('line',{x1:left,y1:top,x2:left,y2:height-bottom,class:'v3-axis'}));
      svg.appendChild(svgEl('text',{x:(left+width-right)/2,y:height-5,'text-anchor':'middle',class:'v3-axis-label'},'Year'));
      svg.appendChild(svgEl('text',{x:14,y:(top+height-bottom)/2,transform:`rotate(-90 14 ${(top+height-bottom)/2})`,'text-anchor':'middle',class:'v3-axis-label'},'Annual Return %'));
      root.innerHTML=''; root.appendChild(svg);
      section('annual-asset-returns')?.querySelectorAll('.legend').forEach(node=>node.remove());
      const legend=document.createElement('div'); legend.className='legend';
      legend.innerHTML=tickers.map(ticker=>`<span style="--color:${assetColor(ticker)}">${esc(ticker)}</span>`).join('');
      root.before(legend);
    };
    renderAnnualAssetReturns();

    // PV Return vs. Benchmark: sort monthly observations by benchmark return, split into
    // 20 equal-frequency groups, and show the mean portfolio/benchmark return as paired bars.
    const returnVsBenchmarkBins = (rows, targetBins=20) => {
      const sorted = rows
        .filter(row => finite(row.benchmark_return_pct) && finite(row.portfolio_return_pct))
        .slice()
        .sort((a,b)=>Number(a.benchmark_return_pct)-Number(b.benchmark_return_pct));
      if (!sorted.length) return [];
      const binCount=Math.min(targetBins,sorted.length);
      const mean=(items,key)=>items.reduce((sum,item)=>sum+Number(item[key]),0)/items.length;
      return Array.from({length:binCount},(_,index)=>{
        const start=Math.floor(index*sorted.length/binCount);
        const end=Math.floor((index+1)*sorted.length/binCount);
        const members=sorted.slice(start,Math.max(start+1,end));
        return {
          benchmark_return_pct:mean(members,'benchmark_return_pct'),
          portfolio_return_pct:mean(members,'portfolio_return_pct'),
          observations:members.length,
        };
      });
    };

    const upDownSummaryRows = (perf,key) => {
      const rows=perf.filter(row=>row.portfolio===key);
      const up=rows.find(row=>row.market_type==='up');
      const down=rows.find(row=>row.market_type==='down');
      const total=(a,b)=>finite(a)&&finite(b)?Number(a)+Number(b):null;
      const weighted=(a,na,b,nb)=>finite(a)&&finite(b)&&finite(na)&&finite(nb)&&Number(na)+Number(nb)>0
        ? (Number(a)*Number(na)+Number(b)*Number(nb))/(Number(na)+Number(nb)) : null;
      return [
        up&&{label:'Up Market',...up},
        down&&{label:'Down Market',...down},
        up&&down&&{
          label:'Total',
          above_benchmark_count:total(up.above_benchmark_count,down.above_benchmark_count),
          below_benchmark_count:total(up.below_benchmark_count,down.below_benchmark_count),
          total_count:total(up.total_count,down.total_count),
          pct_above_benchmark:100*total(up.above_benchmark_count,down.above_benchmark_count)/total(up.total_count,down.total_count),
          above_active_return_pct:weighted(up.above_active_return_pct,up.above_benchmark_count,down.above_active_return_pct,down.above_benchmark_count),
          below_active_return_pct:weighted(up.below_active_return_pct,up.below_benchmark_count,down.below_active_return_pct,down.below_benchmark_count),
          overall_active_return_pct:weighted(up.overall_active_return_pct,up.total_count,down.overall_active_return_pct,down.total_count),
        },
      ].filter(Boolean);
    };

    const renderReturnVsBenchmarkBars = (host, rows, {label,key,color}) => {
      const bins=returnVsBenchmarkBins(rows,20); if(!bins.length)return;
      const values=bins.flatMap(bin=>[bin.portfolio_return_pct,bin.benchmark_return_pct]);
      let min=Math.min(0,...values),max=Math.max(0,...values);
      const yDomain=outwardDomain(min,max,{lowerPad:0,upperPad:0,target:10});
      yDomain.min=Math.min(0,yDomain.min); yDomain.max=Math.max(0,yDomain.max);
      const width=1000,height=390,left=58,right=22,top=18,bottom=58;
      const groupWidth=(width-left-right)/bins.length;
      const barWidth=Math.min(14,groupWidth*.32);
      const y=value=>top+(yDomain.max-value)*(height-top-bottom)/(yDomain.max-yDomain.min||1);
      const zero=y(0);
      const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`});
      ticksFor(yDomain).forEach(value=>{
        const yy=y(value);
        svg.appendChild(svgEl('line',{x1:left,y1:yy,x2:width-right,y2:yy,class:'v3-grid'}));
        svg.appendChild(svgEl('text',{x:left-7,y:yy+3,'text-anchor':'end',class:'v3-tick'},`${value.toFixed(1)}%`));
      });
      bins.forEach((bin,index)=>{
        const center=left+groupWidth*(index+0.5);
        const pair=[
          {value:bin.portfolio_return_pct,color,label},
          {value:bin.benchmark_return_pct,color:MINT,label:benchmarkLabel},
        ];
        pair.forEach((item,pairIndex)=>{
          const x=center+(pairIndex===0?-barWidth:0);
          const rect=svgEl('rect',{x,y:item.value>=0?y(item.value):zero,width:barWidth*.88,height:Math.max(1,Math.abs(y(item.value)-zero)),fill:item.color});
          rect.addEventListener('mousemove',event=>showTip(event,`<b>Return vs Benchmark</b><br>${esc(label)}: ${pct(bin.portfolio_return_pct)}<br>${esc(benchmarkLabel)}: ${pct(bin.benchmark_return_pct)}<br>Months in group: ${bin.observations}`));
          rect.addEventListener('mouseleave',hideTip);
          svg.appendChild(rect);
        });
        svg.appendChild(svgEl('text',{x:center,y:height-bottom+17,'text-anchor':'middle',class:'v3-tick'},`${bin.benchmark_return_pct.toFixed(1)}%`));
      });
      svg.appendChild(svgEl('line',{x1:left,y1:zero,x2:width-right,y2:zero,class:'v3-axis'}));
      svg.appendChild(svgEl('line',{x1:left,y1:top,x2:left,y2:height-bottom,class:'v3-axis'}));
      svg.appendChild(svgEl('text',{x:(left+width-right)/2,y:height-5,'text-anchor':'middle',class:'v3-axis-label'},'Benchmark Return'));
      svg.appendChild(svgEl('text',{x:14,y:(top+height-bottom)/2,transform:`rotate(-90 14 ${(top+height-bottom)/2})`,'text-anchor':'middle',class:'v3-axis-label'},'Return'));
      host.appendChild(svg);
      const legend=document.createElement('div');legend.className='v3-chart-legend';legend.innerHTML=`<span style="--color:${color}">${esc(label)}</span><span style="--color:${MINT}">${esc(benchmarkLabel)}</span>`;host.appendChild(legend);
    };

    const renderUpDown = () => {
      const host=chart('up-down-market'); const oldSlot=tableSlot('up-down-market');
      if(!host)return; host.innerHTML=''; if(oldSlot)oldSlot.style.display='none';
      const perf=records('up_down_market_performance');
      const panels=[
        {key:'provided',label:'Provided Portfolio',color:BLUE,rows:data.up_down_scatter_provided||[]},
        {key:'optimized',label:optimizedLabel,color:PURPLE,rows:data.up_down_scatter_optimized||[]},
      ];
      panels.forEach(panel=>{
        const wrap=document.createElement('div');wrap.className='v3-updown-panel';
        wrap.innerHTML=`<h3>${esc(panel.label)} vs. ${esc(benchmarkLabel)}</h3><div class="table-slot"></div><div class="v3-bar-title">Return vs. Benchmark</div><div class="v3-bar-subtitle">${esc(panel.label)} vs. ${esc(benchmarkLabel)}</div><div class="v3-return-bars"></div>`;
        host.appendChild(wrap);
        const summary=upDownSummaryRows(perf,panel.key);
        wrap.querySelector('.table-slot').innerHTML=`<table class="feedback-table"><thead><tr><th rowspan="2">Market Type</th><th colspan="4">Occurrences</th><th colspan="3">Average Active Return</th></tr><tr><th>Above Benchmark</th><th>Below Benchmark</th><th>Total</th><th>% Above Benchmark</th><th>Above Benchmark</th><th>Below Benchmark</th><th>Total</th></tr></thead><tbody>${summary.map(row=>`<tr><td>${esc(row.label)}</td><td>${row.above_benchmark_count??''}</td><td>${row.below_benchmark_count??''}</td><td>${row.total_count??''}</td><td>${pct(row.pct_above_benchmark)}</td><td>${pct(row.above_active_return_pct)}</td><td>${pct(row.below_active_return_pct)}</td><td>${pct(row.overall_active_return_pct)}</td></tr>`).join('')}</tbody></table>`;
        renderReturnVsBenchmarkBars(wrap.querySelector('.v3-return-bars'),panel.rows,panel);
      });
    };
    renderUpDown();
  };

  if (document.readyState === 'complete') setTimeout(run,0);
  else window.addEventListener('load',()=>setTimeout(run,0),{once:true});
})();
</script>
""".strip()


def _inject_user_feedback_v3_script(html: str) -> str:
    if 'id="report-user-feedback-v3"' in html:
        return html
    closing_body = "</body>"
    if closing_body not in html:
        raise ValueError("report HTML missing closing body tag")
    return html.replace(closing_body, f"  {_USER_FEEDBACK_V3_SCRIPT}\n{closing_body}", 1)


def _postprocess_report(path: Path) -> Path:
    html = path.read_text(encoding="utf-8")
    path.write_text(_inject_user_feedback_v3_script(html), encoding="utf-8")
    return path


def render_report(
    model: ReportModel,
    output_path: str | Path,
    *,
    template_path: str | Path | None = None,
) -> Path:
    target = _base_render_report(model, output_path, template_path=template_path)
    return _postprocess_report(target)


def generate_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> Path:
    target = _base_generate_report(run_dir, output_path=output_path, template_path=template_path)
    return _postprocess_report(target)

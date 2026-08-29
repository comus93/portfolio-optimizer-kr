from __future__ import annotations

from pathlib import Path

from .builder import build_report_model
from .feedback_v3 import render_report as _render_feedback_v3
from .report_model import ReportModel


_USER_FEEDBACK_V4_SCRIPT = r"""
<script id="report-user-feedback-v4">
(() => {
  const run = () => {
    const data = window.PORTFOLIO_REPORT_DATA || {};
    const NS = 'h' + 'ttp://www.w3.org/2000/svg';
    const BLUE = '#2563eb';
    const PURPLE = '#7c3aed';
    const GRAY = '#64748b';
    const RED = '#e11d48';
    const MINT = '#50d8b0';
    const finite = value => value !== null && value !== undefined && Number.isFinite(Number(value));
    const number = value => finite(value) ? Number(value) : null;
    const pct = value => finite(value) ? `${Number(value).toFixed(2)}%` : 'N/A';
    const ratio = value => finite(value) ? Number(value).toFixed(2) : 'N/A';
    const money = value => finite(value) ? (Number(value) * 10000).toLocaleString(undefined,{style:'currency',currency:'USD',maximumFractionDigits:0}) : 'N/A';
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    const section = id => document.querySelector(`#${id}`);
    const chart = id => section(id)?.querySelector('.chart');
    const tableSlot = id => section(id)?.querySelector('.table-slot');
    const records = name => data.tables?.[name] || [];
    const optimizedLabel = data.objective_name || 'Optimized Portfolio';
    const benchmarkLabel = data.benchmark_name || data.benchmark_symbol || 'Benchmark';
    const providedLabel = 'Provided Portfolio';
    const optRows = records('optimization_results');
    const optByTicker = new Map(optRows.map(row => [String(row.ticker),row]));
    const assetName = ticker => optByTicker.get(String(ticker))?.name || String(ticker);
    const assetColors = new Map(optRows.map((row,index)=>[String(row.ticker),['#2563eb','#f97316','#22c55e','#e11d48','#7c3aed','#0891b2','#ca8a04','#4f46e5'][index%8]]));
    const assetColor = ticker => assetColors.get(String(ticker)) || GRAY;
    const tip = document.querySelector('.tooltip') || (()=>{const el=document.createElement('div');el.className='tooltip';document.body.appendChild(el);return el;})();
    const showTip = (event,html) => {tip.innerHTML=html;tip.style.display='block';tip.style.left=`${event.clientX+14}px`;tip.style.top=`${event.clientY+14}px`;};
    const hideTip = () => {tip.style.display='none';};
    const svgEl = (tag,attrs={},text='') => {const el=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,String(v)));if(text!=='')el.textContent=String(text);return el;};

    const style=document.createElement('style');
    style.id='report-user-feedback-v4-style';
    style.textContent=`
      #efficient-frontier .chart svg.v4-frontier-svg{height:clamp(440px,48vw,560px)}
      .v4-rolling-panel{margin:14px 0 34px}.v4-rolling-title{text-align:center;font-weight:700;font-size:17px;margin:6px 0 3px}.v4-rolling-subtitle{text-align:center;color:#475569;font-size:12px;margin-bottom:6px}
      .v4-rolling-panel svg{height:clamp(360px,42vw,470px)}
      .v4-legend{display:flex;justify-content:center;gap:22px;font-size:12px;margin-top:8px}.v4-legend span::before{content:'';display:inline-block;width:10px;height:10px;background:var(--color);margin-right:6px;border-radius:50%}
      .v4-grid{stroke:#e5e7eb;stroke-width:1}.v4-axis{stroke:#94a3b8;stroke-width:1}.v4-tick{fill:#475569;font-size:10px}.v4-axis-label{fill:#334155;font-size:11px}.v4-frontier-label{fill:#475569;font-size:9.5px}
    `;
    document.head.appendChild(style);

    const renderTable = (id, rows, cols) => {
      const slot=tableSlot(id); if(!slot)return;
      if(!rows.length){slot.innerHTML='<div class="empty">N/A</div>';return;}
      slot.style.display='';
      slot.innerHTML=`<table class="feedback-table"><thead><tr>${cols.map(c=>`<th>${esc(c.label)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${cols.map(c=>{const v=typeof c.value==='function'?c.value(r):r[c.key];return `<td>${c.format?c.format(v,r):esc(v??'')}</td>`}).join('')}</tr>`).join('')}</tbody></table>`;
    };

    const performanceRows = () => {
      const base=records('performance_summary').map(row=>({...row}));
      const byMetric=new Map(base.map(row=>[String(row.metric),row]));
      const landmarks=new Map((data.frontier_landmarks||[]).map(row=>[String(row.kind),row]));
      const active=new Map(records('benchmark_summary').map(row=>[String(row.portfolio),row]));
      const add=(metric,unit,provided,optimized,benchmark)=>byMetric.set(metric,{metric,unit,provided,optimized,benchmark});
      add('Sharpe Ratio (ex-ante)','ratio',landmarks.get('provided')?.sharpe_ratio,landmarks.get('optimized')?.sharpe_ratio,landmarks.get('benchmark')?.sharpe_ratio);
      add('Active Return','pct',active.get('provided')?.active_return_pct,active.get('optimized')?.active_return_pct,null);
      add('Tracking Error','pct',active.get('provided')?.tracking_error_pct,active.get('optimized')?.tracking_error_pct,null);
      add('Information Ratio','ratio',active.get('provided')?.information_ratio,active.get('optimized')?.information_ratio,null);
      const order=['Start Balance','End Balance','CAGR','Expected Return','Standard Deviation','Best Year','Worst Year','Maximum Drawdown','Sharpe Ratio (ex-ante)','Sharpe Ratio (ex-post)','Sortino Ratio','Active Return','Tracking Error','Information Ratio'];
      return order.map(name=>byMetric.get(name)).filter(Boolean);
    };
    const metricFormat=(value,row)=>row.unit==='balance'?money(value):(row.unit==='pct'||row.unit==='percent'?pct(value):ratio(value));
    const required=performanceRows();
    const summaryCols=[{key:'metric',label:'Metric'},{key:'provided',label:providedLabel,format:metricFormat},{key:'optimized',label:optimizedLabel,format:metricFormat},{key:'benchmark',label:benchmarkLabel,format:metricFormat}];
    renderTable('performance-summary',required,summaryCols);

    const advanced=records('portfolio_metrics').filter(row=>!required.some(base=>String(base.metric).toLowerCase()===String(row.metric).replaceAll('_',' ').toLowerCase()));
    const titleCase=value=>String(value??'').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
    const combined=[...required,...advanced.map(row=>({...row,metric:titleCase(row.metric)}))];
    renderTable('portfolio-metrics',combined,summaryCols);

    const assetStats=records('asset_statistics').map(row=>({...row,name:assetName(row.ticker)}));
    const pctDecimal=value=>finite(value)?pct(Number(value)*100):'N/A';
    renderTable('asset-performance',assetStats,[
      {key:'ticker',label:'Ticker'},{key:'name',label:'Name'},
      {key:'cagr_pct',label:'CAGR',format:pct},{key:'annualized_return',label:'Annualized Return',format:pctDecimal},{key:'annualized_volatility_pct',label:'Stdev',format:pct},
      {key:'best_year',label:'Best Year',format:pctDecimal},{key:'worst_year',label:'Worst Year',format:pctDecimal},{key:'max_drawdown_pct',label:'Max Drawdown',format:pct},
      {key:'sharpe_ex_post',label:'Sharpe Ratio',format:ratio},{key:'sortino',label:'Sortino Ratio',format:ratio},
      {key:'3m',label:'3M',format:pctDecimal},{key:'ytd',label:'YTD',format:pctDecimal},{key:'1y',label:'1Y',format:pctDecimal},{key:'3y',label:'3Y Ann.',format:pctDecimal},{key:'5y',label:'5Y Ann.',format:pctDecimal},{key:'10y',label:'10Y Ann.',format:pctDecimal},
    ]);

    // Keep portfolio identities consistent wherever generic labels survived earlier render layers.
    const identityMap=new Map([['Provided',providedLabel],['Provided Portfolio',providedLabel],['Optimized',optimizedLabel],['Optimized Portfolio',optimizedLabel],['Benchmark',benchmarkLabel]]);
    document.querySelectorAll('table th,table td,.subtable-card h3').forEach(node=>{const key=(node.textContent||'').trim();if(identityMap.has(key))node.textContent=identityMap.get(key);});

    const niceStep=(span,target=8)=>{if(!(span>0))return 1;const raw=span/Math.max(target,1),p=10**Math.floor(Math.log10(raw)),f=raw/p,n=f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10;return n*p;};
    const outward=(min,max,{lower=0,upper=0,target=8}={})=>{const lo=min-lower,hi=max+upper,step=niceStep(hi-lo,target);return{min:Math.floor(lo/step)*step,max:Math.ceil(hi/step)*step,step};};
    const ticks=domain=>{const out=[];for(let v=domain.min;v<=domain.max+domain.step*.1&&out.length<30;v+=domain.step)out.push(Math.abs(v)<1e-10?0:Number(v.toFixed(10)));return out;};

    const renderFrontier=()=>{
      const root=chart('efficient-frontier');
      const points=(data.efficient_frontier||[]).filter(p=>finite(p.volatility_pct)&&finite(p.expected_return_pct)).slice().sort((a,b)=>Number(a.volatility_pct)-Number(b.volatility_pct));
      const assets=(data.frontier_assets||[]).filter(a=>finite(a.standard_deviation_pct)&&finite(a.expected_return_pct));
      const landmarks=(data.frontier_landmarks||[]).filter(a=>finite(a.volatility_pct)&&finite(a.expected_return_pct));
      if(!root||!points.length)return;
      const cx=points.map(p=>Number(p.volatility_pct)),cy=points.map(p=>Number(p.expected_return_pct));
      const cmin=Math.min(...cx),cmax=Math.max(...cx),span=cmax-cmin;
      const contextRight=cmax+Math.max(span,4.0),contextLeft=cmin-Math.max(span*.15,.5);
      const nearby=assets.filter(a=>Number(a.standard_deviation_pct)>=contextLeft&&Number(a.standard_deviation_pct)<=contextRight);
      const domainPoints=[...points,...nearby.map(a=>({volatility_pct:a.standard_deviation_pct,expected_return_pct:a.expected_return_pct})),...landmarks];
      const xs=domainPoints.map(p=>Number(p.volatility_pct)),ys=domainPoints.map(p=>Number(p.expected_return_pct));
      const xDomain=outward(Math.min(...xs),Math.max(...xs),{lower:.35,upper:.35,target:20});
      const yDomain=outward(Math.min(...ys),Math.max(...ys),{lower:.5,upper:.8,target:12});
      const width=1000,height=500,left=70,right=30,top=20,bottom=56;
      const x=v=>left+(v-xDomain.min)*(width-left-right)/(xDomain.max-xDomain.min||1),y=v=>top+(yDomain.max-v)*(height-top-bottom)/(yDomain.max-yDomain.min||1);
      const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,class:'v4-frontier-svg'});
      ticks(yDomain).forEach(v=>{const yy=y(v);svg.appendChild(svgEl('line',{x1:left,y1:yy,x2:width-right,y2:yy,class:'v4-grid'}));svg.appendChild(svgEl('text',{x:left-7,y:yy+3,'text-anchor':'end',class:'v4-tick'},`${v.toFixed(1)}%`));});
      ticks(xDomain).forEach(v=>{const xx=x(v);svg.appendChild(svgEl('line',{x1:xx,y1:top,x2:xx,y2:height-bottom,class:'v4-grid'}));svg.appendChild(svgEl('text',{x:xx,y:height-bottom+17,'text-anchor':'middle',class:'v4-tick'},`${v.toFixed(1)}%`));});
      svg.appendChild(svgEl('line',{x1:left,y1:height-bottom,x2:width-right,y2:height-bottom,class:'v4-axis'}));svg.appendChild(svgEl('line',{x1:left,y1:top,x2:left,y2:height-bottom,class:'v4-axis'}));
      svg.appendChild(svgEl('text',{x:(left+width-right)/2,y:height-6,'text-anchor':'middle',class:'v4-axis-label'},'Standard Deviation %'));svg.appendChild(svgEl('text',{x:15,y:(top+height-bottom)/2,transform:`rotate(-90 15 ${(top+height-bottom)/2})`,'text-anchor':'middle',class:'v4-axis-label'},'Expected Return %'));
      const curvePts=points.map(p=>`${x(Number(p.volatility_pct))},${y(Number(p.expected_return_pct))}`).join(' ');svg.appendChild(svgEl('polyline',{points:curvePts,fill:'none',stroke:BLUE,'stroke-width':3}));
      const hit=svgEl('polyline',{points:curvePts,fill:'none',stroke:'transparent','stroke-width':20,'pointer-events':'stroke'});hit.addEventListener('mousemove',event=>{const rect=svg.getBoundingClientRect(),px=(event.clientX-rect.left)*width/rect.width,v=xDomain.min+(px-left)*(xDomain.max-xDomain.min)/(width-left-right),near=points.reduce((best,p)=>Math.abs(Number(p.volatility_pct)-v)<Math.abs(Number(best.volatility_pct)-v)?p:best,points[0]);showTip(event,`<b>Efficient Frontier</b><br>Expected Return: ${pct(near.expected_return_pct)}<br>Standard Deviation: ${pct(near.volatility_pct)}<br>Sharpe Ratio: ${ratio(near.sharpe_ratio)}<br><br>${Object.entries(near.weights_pct||{}).map(([t,w])=>`${esc(assetName(t))} (${esc(t)}): ${pct(w)}`).join('<br>')}`);});hit.addEventListener('mouseleave',hideTip);svg.appendChild(hit);
      const inside=(vx,vy)=>vx>=xDomain.min&&vx<=xDomain.max&&vy>=yDomain.min&&vy<=yDomain.max,hidden=[];
      assets.forEach((a,index)=>{const vx=Number(a.standard_deviation_pct),vy=Number(a.expected_return_pct);if(!inside(vx,vy)){hidden.push(a);return;}const c=svgEl('circle',{cx:x(vx),cy:y(vy),r:5,fill:assetColor(a.symbol)});c.addEventListener('mousemove',e=>showTip(e,`<b>${esc(a.name||assetName(a.symbol))} (${esc(a.symbol)})</b><br>Expected Return: ${pct(vy)}<br>Std Dev: ${pct(vx)}<br>Sharpe Ratio: ${ratio(a.sharpe_ratio)}`));c.addEventListener('mouseleave',hideTip);svg.appendChild(c);svg.appendChild(svgEl('text',{x:x(vx)+(index%2? -7:7),y:y(vy)-7,'text-anchor':index%2?'end':'start',class:'v4-frontier-label'},a.symbol));});
      landmarks.forEach((l,index)=>{const vx=Number(l.volatility_pct),vy=Number(l.expected_return_pct);if(!inside(vx,vy))return;const c=svgEl('circle',{cx:x(vx),cy:y(vy),r:5.5,fill:RED});c.addEventListener('mousemove',e=>showTip(e,`<b>${esc(l.label)}</b><br>Expected Return: ${pct(vy)}<br>Std Dev: ${pct(vx)}<br>Sharpe Ratio: ${ratio(l.sharpe_ratio)}`));c.addEventListener('mouseleave',hideTip);svg.appendChild(c);svg.appendChild(svgEl('text',{x:x(vx)+7,y:y(vy)+(index%2?13:-7),class:'v4-frontier-label'},l.label));});
      root.innerHTML='';root.appendChild(svg);section('efficient-frontier')?.querySelectorAll('.legend').forEach(n=>n.remove());const legend=document.createElement('div');legend.className='legend';legend.innerHTML=`<span style="--color:${BLUE}">Efficient Frontier</span><span style="--color:${GRAY}">Assets</span><span style="--color:${RED}">Portfolio / Benchmark</span>`;root.before(legend);
      section('efficient-frontier')?.querySelectorAll('.frontier-hidden,.v3-frontier-hidden').forEach(n=>n.remove());if(hidden.length){const wrap=document.createElement('div');wrap.className='frontier-hidden table-slot';wrap.innerHTML=`<h3>Assets outside chart scale</h3><table class="feedback-table"><thead><tr><th>Name</th><th>Ticker</th><th>Std Dev</th><th>Expected Return</th><th>Sharpe Ratio</th></tr></thead><tbody>${hidden.map(a=>`<tr><td>${esc(a.name||assetName(a.symbol))}</td><td>${esc(a.symbol)}</td><td>${pct(a.standard_deviation_pct)}</td><td>${pct(a.expected_return_pct)}</td><td>${ratio(a.sharpe_ratio)}</td></tr>`).join('')}</tbody></table>`;section('efficient-frontier').appendChild(wrap);}
    };
    renderFrontier();

    const renderRollingActive=()=>{
      const host=chart('rolling-active-return');if(!host)return;host.innerHTML='';section('rolling-active-return')?.querySelectorAll('.legend').forEach(n=>n.remove());
      [{label:providedLabel,rows:data.rolling_active_provided||[]},{label:optimizedLabel,rows:data.rolling_active_optimized||[]}].forEach(panel=>{
        const rows=panel.rows.filter(r=>finite(r.active_return_pct)&&finite(r.tracking_error_pct));if(!rows.length)return;
        const leftVals=rows.map(r=>Number(r.active_return_pct)),rightVals=rows.map(r=>Number(r.tracking_error_pct));
        const lmin=Math.min(0,...leftVals),lmax=Math.max(0,...leftVals),lspan=lmax-lmin||1,leftDomain=outward(lmin,lmax,{lower:lspan*.05,upper:lspan*.05,target:7});
        const rmin=Math.min(...rightVals),rmax=Math.max(...rightVals),rspan=rmax-rmin||1,rightDomain=outward(rmin,rmax,{lower:rspan*.08,upper:rspan*.08,target:6});
        const width=1000,height=420,left=72,right=72,top=22,bottom=54,xStep=(width-left-right)/rows.length,x=i=>left+xStep*(i+.5),yl=v=>top+(leftDomain.max-v)*(height-top-bottom)/(leftDomain.max-leftDomain.min||1),yr=v=>top+(rightDomain.max-v)*(height-top-bottom)/(rightDomain.max-rightDomain.min||1),zero=yl(0);
        const wrap=document.createElement('div');wrap.className='v4-rolling-panel';wrap.innerHTML=`<div class="v4-rolling-title">Rolling Active Return and Risk (36 months)</div><div class="v4-rolling-subtitle">${esc(panel.label)} vs. ${esc(benchmarkLabel)}</div>`;const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`});
        ticks(leftDomain).forEach(v=>{const yy=yl(v);svg.appendChild(svgEl('line',{x1:left,y1:yy,x2:width-right,y2:yy,class:'v4-grid'}));svg.appendChild(svgEl('text',{x:left-8,y:yy+3,'text-anchor':'end',class:'v4-tick'},`${v.toFixed(1)}%`));});ticks(rightDomain).forEach(v=>svg.appendChild(svgEl('text',{x:width-right+8,y:yr(v)+3,'text-anchor':'start',class:'v4-tick'},`${v.toFixed(1)}%`)));
        const years=[...new Set(rows.map(r=>new Date(`${String(r.date).slice(0,10)}T00:00:00`).getFullYear()))],stride=Math.max(1,Math.ceil(years.length/5));years.filter((_,i)=>i%stride===0||i===years.length-1).forEach(year=>{const idx=rows.findIndex(r=>new Date(`${String(r.date).slice(0,10)}T00:00:00`).getFullYear()===year);if(idx<0)return;const xx=x(idx);svg.appendChild(svgEl('text',{x:xx,y:height-bottom+18,'text-anchor':'middle',class:'v4-tick'},year));});
        svg.appendChild(svgEl('line',{x1:left,y1:height-bottom,x2:width-right,y2:height-bottom,class:'v4-axis'}));svg.appendChild(svgEl('line',{x1:left,y1:top,x2:left,y2:height-bottom,class:'v4-axis'}));svg.appendChild(svgEl('line',{x1:width-right,y1:top,x2:width-right,y2:height-bottom,class:'v4-axis'}));svg.appendChild(svgEl('text',{x:17,y:(top+height-bottom)/2,transform:`rotate(-90 17 ${(top+height-bottom)/2})`,'text-anchor':'middle',class:'v4-axis-label'},'Active Return'));svg.appendChild(svgEl('text',{x:width-17,y:(top+height-bottom)/2,transform:`rotate(90 ${width-17} ${(top+height-bottom)/2})`,'text-anchor':'middle',class:'v4-axis-label'},'Tracking Error'));
        rows.forEach((r,i)=>{const v=Number(r.active_return_pct),yy=yl(v),bar=svgEl('rect',{x:x(i)-Math.max(1,xStep*.22),y:Math.min(zero,yy),width:Math.max(2,xStep*.44),height:Math.max(1,Math.abs(zero-yy)),fill:BLUE});bar.addEventListener('mousemove',e=>showTip(e,`<b>${esc(String(r.date).slice(0,7))}</b><br>Active Return: ${pct(r.active_return_pct)}<br>Tracking Error: ${pct(r.tracking_error_pct)}`));bar.addEventListener('mouseleave',hideTip);svg.appendChild(bar);});
        const line=svgEl('polyline',{points:rows.map((r,i)=>`${x(i)},${yr(Number(r.tracking_error_pct))}`).join(' '),fill:'none',stroke:MINT,'stroke-width':3});svg.appendChild(line);rows.forEach((r,i)=>{const hit=svgEl('circle',{cx:x(i),cy:yr(Number(r.tracking_error_pct)),r:6,fill:'transparent'});hit.addEventListener('mousemove',e=>showTip(e,`<b>${esc(String(r.date).slice(0,7))}</b><br>Active Return: ${pct(r.active_return_pct)}<br>Tracking Error: ${pct(r.tracking_error_pct)}`));hit.addEventListener('mouseleave',hideTip);svg.appendChild(hit);});
        wrap.appendChild(svg);const legend=document.createElement('div');legend.className='v4-legend';legend.innerHTML=`<span style="--color:${BLUE}">Active Return</span><span style="--color:${MINT}">Tracking Error</span>`;wrap.appendChild(legend);host.appendChild(wrap);
      });
    };
    renderRollingActive();
  };
  if(document.readyState==='complete') setTimeout(run,20); else window.addEventListener('load',()=>setTimeout(run,20),{once:true});
})();
</script>
"""


def _inject_user_feedback_v4_script(html: str) -> str:
    if 'id="report-user-feedback-v4"' in html:
        return html
    return html.replace("</body>", _USER_FEEDBACK_V4_SCRIPT + "\n</body>")


def render_report(
    model: ReportModel,
    output_path: str | Path,
    *,
    template_path: str | Path | None = None,
) -> Path:
    target = _render_feedback_v3(model, output_path, template_path=template_path)
    html = target.read_text(encoding="utf-8")
    target.write_text(_inject_user_feedback_v4_script(html), encoding="utf-8")
    return target


def generate_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> Path:
    root = Path(run_dir)
    model = build_report_model(root)
    target = Path(output_path) if output_path is not None else root / "report.html"
    return render_report(model, target, template_path=template_path)

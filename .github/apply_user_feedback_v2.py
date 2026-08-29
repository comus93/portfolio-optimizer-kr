from pathlib import Path


def replace_once(path: str, old: str, new: str, marker: str | None = None) -> None:
    target = Path(path)
    text = target.read_text(encoding='utf-8')
    if marker and marker in text:
        return
    if old not in text:
        raise SystemExit(f'patch anchor not found in {path}: {old[:80]!r}')
    target.write_text(text.replace(old, new, 1), encoding='utf-8')


replace_once(
    'src/portfolio_optimizer_kr/viewer/report_model.py',
    '    benchmark_name: str | None = None\n    tables: Mapping[str, tuple[JSONRecord, ...]] = field(default_factory=dict)\n',
    '    benchmark_name: str | None = None\n    metadata: Mapping[str, Any] = field(default_factory=dict)\n    tables: Mapping[str, tuple[JSONRecord, ...]] = field(default_factory=dict)\n',
    marker='    metadata: Mapping[str, Any] = field(default_factory=dict)\n',
)

replace_once(
    'src/portfolio_optimizer_kr/viewer/builder.py',
    '        benchmark_symbol=benchmark_symbol,\n        benchmark_name=benchmark_name,\n        tables=tables,\n',
    '        benchmark_symbol=benchmark_symbol,\n        benchmark_name=benchmark_name,\n        metadata={\n            "configuration": dict(artifacts.result.get("configuration") or {}),\n            "data_coverage": dict(artifacts.result.get("data_coverage") or {}),\n        },\n        tables=tables,\n',
    marker='            "data_coverage": dict(artifacts.result.get("data_coverage") or {}),\n',
)

pipeline = Path('src/portfolio_optimizer_kr/pipeline.py')
text = pipeline.read_text(encoding='utf-8')
if 'def _asset_price_coverage(' not in text:
    anchor = '\ndef _completed_monthly_returns(\n'
    if anchor not in text:
        raise SystemExit('pipeline helper insertion anchor not found')
    helper = '''\n\ndef _asset_price_coverage(\n    request: OptimizationRequest, prices: Mapping[str, pd.Series]\n) -> dict[str, dict[str, object]]:\n    coverage: dict[str, dict[str, object]] = {}\n    for asset in request.assets:\n        series = prices.get(asset.symbol)\n        if series is None:\n            continue\n        observed = series.dropna()\n        if observed.empty:\n            continue\n        coverage[asset.symbol] = {\n            "name": asset.name,\n            "start": str(pd.Timestamp(observed.index.min()).date()),\n            "end": str(pd.Timestamp(observed.index.max()).date()),\n            "observations": int(len(observed)),\n        }\n    return coverage\n'''
    text = text.replace(anchor, helper + anchor, 1)

metric_anchor = '    metric_names = sorted({metric for values in by_portfolio.values() for metric in values})\n'
if 'by_portfolio["benchmark"] = portfolio_metrics(benchmark, benchmark, rf)' not in text:
    if metric_anchor not in text:
        raise SystemExit('portfolio metrics insertion anchor not found')
    text = text.replace(
        metric_anchor,
        '    if benchmark is not None:\n'
        '        by_portfolio["benchmark"] = portfolio_metrics(benchmark, benchmark, rf)\n'
        + metric_anchor,
        1,
    )

canonical_anchor = '    metrics_table = _portfolio_metrics_table(paths, benchmark_returns, rf)\n    canonical = CanonicalResult(\n'
if '    asset_price_coverage = _asset_price_coverage(request, prices)\n' not in text:
    if canonical_anchor not in text:
        raise SystemExit('canonical result insertion anchor not found')
    text = text.replace(
        canonical_anchor,
        '    metrics_table = _portfolio_metrics_table(paths, benchmark_returns, rf)\n'
        '    asset_price_coverage = _asset_price_coverage(request, prices)\n'
        '    canonical = CanonicalResult(\n',
        1,
    )
coverage_anchor = '"benchmark_overlap": benchmark_summary.get("coverage")},\n'
if '"asset_prices": asset_price_coverage' not in text:
    if coverage_anchor not in text:
        raise SystemExit('data coverage anchor not found')
    text = text.replace(
        coverage_anchor,
        '"benchmark_overlap": benchmark_summary.get("coverage"), "asset_prices": asset_price_coverage},\n',
        1,
    )
pipeline.write_text(text, encoding='utf-8')

replace_once(
    'src/portfolio_optimizer_kr/report/result.py',
    '        metrics.loc[is_percentage, ["provided", "optimized"]] *= 100\n',
    '        value_columns = [\n            column for column in ("provided", "optimized", "benchmark") if column in metrics\n        ]\n        metrics.loc[is_percentage, value_columns] *= 100\n',
    marker='        value_columns = [\n            column for column in ("provided", "optimized", "benchmark") if column in metrics\n',
)

template = Path('site/report-template.html')
parts = [Path(f'.github/report-user-feedback-v2-part{i}.txt').read_text(encoding='utf-8') for i in range(1, 6)]
fragment = ''.join(parts).rstrip()
html = template.read_text(encoding='utf-8')
if 'id="report-user-feedback-v2"' not in html:
    if '</body>' not in html:
        raise SystemExit('report template missing closing body tag')
    html = html.replace('</body>', fragment + '\n</body>', 1)
    template.write_text(html, encoding='utf-8')

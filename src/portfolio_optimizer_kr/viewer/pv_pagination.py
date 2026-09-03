from __future__ import annotations

from pathlib import Path


_MARKER = '<meta name="pv-monthly-pagination" content="applied" />'

_STYLE = """
<style id="pv-monthly-pagination-style">
.monthly-pagination{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:13px}
.monthly-pagination .page-size{display:flex;align-items:center;gap:6px}
.monthly-pagination select{border:1px solid #d1d5db;border-radius:6px;padding:4px 22px 4px 7px;background:#fff;color:#111827}
.monthly-pagination .page-actions{display:flex;align-items:center;gap:4px}
.monthly-pagination button{border:1px solid #d1d5db;background:#fff;color:#1f2937;border-radius:5px;padding:5px 9px;cursor:pointer}
.monthly-pagination button:hover:not(:disabled){background:#f3f4f6}
.monthly-pagination button:disabled{opacity:.4;cursor:default}
.monthly-pagination .page-info{color:#4b5563}
</style>
"""

_SCRIPT = r"""
<script id="pv-monthly-pagination-script">
(() => {
  const init = () => {
    const table = document.getElementById('monthly-returns-detail');
    if (!table || table.dataset.paginationReady === '1') return;
    const body = table.tBodies[0];
    if (!body) return;
    const rows = Array.from(body.rows);
    if (!rows.length) return;
    table.dataset.paginationReady = '1';

    const controls = document.createElement('div');
    controls.className = 'monthly-pagination';
    controls.innerHTML = `
      <label class="page-size">Show
        <select aria-label="Monthly returns rows per page">
          <option value="12" selected>12</option>
          <option value="25">25</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
        entries
      </label>
      <span class="page-info" aria-live="polite"></span>
      <span class="page-actions">
        <button type="button" data-action="first">First</button>
        <button type="button" data-action="prev">Previous</button>
        <button type="button" data-action="next">Next</button>
        <button type="button" data-action="last">Last</button>
      </span>`;

    const wrap = table.closest('.table-wrap');
    (wrap || table).insertAdjacentElement('afterend', controls);
    const select = controls.querySelector('select');
    const info = controls.querySelector('.page-info');
    const buttons = Object.fromEntries(
      Array.from(controls.querySelectorAll('button')).map(button => [button.dataset.action, button])
    );
    let page = 0;
    let size = 12;

    const render = () => {
      const pages = Math.max(1, Math.ceil(rows.length / size));
      page = Math.max(0, Math.min(page, pages - 1));
      const start = page * size;
      const end = Math.min(rows.length, start + size);
      rows.forEach((row, index) => {
        row.style.display = index >= start && index < end ? '' : 'none';
      });
      info.textContent = `Showing ${start + 1} to ${end} of ${rows.length} entries`;
      buttons.first.disabled = page === 0;
      buttons.prev.disabled = page === 0;
      buttons.next.disabled = page >= pages - 1;
      buttons.last.disabled = page >= pages - 1;
    };

    select.addEventListener('change', () => {
      size = Number(select.value) || 12;
      page = 0;
      render();
    });
    buttons.first.addEventListener('click', () => { page = 0; render(); });
    buttons.prev.addEventListener('click', () => { page -= 1; render(); });
    buttons.next.addEventListener('click', () => { page += 1; render(); });
    buttons.last.addEventListener('click', () => { page = Math.ceil(rows.length / size) - 1; render(); });
    render();
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true});
  else init();
})();
</script>
"""


def apply_monthly_returns_pagination(output_path: str | Path) -> Path:
    path = Path(output_path)
    if not path.is_file():
        return path
    html = path.read_text(encoding="utf-8")
    if _MARKER in html or 'id="monthly-returns-detail"' not in html:
        return path
    html = html.replace("</head>", f"{_MARKER}\n{_STYLE}\n</head>", 1)
    html = html.replace("</body>", f"{_SCRIPT}\n</body>", 1)
    path.write_text(html, encoding="utf-8")
    return path

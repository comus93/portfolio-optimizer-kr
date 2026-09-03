from __future__ import annotations

import portfolio_optimizer_kr.viewer as viewer


def test_public_report_boundary_adds_monthly_pagination(tmp_path, monkeypatch):
    target = tmp_path / "report.html"
    rows = "".join(f"<tr><td>{index}</td></tr>" for index in range(1, 81))

    def fake_generate_report(*args, **kwargs):
        target.write_text(
            '<html><head></head><body><div class="table-wrap">'
            '<table id="monthly-returns-detail"><tbody>'
            f"{rows}</tbody></table></div></body></html>",
            encoding="utf-8",
        )
        return target

    monkeypatch.setattr(viewer, "_generate_report", fake_generate_report)
    rendered = viewer.generate_report(tmp_path)
    html = rendered.read_text(encoding="utf-8")

    assert viewer.generate_report.__module__.endswith("final_renderer")
    assert 'meta name="pv-monthly-pagination"' in html
    assert 'id="pv-monthly-pagination-script"' in html
    assert '<option value="12" selected>12</option>' in html
    assert 'data-action="first"' in html
    assert 'data-action="prev"' in html
    assert 'data-action="next"' in html
    assert 'data-action="last"' in html
    assert "Showing ${start + 1} to ${end} of ${rows.length} entries" in html

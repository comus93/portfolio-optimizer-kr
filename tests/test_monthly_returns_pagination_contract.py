from __future__ import annotations
import pandas as pd
from portfolio_optimizer_kr.viewer import pv_round1_overlay as overlay

def test_pv_monthly_pagination_contract():
    frame=pd.DataFrame([{"year":2026,"month":(i%12)+1,"series::P::return":.01,"series::P::balance":100+i,"asset::SPY::return":.02} for i in range(13)])
    html=overlay._monthly_detail_table(frame,["P"],None,{"SPY":"SPY"},"USD")
    assert 'Showing 1 to 12 of 13 entries' in html
    assert "row.style.display=hide?'none':'table-row'" in html
    for name in ("first","previous","next","last"):
        assert f'id="monthly-page-{name}"' in html

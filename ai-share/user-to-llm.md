최상단 Title

Portfolio Optimization · 20260829-p1-polish-validation 여기에 (시작월 시작년 - 종료월 종료월) 추가 필요

--> PV에선 전 달인 7월까지만 계산이 되었다 깔끔함

아래 제약 노트 필요

Note:

The time period was constrained by the available data for Invesco S&P 500 Momentum ETF (SPMO) [Nov 2015 - Jul 2026].



Provided Portfolio, Optimized Portfolio 의 파이 차트에 마우스 오버 할 경우 종목과 % 표기 필요

Annual Returns

 우리는 2017 -Provided Annual Return % : 23.89%

           2017 - Optimized Annual Return % : 23.08 %

           2017 - Benchmark Annual Return % : 21.71 %

  ==> 년도의 3개중 어느 차트를 누르더라도

2017

(파란색점)  Provided Annual Return : 23.89%

(보라색점)  Optimized Annual Return  : 23.08 %

(회색점)  Benchmark Annual Return  : 21.71 %



4. Efficient Frontier Assets

테이블내 Asset 칼럼에 현재는 

QQQ로 티커만 표기 됨

==> 

Name                       Ticker

Invesco QQQ Trust       QQQ

으로 name 칼럼 추가하고 가장 왼쪽으로 



5. Asset Correlations

Name                       Ticker

Invesco QQQ Trust       QQQ

으로 name 칼럼 추가하고 가장 왼쪽으로 



6. Efficient Frontier (중요)

. Scaling을 DOT 기준이 아닌 곡선 기준으로 맞춤. 즉 곡선 범위를 벗어난 dot은 보여지지 않게 처리하며 보여지지 않은 종목은 아래 테이블 추가하여 종목 티커, Std Dev % Expected Return %, Sharpe 별도 표기

. Efficient Frontier 곡선 마우스 오버할경우 구성 종목 %, Expected Return % Standard Deviation %, 가 나타아야 함 (중요)



7. Efficient Frontier Transition Map ==> Efficient Frontier Transition Map (기간)





종목 % 가장 오른쪽 칼럼에 Expected Return , Standard Deviation, Sharpe Ratio % 나타내기 (중요)

하단 노트

*Annualized ex-ante values shown for portfolio return and volatility. Ex-ante Sharpe Ratio calculated using historical U.S. 3-Month Treasury Bill Rate returns as the risk-free rate.  



Annualized Active Return

-이것역시 bar 마우스 오버하면 년도 그루핑 해서 포트별 % 표기



Active Return Contribution

-왼쪽 눈금 필요 0 100% 200% 이런식으로 

-아래쪽 눈금 필요 May 2021 Aug 2021이런식으

-date portfoilio ticker....로 구성된 테이블 제거





Rolling Active Return / Tracking Error

세로 % 눈금 가로 월 년 필요



Up vs. Down Market Performance 현재 구성 폐기 후 재구성 필요



Provided Portfolio vs. State Street SPDR S&P 500 ETF

Up vs. Down Market Performance - Provided Portfolio vs. State Street SPDR S&P 500 ETF

Market TypeOccurrencesAverage Active Return

Above BenchmarkBelow BenchmarkTotal% Above BenchmarkAbove BenchmarkBelow BenchmarkTotal

Up Market

42

43

85

49%

1.89%

-1.74%

0.05%

Down Market

18

17

35

51%

2.15%

-1.19%

0.53%

Total

60

60

120

50%

1.97%

-1.59%

0.19%




하단 

return vs benchmark  바형 차트 세로는 return %, 가로는 Benchmark Return %

(provided portfolio vs S&P 500 ETF) 





Maximum Sharpe Ratio vs. State Street SPDR S&P 500 ETF

Up vs. Down Market Performance - Maximum Sharpe Ratio vs. State Street SPDR S&P 500 ETF

Market TypeOccurrencesAverage Active Return

Above BenchmarkBelow BenchmarkTotal% Above BenchmarkAbove BenchmarkBelow BenchmarkTotal

Up Market

36

49

85

42%

1.00%

-1.49%

-0.43%

Down Market

29

6

35

83%

2.11%

-0.70%

1.63%

Total

65

55

120

54%

1.49%

-1.40%

0.17%





하단 

return vs benchmark  바형 차트 세로는 return %, 가로는 Benchmark Return %

(provided portfolio vs S&P 500 ETF) 





Portfolio Metrics

가장 오른쪽 Benchmark 칼럼 추가 필요

sharpe sortino등 추가 필요. 이건 specification md참조



Drawdowns

세로 drowdown % 눈금 추가 필요

가로 year 눈금 추가 필요



Portfolio Asset Performance

Ticker이외 Name 칼럼 추가





TickerNameCAGRStdevBest YearWorst YearMax DrawdownSharpe RatioSortino Ratio

QQQ

Invesco QQQ Trust

20.41%

18.97%

54.85%

-32.58%

-32.58%

0.96

1.62

SPMO

Invesco S&P 500 Momentum ETF

19.57%

17.95%

45.81%

-10.46%

-21.35%

0.96

1.71

GDX

VanEck Gold Miners ETF

10.32%

33.94%

154.71%

-31.41%

-43.31%

0.38

0.66

SLV

iShares Silver Trust

10.47%

29.89%

144.66%

-21.91%

-38.39%

0.40

0.68

AIA

iShares Asia 50 ETF

13.43%

21.68%

47.79%

-23.76%

-50.34%

0.58

0.99

XLE

State StreetEngySelSectSPDRETF

10.26%

30.01%

64.17%

-32.51%

-58.14%

0.40

0.63

GLD

SPDR Gold Shares

11.16%

15.10%

63.68%

-15.02%

-23.85%

0.63

1.08



이런식으로 테이블 다시 구성



Portfolio / Asset Correlations

종목 name 칼럼 추가



Risk Decomposition

종목 name 칼럼 추가







Annual Asset Returns

년별로 그루핑해서 

  ==> 년도해당 어느 차트를 누르더라도 구성 전체 종목과 % 표





Rolling 3Y Returns

세로축 annualized return 눈금 추가

가로축 달 년 눈금 추가



Rolling 5Y Returns

세로축 annualized return 눈금 추가

가로축 달 년 눈금 추가


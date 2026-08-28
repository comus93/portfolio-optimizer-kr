Portfolio Optimization               

Minimize Menu

*   [
    
    Summary
    
    ](#overview)
*   [
    
    Assets
    
    ](#portfolioComponents)
*   [
    
    Active Returns
    
    ](#activeReturns)
*   [
    
    Metrics
    
    ](#metrics)
*   [
    
    Annual Returns
    
    ](#annualReturns)
*   [
    
    Monthly Returns
    
    ](#monthlyReturns)
*   [
    
    Drawdowns
    
    ](#drawdowns)
*   [
    
    Assets
    
    ](#portfolioComponents)
*   [
    
    Rolling Returns
    
    ](#rollingReturns)

# Portfolio Optimization

## Portfolio Optimization Overview

This portfolio optimizer tool supports the following portfolio optimization strategies:

*   Mean Variance Optimization – Find the optimal risk adjusted portfolio that lies on the efficient frontier
*   Conditional Value-at-Risk – Optimize the portfolio to minimize the expected tail loss
*   Risk Parity – Find the portfolio that equalizes the risk contribution of portfolio assets
*   Tracking Error – Find the portfolio that minimizes the tracking error against the selected benchmark
*   Information Ratio – Find the portfolio that maximizes the information ratio against the selected benchmark
*   Kelly Criterion – Finds the portfolio with the maximum expected geometric growth rate
*   Sortino Ratio – Find the portfolio that maximizes the Sortino ratio for the given minimum acceptable return
*   Omega Ratio – Find the portfolio that maximizes the Omega ratio for the given minimum acceptable return
*   Maximum Drawdown – Find the portfolio with the minimum worst case drawdown with optional minimum acceptable return

The optimization is based on the monthly return statistics of the selected portfolio assets for the given time period. The optimization result does not predict what allocation would perform best outside the given time period, and the actual performance of portfolios constructed using the optimized asset weights may vary from the given performance goal.

The required inputs for the optimization include the time range and the portfolio assets. Portfolio asset weights and constraints are optional. You can also use the [Black-Litterman model](black-litterman-model) based portfolio optimization, which allows the benchmark portfolio asset weights to be optimized based on investor's views.

### Portfolio Optimization Configuration

## Portfolio Optimization Results (Aug 2016 - Jul 2026) [](javascript:void\(0\);)[Link](javascript:void\(0\);) [PDF](javascript:void\(0\)) [Excel](javascript:void\(0\)) [Save](#)

Note:

*   The time period was constrained by the available data for Invesco S&P 500 Momentum ETF (SPMO) \[Nov 2015 - Jul 2026\].
*   The time period of the results is limited to 10 years for free tier accounts.

Portfolio optimization results with the goal to maximize Sharpe ratio. The possible range of expected annual portfolio returns for the given period taking into account the specified constraints is 16.23% to 30.08%. Refer to the efficient frontier section for additional details.

#### Provided Portfolio

| Ticker | Name | Allocation |
| --- | --- | --- |
| QQQ | Invesco QQQ Trust | 20.00% |
| SPMO | Invesco S&P 500 Momentum ETF | 10.00% |
| GDX | VanEck Gold Miners ETF | 10.00% |
| SLV | iShares Silver Trust | 10.00% |
| AIA | iShares Asia 50 ETF | 15.00% |
| XLE | State StreetEngySelSectSPDRETF | 15.00% |
| PTF | Invesco Dorsey Wright Technology MomtETF | 10.00% |
| QLD | ProShares Ultra QQQ | 10.00% |
| Save Portfolio |

Created with Highcharts 10.3.320.0 %10.0 %10.0 %10.0 %15.0 %15.0 %10.0 %10.0 %Invesco QQQ TrustInvesco S&P 500 Momentum ETFVanEck Gold Miners ETFiShares Silver TrustiShares Asia 50 ETFState StreetEngySelSectSPDRETFInvesco Dorsey Wright Technology MomtETFProShares Ultra QQQiShares Asia 50 ETF​Allocation: 15.00%

#### Maximum Sharpe Ratio

| Ticker | Name | Allocation |
| --- | --- | --- |
| QQQ | Invesco QQQ Trust | 24.61% |
| SPMO | Invesco S&P 500 Momentum ETF | 40.72% |
| GLD | SPDR Gold Shares | 30.00% |
| XLE | State StreetEngySelSectSPDRETF | 4.66% |
| Save Portfolio |

Created with Highcharts 10.3.324.6 %40.7 %30.0 %Invesco QQQ TrustInvesco S&P 500 Momentum ETFSPDR Gold SharesState StreetEngySelSectSPDRETF

#### Performance Summary

Portfolio performance statistics

| Metric | Provided Portfolio | Maximum Sharpe Ratio | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- |
| Start Balance | $10,000 | $10,000 | $10,000 |
| End Balance | $57,949 | $50,793 | $40,420 |
| Annualized Return (CAGR) | 19.21% | 17.65% | 14.99% |
| Expected Return | 19.42% | 17.21% | 15.22% |
| Standard Deviation | 18.71% | 13.10% | 15.32% |
| Best Year | 44.10% | 35.11% | 31.22% |
| Worst Year | \-14.75% | \-10.38% | \-18.17% |
| Maximum Drawdown | \-24.58% | \-18.28% | \-23.93% |
| Sharpe Ratio (ex-ante) | 0.91 | 1.13 | 0.84 |
| Sharpe Ratio (ex-post) | 0.91 | 1.14 | 0.84 |
| Sortino Ratio | 1.56 | 2.02 | 1.32 |
| Active Return | 4.22% | 2.66% | N/A |
| Tracking Error | 8.38% | 6.68% | N/A |
| Information Ratio | 0.50 | 0.40 | N/A |
| Results based on historical returns. Expected return is the annualized monthly arithmetic mean return. |

#### Portfolio Growth

Created with Highcharts 10.3.3YearPortfolio Balance ($)Provided PortfolioMaximum Sharpe RatioState Street SPDR S&P 500 ETF2017201820192020202120222023202420252026$0$10,000$20,000$30,000$40,000$50,000$60,000$70,000

 Logarithmic scale     Inflation adjusted

#### Annual Returns

Created with Highcharts 10.3.3YearAnnual ReturnProvided PortfolioMaximum Sharpe RatioState Street SPDR S&P 500 ETF20162017201820192020202120222023202420252026\-30.0%\-20.0%\-10.0%0.0%10.0%20.0%30.0%40.0%50.0%

#### Trailing Returns

Trailing Returns

| Name | Total Return | Annualized Return | Annualized Standard Deviation |
| --- | --- | --- | --- |
| 3 Month | Year To Date | 1 year | 3 year | 5 year | 10 year | Full | 3 year | 5 year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Provided Portfolio | \-1.20% | 18.65% | 45.36% | 30.16% | 19.64% | 19.21% | 19.21% | 16.87% | 19.19% |
| Maximum Sharpe Ratio | 0.60% | 12.27% | 26.51% | 30.46% | 19.00% | 17.65% | 17.65% | 12.74% | 14.16% |
| State Street SPDR S&P 500 ETF | 4.21% | 10.13% | 19.49% | 19.20% | 12.76% | 14.99% | 14.99% | 13.06% | 15.88% |
| Trailing return and volatility are as of last calendar month ending July 2026 |

#### Efficient Frontier Assets

Efficient Frontier Assets

| # | Asset | Expected Return | Standard Deviation | Sharpe Ratio | Min. Weight | Max. Weight |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Invesco QQQ Trust | 20.49% | 18.97% | 0.956 | 0.00% | 50.00% |
| 2 | Invesco S&P 500 Momentum ETF | 19.57% | 17.95% | 0.959 | 0.00% | 50.00% |
| 3 | VanEck Gold Miners ETF | 15.34% | 33.94% | 0.382 | 0.00% | 30.00% |
| 4 | SPDR Gold Shares | 11.75% | 15.10% | 0.622 | 0.00% | 30.00% |
| 5 | iShares Silver Trust | 14.30% | 29.89% | 0.399 | 0.00% | 30.00% |
| 6 | iShares Asia 50 ETF | 14.95% | 21.68% | 0.581 | 0.00% | 30.00% |
| 7 | State StreetEngySelSectSPDRETF | 14.29% | 30.01% | 0.398 | 0.00% | 30.00% |
| 8 | Invesco Dorsey Wright Technology MomtETF | 24.31% | 28.89% | 0.760 | 0.00% | 50.00% |
| 9 | ProShares Ultra QQQ | 35.86% | 38.81% | 0.863 | 0.00% | 50.00% |
| Results based on historical returns. Expected return is the annualized monthly arithmetic mean return. Ex-ante Sharpe Ratio calculated using U.S. 3-Month Treasury Bill Rate returns as the risk-free rate. |

#### Asset Correlations

Efficient Frontier Asset Correlations

| Name | Ticker | QQQ | SPMO | GDX | GLD | SLV | AIA | XLE | PTF | QLD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Invesco QQQ Trust | QQQ | 1.00 | 0.83 | 0.24 | 0.12 | 0.26 | 0.58 | 0.29 | 0.83 | 1.00 |
| Invesco S&P 500 Momentum ETF | SPMO | 0.83 | 1.00 | 0.17 | 0.03 | 0.20 | 0.48 | 0.33 | 0.76 | 0.83 |
| VanEck Gold Miners ETF | GDX | 0.24 | 0.17 | 1.00 | 0.84 | 0.73 | 0.37 | 0.20 | 0.14 | 0.24 |
| SPDR Gold Shares | GLD | 0.12 | 0.03 | 0.84 | 1.00 | 0.76 | 0.35 | \-0.03 | 0.06 | 0.12 |
| iShares Silver Trust | SLV | 0.26 | 0.20 | 0.73 | 0.76 | 1.00 | 0.40 | 0.14 | 0.22 | 0.27 |
| iShares Asia 50 ETF | AIA | 0.58 | 0.48 | 0.37 | 0.35 | 0.40 | 1.00 | 0.26 | 0.54 | 0.59 |
| State StreetEngySelSectSPDRETF | XLE | 0.29 | 0.33 | 0.20 | \-0.03 | 0.14 | 0.26 | 1.00 | 0.24 | 0.31 |
| Invesco Dorsey Wright Technology MomtETF | PTF | 0.83 | 0.76 | 0.14 | 0.06 | 0.22 | 0.54 | 0.24 | 1.00 | 0.83 |
| ProShares Ultra QQQ | QLD | 1.00 | 0.83 | 0.24 | 0.12 | 0.27 | 0.59 | 0.31 | 0.83 | 1.00 |
| Based on monthly returns from Aug 2016 to Jul 2026 |

#### Efficient Frontier

Created with Highcharts 10.3.3Expected ReturnStandard DeviationEfficient Frontier (Aug 2016 - Jul 2026)Tangency PortfolioProShares Ultra QQQInvesco Dorsey Wright Technology MomtETFState StreetEngySelSectSPDRETFiShares Asia 50 ETFiShares Silver TrustSPDR Gold SharesVanEck Gold Miners ETFInvesco S&P 500 Momentum ETFInvesco QQQ TrustState Street SPDR S&P 500 ETFMaximum Sharpe RatioProvided Portfolio10.0%15.0%20.0%25.0%30.0%35.0%40.0%10.0%12.0%14.0%16.0%18.0%20.0%22.0%24.0%26.0%28.0%30.0%32.0%34.0%36.0%38.0%40.0%42.0%

Created with Highcharts 10.3.3Standard DeviationAllocationEfficient Frontier Transition Map (Aug 2016 - Jul 2026)Invesco QQQ TrustInvesco S&P 500 Momentum ETFVanEck Gold Miners ETFSPDR Gold SharesiShares Asia 50 ETFState StreetEngySelSectSPDRETFInvesco Dorsey Wright Technology MomtETFProShares Ultra QQQ14.0%16.0%18.0%20.0%22.0%24.0%26.0%28.0%30.0%32.0%0.0%10.0%20.0%30.0%40.0%50.0%60.0%70.0%80.0%90.0%100.0%

#### Efficient Frontier Portfolios

Efficient Frontier Assets

| # | Invesco QQQ Trust | Invesco S&P 500 Momentum ETF | VanEck Gold Miners ETF | SPDR Gold Shares | iShares Silver Trust | iShares Asia 50 ETF | State StreetEngySelSectSPDRETF | Invesco Dorsey Wright Technology MomtETF | ProShares Ultra QQQ | Expected Return \* | Standard Deviation \* | Sharpe Ratio \* |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5.69% | 43.10% | 0.00% | 30.00% | 0.00% | 10.42% | 10.80% | 0.00% | 0.00% | 16.23% | 12.74% | 1.089 |
| 2 | 8.30% | 42.91% | 0.00% | 30.00% | 0.00% | 8.59% | 10.20% | 0.00% | 0.00% | 16.37% | 12.74% | 1.099 |
| 3 | 10.91% | 42.72% | 0.00% | 30.00% | 0.00% | 6.77% | 9.60% | 0.00% | 0.00% | 16.51% | 12.76% | 1.108 |
| 4 | 13.52% | 42.53% | 0.00% | 30.00% | 0.00% | 4.95% | 9.00% | 0.00% | 0.00% | 16.65% | 12.80% | 1.116 |
| 5 | 16.13% | 42.34% | 0.00% | 30.00% | 0.00% | 3.13% | 8.40% | 0.00% | 0.00% | 16.79% | 12.85% | 1.123 |
| 6 | 18.75% | 42.15% | 0.00% | 30.00% | 0.00% | 1.30% | 7.80% | 0.00% | 0.00% | 16.93% | 12.91% | 1.128 |
| 7 | 21.50% | 41.73% | 0.00% | 30.00% | 0.00% | 0.00% | 6.77% | 0.00% | 0.00% | 17.07% | 12.99% | 1.132 |
| 8 | 24.61% | 40.72% | 0.00% | 30.00% | 0.00% | 0.00% | 4.66% | 0.00% | 0.00% | 17.21% | 13.10% | 1.134 |
| 9 | 27.72% | 39.72% | 0.00% | 30.00% | 0.00% | 0.00% | 2.55% | 0.00% | 0.00% | 17.35% | 13.24% | 1.132 |
| 10 | 26.95% | 39.99% | 0.00% | 30.00% | 0.00% | 0.00% | 2.25% | 0.00% | 0.81% | 17.49% | 13.40% | 1.129 |
| 11 | 25.54% | 40.47% | 0.00% | 30.00% | 0.00% | 0.00% | 2.25% | 0.00% | 1.74% | 17.63% | 13.56% | 1.126 |
| 12 | 24.14% | 40.94% | 0.00% | 30.00% | 0.00% | 0.00% | 2.24% | 0.00% | 2.68% | 17.77% | 13.73% | 1.122 |
| 13 | 22.73% | 41.41% | 0.00% | 30.00% | 0.00% | 0.00% | 2.24% | 0.00% | 3.62% | 17.91% | 13.89% | 1.119 |
| 14 | 21.33% | 41.89% | 0.00% | 30.00% | 0.00% | 0.00% | 2.23% | 0.00% | 4.55% | 18.05% | 14.05% | 1.116 |
| 15 | 19.92% | 42.36% | 0.00% | 30.00% | 0.00% | 0.00% | 2.23% | 0.00% | 5.49% | 18.19% | 14.22% | 1.113 |
| 16 | 18.51% | 42.84% | 0.00% | 30.00% | 0.00% | 0.00% | 2.22% | 0.00% | 6.43% | 18.33% | 14.38% | 1.110 |
| 17 | 17.11% | 43.31% | 0.00% | 30.00% | 0.00% | 0.00% | 2.21% | 0.00% | 7.36% | 18.47% | 14.55% | 1.107 |
| 18 | 15.70% | 43.79% | 0.00% | 30.00% | 0.00% | 0.00% | 2.21% | 0.00% | 8.30% | 18.61% | 14.71% | 1.104 |
| 19 | 14.30% | 44.26% | 0.00% | 30.00% | 0.00% | 0.00% | 2.20% | 0.00% | 9.24% | 18.75% | 14.88% | 1.102 |
| 20 | 12.89% | 44.74% | 0.00% | 30.00% | 0.00% | 0.00% | 2.20% | 0.00% | 10.18% | 18.89% | 15.04% | 1.099 |
| 21 | 11.49% | 45.21% | 0.00% | 30.00% | 0.00% | 0.00% | 2.19% | 0.00% | 11.11% | 19.03% | 15.21% | 1.096 |
| 22 | 10.08% | 45.69% | 0.00% | 30.00% | 0.00% | 0.00% | 2.19% | 0.00% | 12.05% | 19.17% | 15.37% | 1.093 |
| 23 | 8.67% | 46.16% | 0.00% | 30.00% | 0.00% | 0.00% | 2.18% | 0.00% | 12.99% | 19.31% | 15.54% | 1.091 |
| 24 | 7.27% | 46.63% | 0.00% | 30.00% | 0.00% | 0.00% | 2.17% | 0.00% | 13.92% | 19.45% | 15.70% | 1.088 |
| 25 | 5.86% | 47.11% | 0.00% | 30.00% | 0.00% | 0.00% | 2.17% | 0.00% | 14.86% | 19.59% | 15.87% | 1.085 |
| 26 | 4.46% | 47.58% | 0.00% | 30.00% | 0.00% | 0.00% | 2.16% | 0.00% | 15.80% | 19.73% | 16.04% | 1.083 |
| 27 | 3.05% | 48.06% | 0.00% | 30.00% | 0.00% | 0.00% | 2.16% | 0.00% | 16.73% | 19.86% | 16.20% | 1.080 |
| 28 | 1.65% | 48.53% | 0.00% | 30.00% | 0.00% | 0.00% | 2.15% | 0.00% | 17.67% | 20.00% | 16.37% | 1.078 |
| 29 | 0.24% | 49.01% | 0.00% | 30.00% | 0.00% | 0.00% | 2.15% | 0.00% | 18.61% | 20.14% | 16.54% | 1.076 |
| 30 | 0.00% | 48.53% | 0.00% | 30.00% | 0.00% | 0.00% | 2.03% | 0.00% | 19.44% | 20.28% | 16.70% | 1.073 |
| 31 | 0.00% | 47.85% | 0.00% | 30.00% | 0.00% | 0.00% | 1.89% | 0.00% | 20.26% | 20.42% | 16.87% | 1.071 |
| 32 | 0.00% | 47.17% | 0.00% | 30.00% | 0.00% | 0.00% | 1.75% | 0.00% | 21.07% | 20.56% | 17.04% | 1.068 |
| 33 | 0.00% | 46.50% | 0.00% | 30.00% | 0.00% | 0.00% | 1.61% | 0.00% | 21.89% | 20.70% | 17.21% | 1.066 |
| 34 | 0.00% | 45.82% | 0.00% | 30.00% | 0.00% | 0.00% | 1.48% | 0.00% | 22.70% | 20.84% | 17.38% | 1.063 |
| 35 | 0.00% | 45.15% | 0.00% | 30.00% | 0.00% | 0.00% | 1.34% | 0.00% | 23.52% | 20.98% | 17.56% | 1.061 |
| 36 | 0.00% | 44.47% | 0.00% | 30.00% | 0.00% | 0.00% | 1.20% | 0.00% | 24.33% | 21.12% | 17.73% | 1.058 |
| 37 | 0.00% | 43.79% | 0.00% | 30.00% | 0.00% | 0.00% | 1.06% | 0.00% | 25.15% | 21.26% | 17.91% | 1.056 |
| 38 | 0.00% | 43.12% | 0.00% | 30.00% | 0.00% | 0.00% | 0.92% | 0.00% | 25.96% | 21.40% | 18.08% | 1.053 |
| 39 | 0.00% | 42.44% | 0.00% | 30.00% | 0.00% | 0.00% | 0.78% | 0.00% | 26.77% | 21.54% | 18.26% | 1.051 |
| 40 | 0.00% | 41.76% | 0.00% | 30.00% | 0.00% | 0.00% | 0.65% | 0.00% | 27.59% | 21.68% | 18.44% | 1.048 |
| 41 | 0.00% | 41.09% | 0.00% | 30.00% | 0.00% | 0.00% | 0.51% | 0.00% | 28.40% | 21.82% | 18.62% | 1.046 |
| 42 | 0.00% | 40.41% | 0.00% | 30.00% | 0.00% | 0.00% | 0.37% | 0.00% | 29.22% | 21.96% | 18.79% | 1.043 |
| 43 | 0.00% | 39.74% | 0.00% | 30.00% | 0.00% | 0.00% | 0.23% | 0.00% | 30.03% | 22.10% | 18.98% | 1.041 |
| 44 | 0.00% | 39.06% | 0.00% | 30.00% | 0.00% | 0.00% | 0.09% | 0.00% | 30.85% | 22.24% | 19.16% | 1.038 |
| 45 | 0.00% | 38.32% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 31.68% | 22.38% | 19.34% | 1.035 |
| 46 | 0.00% | 37.46% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 32.54% | 22.52% | 19.52% | 1.033 |
| 47 | 0.00% | 36.60% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 33.40% | 22.66% | 19.70% | 1.030 |
| 48 | 0.00% | 35.74% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 34.26% | 22.80% | 19.89% | 1.028 |
| 49 | 0.00% | 34.88% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 35.12% | 22.94% | 20.07% | 1.025 |
| 50 | 0.00% | 34.03% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 35.97% | 23.08% | 20.26% | 1.023 |
| 51 | 0.00% | 33.17% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 36.83% | 23.22% | 20.45% | 1.020 |
| 52 | 0.00% | 32.31% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 37.69% | 23.36% | 20.63% | 1.018 |
| 53 | 0.00% | 31.45% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 38.55% | 23.50% | 20.82% | 1.015 |
| 54 | 0.00% | 30.59% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 39.41% | 23.64% | 21.01% | 1.013 |
| 55 | 0.00% | 29.73% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 40.27% | 23.78% | 21.20% | 1.011 |
| 56 | 0.00% | 28.87% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 41.13% | 23.92% | 21.39% | 1.008 |
| 57 | 0.00% | 28.01% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 41.99% | 24.06% | 21.58% | 1.006 |
| 58 | 0.00% | 27.15% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 42.85% | 24.20% | 21.77% | 1.003 |
| 59 | 0.00% | 26.29% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 43.71% | 24.34% | 21.97% | 1.001 |
| 60 | 0.00% | 25.43% | 0.00% | 30.00% | 0.00% | 0.00% | 0.00% | 0.00% | 44.57% | 24.48% | 22.16% | 0.998 |
| 61 | 0.00% | 24.63% | 0.00% | 29.96% | 0.00% | 0.00% | 0.00% | 0.00% | 45.41% | 24.62% | 22.35% | 0.996 |
| 62 | 0.00% | 24.10% | 0.00% | 29.74% | 0.00% | 0.00% | 0.00% | 0.00% | 46.16% | 24.76% | 22.55% | 0.994 |
| 63 | 0.00% | 23.57% | 0.00% | 29.51% | 0.00% | 0.00% | 0.00% | 0.00% | 46.91% | 24.90% | 22.74% | 0.991 |
| 64 | 0.00% | 23.04% | 0.00% | 29.29% | 0.00% | 0.00% | 0.00% | 0.00% | 47.67% | 25.04% | 22.93% | 0.989 |
| 65 | 0.00% | 22.51% | 0.00% | 29.07% | 0.00% | 0.00% | 0.00% | 0.00% | 48.42% | 25.18% | 23.13% | 0.987 |
| 66 | 0.00% | 21.99% | 0.00% | 28.84% | 0.00% | 0.00% | 0.00% | 0.00% | 49.17% | 25.32% | 23.32% | 0.985 |
| 67 | 0.00% | 21.46% | 0.00% | 28.62% | 0.00% | 0.00% | 0.00% | 0.00% | 49.92% | 25.46% | 23.52% | 0.982 |
| 68 | 0.00% | 23.01% | 0.00% | 26.99% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 25.60% | 23.72% | 0.980 |
| 69 | 0.00% | 24.79% | 0.00% | 25.21% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 25.74% | 23.92% | 0.978 |
| 70 | 0.00% | 26.58% | 0.00% | 23.42% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 25.88% | 24.13% | 0.975 |
| 71 | 0.00% | 28.37% | 0.00% | 21.63% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 26.02% | 24.35% | 0.972 |
| 72 | 0.00% | 30.16% | 0.00% | 19.84% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 26.16% | 24.56% | 0.969 |
| 73 | 0.00% | 31.95% | 0.00% | 18.05% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 26.30% | 24.79% | 0.966 |
| 74 | 0.00% | 33.73% | 0.00% | 16.27% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 26.44% | 25.02% | 0.963 |
| 75 | 0.00% | 35.52% | 0.00% | 14.48% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 26.58% | 25.25% | 0.959 |
| 76 | 0.00% | 37.11% | 0.00% | 12.77% | 0.00% | 0.00% | 0.00% | 0.12% | 50.00% | 26.72% | 25.49% | 0.956 |
| 77 | 0.00% | 37.35% | 0.00% | 11.56% | 0.00% | 0.00% | 0.00% | 1.09% | 50.00% | 26.86% | 25.73% | 0.952 |
| 78 | 0.00% | 37.59% | 0.00% | 10.36% | 0.00% | 0.00% | 0.00% | 2.05% | 50.00% | 27.00% | 25.98% | 0.949 |
| 79 | 0.00% | 37.83% | 0.00% | 9.15% | 0.00% | 0.00% | 0.00% | 3.02% | 50.00% | 27.14% | 26.22% | 0.945 |
| 80 | 0.00% | 38.07% | 0.00% | 7.95% | 0.00% | 0.00% | 0.00% | 3.98% | 50.00% | 27.28% | 26.47% | 0.942 |
| 81 | 0.00% | 38.31% | 0.00% | 6.74% | 0.00% | 0.00% | 0.00% | 4.95% | 50.00% | 27.42% | 26.72% | 0.938 |
| 82 | 0.00% | 38.55% | 0.00% | 5.54% | 0.00% | 0.00% | 0.00% | 5.91% | 50.00% | 27.56% | 26.98% | 0.934 |
| 83 | 0.00% | 38.79% | 0.00% | 4.33% | 0.00% | 0.00% | 0.00% | 6.88% | 50.00% | 27.70% | 27.23% | 0.931 |
| 84 | 0.00% | 39.16% | 0.66% | 2.61% | 0.00% | 0.00% | 0.00% | 7.57% | 50.00% | 27.84% | 27.49% | 0.927 |
| 85 | 0.00% | 39.52% | 1.33% | 0.88% | 0.00% | 0.00% | 0.00% | 8.27% | 50.00% | 27.98% | 27.75% | 0.923 |
| 86 | 0.00% | 38.79% | 1.38% | 0.00% | 0.00% | 0.00% | 0.00% | 9.82% | 50.00% | 28.12% | 28.01% | 0.920 |
| 87 | 0.00% | 36.93% | 0.81% | 0.00% | 0.00% | 0.00% | 0.00% | 12.26% | 50.00% | 28.26% | 28.28% | 0.916 |
| 88 | 0.00% | 35.06% | 0.23% | 0.00% | 0.00% | 0.00% | 0.00% | 14.71% | 50.00% | 28.40% | 28.55% | 0.912 |
| 89 | 0.00% | 32.54% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 17.46% | 50.00% | 28.54% | 28.83% | 0.908 |
| 90 | 0.00% | 29.58% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 20.42% | 50.00% | 28.68% | 29.12% | 0.904 |
| 91 | 0.00% | 26.63% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 23.37% | 50.00% | 28.82% | 29.42% | 0.900 |
| 92 | 0.00% | 23.67% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 26.33% | 50.00% | 28.96% | 29.72% | 0.895 |
| 93 | 0.00% | 20.71% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 29.29% | 50.00% | 29.10% | 30.03% | 0.890 |
| 94 | 0.00% | 17.75% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 32.25% | 50.00% | 29.24% | 30.35% | 0.886 |
| 95 | 0.00% | 14.79% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 35.21% | 50.00% | 29.38% | 30.68% | 0.881 |
| 96 | 0.00% | 11.83% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 38.17% | 50.00% | 29.52% | 31.02% | 0.876 |
| 97 | 0.00% | 8.88% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 41.12% | 50.00% | 29.66% | 31.36% | 0.871 |
| 98 | 0.00% | 5.92% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 44.08% | 50.00% | 29.80% | 31.70% | 0.866 |
| 99 | 0.00% | 2.96% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 47.04% | 50.00% | 29.94% | 32.06% | 0.860 |
| 100 | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 50.00% | 50.00% | 30.08% | 32.42% | 0.855 |
| \*Annualized ex-ante values shown for portfolio return and volatility. Ex-ante Sharpe Ratio calculated using historical U.S. 3-Month Treasury Bill Rate returns as the risk-free rate. |

#### Annualized Active Return

Created with Highcharts 10.3.3YearActive ReturnAnnualized Active ReturnActive Return vs. State Street SPDR S&P 500 ETFProvided PortfolioMaximum Sharpe Ratio20162017201820192020202120222023202420252026\-20.0%\-10.0%0.0%10.0%20.0%30.0%

#### Active Return Contribution

Created with Highcharts 10.3.3Cumulative Active ReturnCumulative Active ReturnProvided Portfolio vs. State Street SPDR S&P 500 ETFInvesco QQQ TrustInvesco S&P 500 Momentum ETFVanEck Gold Miners ETFiShares Silver TrustiShares Asia 50 ETFState StreetEngySelSectSPDRETFInvesco Dorsey Wright Technology MomtETFProShares Ultra QQQAug 2016Sep 2016Oct 2016Nov 2016Dec 2016Jan 2017Feb 2017Mar 2017Apr 2017May 2017Jun 2017Jul 2017Aug 2017Sep 2017Oct 2017Nov 2017Dec 2017Jan 2018Feb 2018Mar 2018Apr 2018May 2018Jun 2018Jul 2018Aug 2018Sep 2018Oct 2018Nov 2018Dec 2018Jan 2019Feb 2019Mar 2019Apr 2019May 2019Jun 2019Jul 2019Aug 2019Sep 2019Oct 2019Nov 2019Dec 2019Jan 2020Feb 2020Mar 2020Apr 2020May 2020Jun 2020Jul 2020Aug 2020Sep 2020Oct 2020Nov 2020Dec 2020Jan 2021Feb 2021Mar 2021Apr 2021May 2021Jun 2021Jul 2021Aug 2021Sep 2021Oct 2021Nov 2021Dec 2021Jan 2022Feb 2022Mar 2022Apr 2022May 2022Jun 2022Jul 2022Aug 2022Sep 2022Oct 2022Nov 2022Dec 2022Jan 2023Feb 2023Mar 2023Apr 2023May 2023Jun 2023Jul 2023Aug 2023Sep 2023Oct 2023Nov 2023Dec 2023Jan 2024Feb 2024Mar 2024Apr 2024May 2024Jun 2024Jul 2024Aug 2024Sep 2024Oct 2024Nov 2024Dec 2024Jan 2025Feb 2025Mar 2025Apr 2025May 2025Jun 2025Jul 2025Aug 2025Sep 2025Oct 2025Nov 2025Dec 2025Jan 2026Feb 2026Mar 2026Apr 2026May 2026Jun 2026Jul 2026\-200.0%\-100.0%0.0%100.0%200.0%300.0%

Cumulative Active Return - Provided Portfolio vs. State Street SPDR S&P 500 ETF

| Asset | 1-year | 3-year | 5-year | 10-year | Full |
| --- | --- | --- | --- | --- | --- |
| Invesco QQQ Trust | 2.54% | 7.78% | 7.68% | 46.90% | 46.90% |
| Invesco S&P 500 Momentum ETF | 2.90% | 21.65% | 16.99% | 20.95% | 20.95% |
| VanEck Gold Miners ETF | 13.63% | 25.76% | 22.00% | 0.58% | 0.58% |
| iShares Silver Trust | 17.93% | 21.71% | 19.05% | \-3.32% | \-3.32% |
| iShares Asia 50 ETF | 23.72% | 23.10% | 4.46% | \-1.65% | \-1.65% |
| State StreetEngySelSectSPDRETF | 15.50% | \-3.03% | 45.81% | \-8.71% | \-8.71% |
| Invesco Dorsey Wright Technology MomtETF | 10.83% | 9.99% | 9.37% | 37.75% | 37.75% |
| ProShares Ultra QQQ | 8.29% | 21.45% | 18.61% | 82.79% | 82.79% |

Created with Highcharts 10.3.3Cumulative Active ReturnCumulative Active ReturnMaximum Sharpe Ratio vs. State Street SPDR S&P 500 ETFInvesco QQQ TrustInvesco S&P 500 Momentum ETFSPDR Gold SharesState StreetEngySelSectSPDRETFAug 2016Sep 2016Oct 2016Nov 2016Dec 2016Jan 2017Feb 2017Mar 2017Apr 2017May 2017Jun 2017Jul 2017Aug 2017Sep 2017Oct 2017Nov 2017Dec 2017Jan 2018Feb 2018Mar 2018Apr 2018May 2018Jun 2018Jul 2018Aug 2018Sep 2018Oct 2018Nov 2018Dec 2018Jan 2019Feb 2019Mar 2019Apr 2019May 2019Jun 2019Jul 2019Aug 2019Sep 2019Oct 2019Nov 2019Dec 2019Jan 2020Feb 2020Mar 2020Apr 2020May 2020Jun 2020Jul 2020Aug 2020Sep 2020Oct 2020Nov 2020Dec 2020Jan 2021Feb 2021Mar 2021Apr 2021May 2021Jun 2021Jul 2021Aug 2021Sep 2021Oct 2021Nov 2021Dec 2021Jan 2022Feb 2022Mar 2022Apr 2022May 2022Jun 2022Jul 2022Aug 2022Sep 2022Oct 2022Nov 2022Dec 2022Jan 2023Feb 2023Mar 2023Apr 2023May 2023Jun 2023Jul 2023Aug 2023Sep 2023Oct 2023Nov 2023Dec 2023Jan 2024Feb 2024Mar 2024Apr 2024May 2024Jun 2024Jul 2024Aug 2024Sep 2024Oct 2024Nov 2024Dec 2024Jan 2025Feb 2025Mar 2025Apr 2025May 2025Jun 2025Jul 2025Aug 2025Sep 2025Oct 2025Nov 2025Dec 2025Jan 2026Feb 2026Mar 2026Apr 2026May 2026Jun 2026Jul 2026\-100.0%0.0%100.0%200.0%

Cumulative Active Return - Maximum Sharpe Ratio vs. State Street SPDR S&P 500 ETF

| Asset | 1-year | 3-year | 5-year | 10-year | Full |
| --- | --- | --- | --- | --- | --- |
| Invesco QQQ Trust | 2.99% | 8.96% | 9.34% | 54.43% | 54.43% |
| Invesco S&P 500 Momentum ETF | 11.06% | 81.82% | 63.38% | 77.26% | 77.26% |
| SPDR Gold Shares | 7.33% | 32.93% | 36.13% | \-26.24% | \-26.24% |
| State StreetEngySelSectSPDRETF | 4.52% | \-0.81% | 13.35% | \-1.73% | \-1.73% |

#### Rolling Active Return

Created with Highcharts 10.3.3Active ReturnTracking ErrorRolling Active Return and Risk (36 months)Provided Portfolio vs. State Street SPDR S&P 500 ETFActive ReturnTracking ErrorJul 2019Jan 2020Jul 2020Jan 2021Jul 2021Jan 2022Jul 2022Jan 2023Jul 2023Jan 2024Jul 2024Jan 2025Jul 2025Jan 2026Jul 2026\-10.0%\-5.0%0.0%5.0%10.0%15.0%20.0%5.6%6.4%7.2%8.0%8.8%9.6%10.4%

Created with Highcharts 10.3.3Active ReturnTracking ErrorRolling Active Return and Risk (36 months)Maximum Sharpe Ratio vs. State Street SPDR S&P 500 ETFActive ReturnTracking ErrorJul 2019Jan 2020Jul 2020Jan 2021Jul 2021Jan 2022Jul 2022Jan 2023Jul 2023Jan 2024Jul 2024Jan 2025Jul 2025Jan 2026Jul 2026\-8.0%\-4.0%0.0%4.0%8.0%12.0%16.0%4.8%5.4%6.0%6.6%7.2%7.8%8.4%

#### Up vs. Down Market Performance

##### Provided Portfolio vs. State Street SPDR S&P 500 ETF

Up vs. Down Market Performance - Provided Portfolio vs. State Street SPDR S&P 500 ETF

| Market Type | Occurrences | Average Active Return |
| --- | --- | --- |
| Above Benchmark | Below Benchmark | Total | % Above Benchmark | Above Benchmark | Below Benchmark | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Up Market | 52 | 33 | 85 | 61% | 2.06% | \-2.00% | 0.49% |
| Down Market | 15 | 20 | 35 | 43% | 2.03% | \-1.48% | 0.02% |
| Total | 67 | 53 | 120 | 56% | 2.06% | \-1.81% | 0.35% |

Created with Highcharts 10.3.3Benchmark ReturnReturnReturn vs. BenchmarkProvided Portfolio vs. State Street SPDR S&P 500 ETFProvided PortfolioState Street SPDR S&P 500 ETF\-9.2%\-5.8%\-4.1%\-2.5%\-1.4%\-0.6%0.1%0.5%1.2%1.7%2.0%2.3%2.6%3.2%3.6%4.1%5.0%5.8%7.0%10.1%\-12.0%\-10.0%\-8.0%\-6.0%\-4.0%\-2.0%0.0%2.0%4.0%6.0%8.0%10.0%12.0%14.0%

##### Maximum Sharpe Ratio vs. State Street SPDR S&P 500 ETF

Up vs. Down Market Performance - Maximum Sharpe Ratio vs. State Street SPDR S&P 500 ETF

| Market Type | Occurrences | Average Active Return |
| --- | --- | --- |
| Above Benchmark | Below Benchmark | Total | % Above Benchmark | Above Benchmark | Below Benchmark | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Up Market | 36 | 49 | 85 | 42% | 0.99% | \-1.49% | \-0.44% |
| Down Market | 29 | 6 | 35 | 83% | 2.11% | \-0.70% | 1.63% |
| Total | 65 | 55 | 120 | 54% | 1.49% | \-1.40% | 0.17% |

Created with Highcharts 10.3.3Benchmark ReturnReturnReturn vs. BenchmarkMaximum Sharpe Ratio vs. State Street SPDR S&P 500 ETFMaximum Sharpe RatioState Street SPDR S&P 500 ETF\-9.2%\-5.8%\-4.1%\-2.5%\-1.4%\-0.6%0.1%0.5%1.2%1.7%2.0%2.3%2.6%3.2%3.6%4.1%5.0%5.8%7.0%10.1%\-12.0%\-10.0%\-8.0%\-6.0%\-4.0%\-2.0%0.0%2.0%4.0%6.0%8.0%10.0%12.0%

#### Risk and Return Metrics

Portfolio return and risk metrics

| Metric | Provided Portfolio | Maximum Sharpe Ratio | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- |
| Arithmetic Mean (monthly) | 1.62% | 1.43% | 1.27% |
| Arithmetic Mean (annualized) | 21.25% | 18.63% | 16.32% |
| Geometric Mean (monthly) | 1.47% | 1.36% | 1.17% |
| Geometric Mean (annualized) | 19.21% | 17.65% | 14.99% |
| Standard Deviation (monthly) | 5.40% | 3.78% | 4.42% |
| Standard Deviation (annualized) | 18.71% | 13.10% | 15.32% |
| Downside Deviation (monthly) | 3.08% | 2.05% | 2.72% |
| Maximum Drawdown | \-24.58% | \-18.28% | \-23.93% |
| Benchmark Correlation | 0.90 | 0.90 | 1.00 |
| Beta(\*) | 1.10 | 0.77 | 1.00 |
| Alpha (annualized) | 2.74% | 5.48% | 0.00% |
| R2 | 80.57% | 81.22% | 100.00% |
| Sharpe Ratio | 0.91 | 1.14 | 0.84 |
| Sortino Ratio | 1.56 | 2.02 | 1.32 |
| Treynor Ratio (%) | 15.56 | 19.27 | 12.86 |
| Calmar Ratio | 3.01 | 4.74 | 2.31 |
| Modigliani–Modigliani Measure | 16.34% | 19.79% | 15.22% |
| Active Return | 4.22% | 2.66% | N/A |
| Tracking Error | 8.38% | 6.68% | N/A |
| Information Ratio | 0.50 | 0.40 | N/A |
| Skewness | \-0.12 | \-0.16 | \-0.42 |
| Excess Kurtosis | 0.71 | 0.13 | 0.63 |
| Historical Value-at-Risk (5%) | 7.27% | 5.78% | 6.96% |
| Analytical Value-at-Risk (5%) | 7.23% | 4.76% | 6.01% |
| Conditional Value-at-Risk (5%) | 10.41% | 6.74% | 9.24% |
| Upside Capture Ratio (%) | 115.95 | 84.99 | 100.00 |
| Downside Capture Ratio (%) | 100.32 | 65.68 | 100.00 |
| Safe Withdrawal Rate | 16.24% | 15.70% | 15.91% |
| Perpetual Withdrawal Rate | 13.32% | 12.17% | 10.14% |
| Positive Periods | 80 out of 120 (66.67%) | 83 out of 120 (69.17%) | 85 out of 120 (70.83%) |
| Gain/Loss Ratio | 1.09 | 1.15 | 0.85 |
| \* State Street SPDR S&P 500 ETF is used as the benchmark for calculations. Value-at-risk metrics are monthly values. |

#### Annual Returns

Annual returns for the configured portfolios

| Year | Inflation | Provided Portfolio | Maximum Sharpe Ratio | State Street SPDR S&P 500 ETF | Invesco QQQ Trust (QQQ) | Invesco S&P 500 Momentum ETF (SPMO) | VanEck Gold Miners ETF (GDX) | iShares Silver Trust (SLV) | iShares Asia 50 ETF (AIA) | State StreetEngySelSectSPDRETF (XLE) | Invesco Dorsey Wright Technology MomtETF (PTF) | ProShares Ultra QQQ (QLD) | SPDR Gold Shares (GLD) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Return | Balance | Return | Balance | Return | Balance |
| --- | --- | --- | --- | --- | --- |
| 2026 | 3.04% | 18.65% | $57,949 | 12.27% | $50,793 | 10.13% | $40,420 | 12.26% | 21.06% | \-13.61% | \-18.72% | 37.35% | 35.01% | 28.31% | 18.94% | \-6.25% |
| 2025 | 2.68% | 44.10% | $48,839 | 35.11% | $45,243 | 17.72% | $36,702 | 20.77% | 26.57% | 154.71% | 144.66% | 47.79% | 7.88% | 5.67% | 30.36% | 63.68% |
| 2024 | 2.89% | 26.12% | $33,893 | 33.46% | $33,486 | 24.89% | $31,178 | 25.58% | 45.81% | 10.63% | 20.89% | 20.26% | 5.52% | 43.65% | 42.81% | 26.66% |
| 2023 | 3.35% | 27.19% | $26,874 | 24.05% | $25,091 | 26.19% | $24,966 | 54.85% | 17.55% | 9.96% | \-1.09% | 4.90% | \-0.64% | 33.73% | 117.13% | 12.69% |
| 2022 | 6.45% | \-14.75% | $21,128 | \-10.38% | $20,227 | \-18.17% | $19,784 | \-32.58% | \-10.46% | \-8.98% | 2.37% | \-23.76% | 64.17% | \-31.75% | \-60.52% | \-0.77% |
| 2021 | 7.04% | 18.33% | $24,784 | 16.92% | $22,570 | 28.75% | $24,178 | 27.42% | 22.65% | \-9.52% | \-12.45% | \-10.90% | 53.31% | 18.10% | 54.67% | \-4.15% |
| 2020 | 1.36% | 35.33% | $20,946 | 29.48% | $19,305 | 18.37% | $18,780 | 48.62% | 28.28% | 23.66% | 47.30% | 33.74% | \-32.51% | 82.06% | 88.90% | 24.81% |
| 2019 | 2.29% | 33.91% | $15,477 | 26.28% | $14,909 | 31.22% | $15,865 | 38.96% | 25.93% | 39.79% | 14.88% | 22.19% | 11.74% | 46.71% | 81.69% | 17.86% |
| 2018 | 1.91% | \-6.60% | $11,558 | \-1.29% | $11,806 | \-4.56% | $12,090 | \-0.12% | \-0.90% | \-8.79% | \-9.19% | \-14.23% | \-18.21% | 0.02% | \-8.32% | \-1.94% |
| 2017 | 2.11% | 27.10% | $12,375 | 23.04% | $11,961 | 21.70% | $12,667 | 32.66% | 27.75% | 11.97% | 5.82% | 45.00% | \-0.90% | 32.06% | 70.34% | 12.81% |
| 2016 | 0.33% | \-2.64% | $9,736 | \-2.79% | $9,721 | 4.09% | $10,409 | 3.38% | 1.26% | \-31.41% | \-21.91% | \-0.22% | 13.06% | \-0.31% | 5.67% | \-15.02% |
| Annual return for 2016 is from 08/01/2016 to 12/31/2016 and annual return for 2026 is from 01/01/2026 to 07/31/2026 |

Show 123660All entries

*   First
*   Previous
*   Next
*   Last

#### Monthly Returns

Monthly returns for the configured portfolios

| Year | Month | Provided Portfolio | Maximum Sharpe Ratio | State Street SPDR S&P 500 ETF | Invesco QQQ Trust (QQQ) | Invesco S&P 500 Momentum ETF (SPMO) | VanEck Gold Miners ETF (GDX) | iShares Silver Trust (SLV) | iShares Asia 50 ETF (AIA) | State StreetEngySelSectSPDRETF (XLE) | Invesco Dorsey Wright Technology MomtETF (PTF) | ProShares Ultra QQQ (QLD) | SPDR Gold Shares (GLD) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Return | Balance | Return | Balance | Return | Balance |
| --- | --- | --- | --- | --- | --- |
| 2026 | 7 | \-6.00% | $57,949 | \-5.26% | $50,793 | 0.03% | $40,420 | \-6.57% | \-10.96% | \-1.79% | \-2.08% | \-5.79% | 12.13% | \-28.00% | \-13.53% | 0.86% |
| 2026 | 6 | \-3.40% | $61,648 | \-0.75% | $53,614 | \-1.03% | $40,406 | \-0.15% | 7.43% | \-15.69% | \-21.75% | \-0.12% | \-4.98% | 5.62% | \-1.66% | \-11.68% |
| 2026 | 5 | 8.81% | $63,817 | 6.99% | $54,017 | 5.26% | $40,827 | 10.57% | 12.56% | 1.36% | 2.51% | 14.43% | \-5.63% | 15.85% | 21.48% | \-1.54% |
| 2026 | 4 | 12.85% | $58,650 | 11.15% | $50,488 | 10.51% | $38,786 | 15.69% | 19.34% | \-3.79% | \-2.17% | 17.17% | \-2.63% | 29.05% | 32.87% | \-1.54% |
| 2026 | 3 | \-7.24% | $51,972 | \-6.43% | $45,422 | \-4.93% | $35,099 | \-4.84% | \-5.90% | \-20.78% | \-19.83% | \-10.06% | 10.26% | \-6.21% | \-10.26% | \-11.05% |
| 2026 | 2 | 6.02% | $56,026 | 2.35% | $48,544 | \-0.86% | $36,921 | \-2.34% | \-0.33% | 22.97% | 12.66% | 7.92% | 9.54% | 8.61% | \-5.19% | 8.72% |
| 2026 | 1 | 8.20% | $52,844 | 4.83% | $47,430 | 1.47% | $37,243 | 1.23% | 0.46% | 9.83% | 17.11% | 12.15% | 14.18% | 10.79% | 1.85% | 12.27% |
| 2025 | 12 | 2.87% | $48,839 | 0.30% | $45,243 | 0.08% | $36,702 | \-0.67% | \-0.43% | 3.78% | 25.80% | 4.12% | \-0.30% | \-2.94% | \-1.92% | 2.17% |
| 2025 | 11 | 1.77% | $47,478 | 0.82% | $45,108 | 0.19% | $36,673 | \-1.56% | \-1.30% | 15.50% | 16.36% | \-3.71% | 2.63% | \-4.21% | \-3.92% | 5.37% |
| 2025 | 10 | 3.21% | $46,652 | 2.40% | $44,741 | 2.38% | $36,602 | 4.78% | 0.53% | \-5.68% | 3.87% | 4.62% | \-1.35% | 9.96% | 8.95% | 3.56% |
| 2025 | 9 | 9.03% | $45,202 | 6.50% | $43,694 | 3.56% | $35,750 | 5.38% | 4.10% | 20.94% | 17.08% | 11.48% | \-0.32% | 10.26% | 10.48% | 11.76% |
| 2025 | 8 | 3.99% | $41,457 | 2.18% | $41,026 | 2.05% | $34,521 | 0.95% | 0.68% | 22.33% | 8.61% | 2.05% | 3.65% | \-3.35% | 1.18% | 4.99% |

Show 123660All entries

*   First
*   Previous
*   [Next](#)
*   [Last](#)

#### Drawdowns

Created with Highcharts 10.3.3YearDrawdownProvided PortfolioMaximum Sharpe RatioState Street SPDR S&P 500 ETF2017201820192020202120222023202420252026\-30.0%\-25.0%\-20.0%\-15.0%\-10.0%\-5.0%0.0%

#### Historical Market Stress Periods

Drawdowns for Historical Market Stress Periods

| Stress Period | Start | End | Provided Portfolio | Maximum Sharpe Ratio | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- | --- | --- |
| COVID-19 Start | Jan 2020 | Mar 2020 | \-22.17% | \-12.30% | \-19.43% |

#### Drawdowns for Provided Portfolio

Drawdowns for Provided Portfolio (worst 10)

| Rank | Start | End | Length | Recovery By | Recovery Time | Underwater Period | Drawdown |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Apr 2022 | Sep 2022 | 6 months | Jun 2023 | 9 months | 1 year 3 months | \-24.58% |
| 2 | Jan 2020 | Mar 2020 | 3 months | Jun 2020 | 3 months | 6 months | \-22.17% |
| 3 | Oct 2018 | Dec 2018 | 3 months | Apr 2019 | 4 months | 7 months | \-13.78% |
| 4 | Aug 2023 | Oct 2023 | 3 months | Dec 2023 | 2 months | 5 months | \-10.01% |
| 5 | Jun 2026 | Jul 2026 | 2 months |  |  |  | \-9.20% |
| 6 | Sep 2020 | Oct 2020 | 2 months | Nov 2020 | 1 month | 3 months | \-9.18% |
| 7 | Mar 2026 | Mar 2026 | 1 month | Apr 2026 | 1 month | 2 months | \-7.24% |
| 8 | May 2019 | May 2019 | 1 month | Jun 2019 | 1 month | 2 months | \-7.03% |
| 9 | Feb 2018 | Mar 2018 | 2 months | Aug 2018 | 5 months | 7 months | \-5.96% |
| 10 | Jul 2021 | Sep 2021 | 3 months | Oct 2021 | 1 month | 4 months | \-4.63% |
| Worst 10 drawdowns included above |

#### Drawdowns for Maximum Sharpe Ratio

Drawdowns for Maximum Sharpe Ratio (worst 10)

| Rank | Start | End | Length | Recovery By | Recovery Time | Underwater Period | Drawdown |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Jan 2022 | Sep 2022 | 9 months | Jul 2023 | 10 months | 1 year 7 months | \-18.28% |
| 2 | Feb 2020 | Mar 2020 | 2 months | May 2020 | 2 months | 4 months | \-12.30% |
| 3 | Oct 2018 | Dec 2018 | 3 months | Mar 2019 | 3 months | 6 months | \-9.95% |
| 4 | Sep 2020 | Oct 2020 | 2 months | Dec 2020 | 2 months | 4 months | \-6.73% |
| 5 | Mar 2026 | Mar 2026 | 1 month | Apr 2026 | 1 month | 2 months | \-6.43% |
| 6 | Jun 2026 | Jul 2026 | 2 months |  |  |  | \-5.97% |
| 7 | Oct 2016 | Nov 2016 | 2 months | Feb 2017 | 3 months | 5 months | \-4.34% |
| 8 | Feb 2018 | Mar 2018 | 2 months | Jul 2018 | 4 months | 6 months | \-3.95% |
| 9 | Sep 2021 | Sep 2021 | 1 month | Oct 2021 | 1 month | 2 months | \-3.85% |
| 10 | Sep 2023 | Sep 2023 | 1 month | Nov 2023 | 2 months | 3 months | \-3.07% |
| Worst 10 drawdowns included above |

#### Drawdowns for State Street SPDR S&P 500 ETF

Drawdowns for State Street SPDR S&P 500 ETF (worst 10)

| Rank | Start | End | Length | Recovery By | Recovery Time | Underwater Period | Drawdown |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Jan 2022 | Sep 2022 | 9 months | Dec 2023 | 1 year 3 months | 2 years | \-23.93% |
| 2 | Jan 2020 | Mar 2020 | 3 months | Jul 2020 | 4 months | 7 months | \-19.43% |
| 3 | Oct 2018 | Dec 2018 | 3 months | Apr 2019 | 4 months | 7 months | \-13.52% |
| 4 | Feb 2025 | Apr 2025 | 3 months | Jun 2025 | 2 months | 5 months | \-7.58% |
| 5 | May 2019 | May 2019 | 1 month | Jun 2019 | 1 month | 2 months | \-6.38% |
| 6 | Feb 2018 | Mar 2018 | 2 months | Jul 2018 | 4 months | 6 months | \-6.28% |
| 7 | Sep 2020 | Oct 2020 | 2 months | Nov 2020 | 1 month | 3 months | \-6.14% |
| 8 | Feb 2026 | Mar 2026 | 2 months | Apr 2026 | 1 month | 3 months | \-5.76% |
| 9 | Sep 2021 | Sep 2021 | 1 month | Oct 2021 | 1 month | 2 months | \-4.66% |
| 10 | Apr 2024 | Apr 2024 | 1 month | May 2024 | 1 month | 2 months | \-4.03% |
| Worst 10 drawdowns included above |

#### Portfolio Assets

Performance statistics for portfolio components

| Ticker | Name | CAGR | Stdev | Best Year | Worst Year | Max Drawdown | Sharpe Ratio | Sortino Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QQQ | Invesco QQQ Trust | 20.41% | 18.97% | 54.85% | \-32.58% | \-32.58% | 0.96 | 1.62 |
| SPMO | Invesco S&P 500 Momentum ETF | 19.57% | 17.95% | 45.81% | \-10.46% | \-21.35% | 0.96 | 1.71 |
| GDX | VanEck Gold Miners ETF | 10.32% | 33.94% | 154.71% | \-31.41% | \-43.31% | 0.38 | 0.66 |
| SLV | iShares Silver Trust | 10.47% | 29.89% | 144.66% | \-21.91% | \-38.39% | 0.40 | 0.68 |
| AIA | iShares Asia 50 ETF | 13.43% | 21.68% | 47.79% | \-23.76% | \-50.34% | 0.58 | 0.99 |
| XLE | State StreetEngySelSectSPDRETF | 10.26% | 30.01% | 64.17% | \-32.51% | \-58.14% | 0.40 | 0.63 |
| PTF | Invesco Dorsey Wright Technology MomtETF | 22.13% | 28.89% | 82.06% | \-31.75% | \-38.60% | 0.76 | 1.24 |
| QLD | ProShares Ultra QQQ | 32.46% | 38.81% | 117.13% | \-60.52% | \-60.52% | 0.86 | 1.46 |
| GLD | SPDR Gold Shares | 11.16% | 15.10% | 63.68% | \-15.02% | \-23.85% | 0.63 | 1.08 |

#### Portfolio Asset Performance

Performance of portfolio assets

| Name | Total Return | Annualized Return | Expense Ratio |
| --- | --- | --- | --- |
| 3 Month | Year To Date | 1 year | 3 year | 5 year | 10 year | Net | Gross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Invesco QQQ Trust | 3.15% | 12.26% | 22.35% | 22.19% | 14.22% | 20.41% | 0.18% | 0.18% |
| Invesco S&P 500 Momentum ETF | 7.67% | 21.06% | 25.36% | 37.32% | 20.20% | 19.57% | 0.13% | 0.13% |
| VanEck Gold Miners ETF | \-16.07% | \-13.61% | 44.50% | 34.67% | 17.86% | 10.32% | 0.51% | 0.51% |
| iShares Silver Trust | \-21.45% | \-18.72% | 57.14% | 32.15% | 17.25% | 10.47% | 0.50% | 0.50% |
| iShares Asia 50 ETF | 7.68% | 37.35% | 63.89% | 31.51% | 12.44% | 13.43% | 0.50% | 0.50% |
| State StreetEngySelSectSPDRETF | 0.54% | 35.01% | 40.79% | 14.42% | 23.64% | 10.26% | 0.08% | 0.08% |
| Invesco Dorsey Wright Technology MomtETF | \-11.90% | 28.31% | 39.78% | 23.93% | 14.36% | 22.13% | 0.60% | 0.68% |
| ProShares Ultra QQQ | 3.30% | 18.94% | 36.51% | 34.63% | 17.39% | 32.46% | 0.95% | 0.98% |
| SPDR Gold Shares | \-12.30% | \-6.25% | 22.64% | 26.77% | 16.95% | 11.16% | 0.40% | 0.40% |
| Trailing returns as of last calendar month ending July 2026 |

#### Monthly Correlations

Correlations for the portfolio assets

| Ticker | Name | QQQ | SPMO | GDX | SLV | AIA | XLE | PTF | QLD | GLD | Provided Portfolio | Maximum Sharpe Ratio | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QQQ | Invesco QQQ Trust | 1.00 | 0.83 | 0.24 | 0.26 | 0.58 | 0.29 | 0.83 | 1.00 | 0.12 | 0.87 | 0.89 | 0.91 |
| SPMO | Invesco S&P 500 Momentum ETF | 0.83 | 1.00 | 0.17 | 0.20 | 0.48 | 0.33 | 0.76 | 0.83 | 0.03 | 0.78 | 0.90 | 0.85 |
| GDX | VanEck Gold Miners ETF | 0.24 | 0.17 | 1.00 | 0.73 | 0.37 | 0.20 | 0.14 | 0.24 | 0.84 | 0.55 | 0.50 | 0.30 |
| SLV | iShares Silver Trust | 0.26 | 0.20 | 0.73 | 1.00 | 0.40 | 0.14 | 0.22 | 0.27 | 0.76 | 0.56 | 0.48 | 0.29 |
| AIA | iShares Asia 50 ETF | 0.58 | 0.48 | 0.37 | 0.40 | 1.00 | 0.26 | 0.54 | 0.59 | 0.35 | 0.74 | 0.63 | 0.57 |
| XLE | State StreetEngySelSectSPDRETF | 0.29 | 0.33 | 0.20 | 0.14 | 0.26 | 1.00 | 0.24 | 0.31 | \-0.03 | 0.53 | 0.38 | 0.53 |
| PTF | Invesco Dorsey Wright Technology MomtETF | 0.83 | 0.76 | 0.14 | 0.22 | 0.54 | 0.24 | 1.00 | 0.83 | 0.06 | 0.78 | 0.77 | 0.74 |
| QLD | ProShares Ultra QQQ | 1.00 | 0.83 | 0.24 | 0.27 | 0.59 | 0.31 | 0.83 | 1.00 | 0.12 | 0.88 | 0.89 | 0.92 |
| GLD | SPDR Gold Shares | 0.12 | 0.03 | 0.84 | 0.76 | 0.35 | \-0.03 | 0.06 | 0.12 | 1.00 | 0.39 | 0.40 | 0.13 |

#### Portfolio Return Decomposition

Portfolio return decomposition

| Ticker | Name | Provided Portfolio | Maximum Sharpe Ratio |
| --- | --- | --- | --- |
| QQQ | Invesco QQQ Trust | $8,770 | $10,466 |
| SPMO | Invesco S&P 500 Momentum ETF | $4,913 | $19,062 |
| GDX | VanEck Gold Miners ETF | $4,159 |  |
| SLV | iShares Silver Trust | $4,165 |  |
| AIA | iShares Asia 50 ETF | $6,554 |  |
| XLE | State StreetEngySelSectSPDRETF | $6,388 | $1,851 |
| PTF | Invesco Dorsey Wright Technology MomtETF | $5,499 |  |
| QLD | ProShares Ultra QQQ | $7,502 |  |
| GLD | SPDR Gold Shares |  | $9,415 |
| Return attribution decomposes portfolio gains into its constituent parts and identifies the contribution to returns by each of the assets. |

#### Portfolio Risk Decomposition

Portfolio risk decomposition

| Ticker | Name | Provided Portfolio | Maximum Sharpe Ratio |
| --- | --- | --- | --- |
| QQQ | Invesco QQQ Trust | 17.72% | 31.84% |
| SPMO | Invesco S&P 500 Momentum ETF | 7.47% | 50.15% |
| GDX | VanEck Gold Miners ETF | 9.96% |  |
| SLV | iShares Silver Trust | 8.90% |  |
| AIA | iShares Asia 50 ETF | 12.80% |  |
| XLE | State StreetEngySelSectSPDRETF | 12.87% | 4.07% |
| PTF | Invesco Dorsey Wright Technology MomtETF | 12.03% |  |
| QLD | ProShares Ultra QQQ | 18.25% |  |
| GLD | SPDR Gold Shares |  | 13.94% |
| Risk attribution decomposes portfolio risk into its constituent parts and identifies the contribution to overall volatility by each of the assets. |

#### Annual Asset Returns

Created with Highcharts 10.3.3YearReturnAnnual Returns of Portfolio AssetsInvesco QQQ TrustInvesco S&P 500 Momentum ETFVanEck Gold Miners ETFSPDR Gold SharesiShares Silver TrustiShares Asia 50 ETFState StreetEngySelSectSPDRETFInvesco Dorsey Wright Technology MomtETFProShares Ultra QQQ20162017201820192020202120222023202420252026\-100.0%0.0%100.0%200.0%

#### Rolling Returns

Rolling returns summary

| Roll Period | Provided Portfolio | Maximum Sharpe Ratio | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- |
| Average | High | Low | Average | High | Low | Average | High | Low |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 year | 21.22% | 81.63% | \-19.44% | 19.33% | 46.78% | \-12.33% | 15.78% | 56.25% | \-18.17% |
| 3 years | 17.83% | 39.07% | 4.13% | 17.17% | 35.98% | 7.03% | 14.30% | 25.99% | 5.05% |
| 5 years | 17.07% | 23.40% | 10.19% | 16.17% | 21.55% | 10.16% | 14.09% | 18.81% | 9.16% |
| 7 years | 17.61% | 25.91% | 13.23% | 16.94% | 22.58% | 12.02% | 14.20% | 17.28% | 12.09% |

#### Annualized Rolling Return - 3 Years

Created with Highcharts 10.3.3YearAnnualized ReturnProvided PortfolioMaximum Sharpe RatioState Street SPDR S&P 500 ETFJan 2020Jul 2020Jan 2021Jul 2021Jan 2022Jul 2022Jan 2023Jul 2023Jan 2024Jul 2024Jan 2025Jul 2025Jan 2026Jul 20260.0%5.0%10.0%15.0%20.0%25.0%30.0%35.0%40.0%45.0%

#### Annualized Rolling Return - 5 Years

Created with Highcharts 10.3.3YearAnnualized ReturnProvided PortfolioMaximum Sharpe RatioState Street SPDR S&P 500 ETFJan 2022Jan 2023Jan 2024Jan 2025Jan 2026Jul 2022Jul 2023Jul 2024Jul 2025Jul 20267.5%10.0%12.5%15.0%17.5%20.0%22.5%25.0%

## Notes and Disclosures

*   IMPORTANT: The projections or other information generated by Portfolio Visualizer regarding the likelihood of various investment outcomes are hypothetical in nature, do not reflect actual investment results and are not guarantees of future results. Results may vary with each use and over time.
*   The results do not constitute investment advice or recommendation, are provided solely for informational purposes, and are not an offer to buy or sell any securities. All use is subject to [terms of service](https://www.portfoliovisualizer.com/terms-of-service).
*   Investing involves risk, including possible loss of principal. Past performance is not a guarantee of future results.
*   Asset allocation and diversification strategies do not guarantee a profit or protect against a loss.
*   Hypothetical returns do not reflect trading costs, transaction fees, commissions, or actual taxes due on investment returns.
*   The results are based on information from a variety of sources we consider reliable, but we do not represent that the information is accurate or complete.
*   Refer to the related documentation sections for more details on [terms and definitions](https://www.portfoliovisualizer.com/faq#definitions), [methodology](https://www.portfoliovisualizer.com/faq#methodology), and [data sources](https://www.portfoliovisualizer.com/faq#marketData).
*   Portfolio optimization is a process of choosing the proportions of various assets to be held in a portfolio in such a way as to make the portfolio better than any other combination according to the selected objective function such as maximizing risk-adjusted return. Portfolio optimization determines target weights for portfolio assets based on mathematical models that can use either historical or forecasted data as inputs. Optimization results are not guarantees of future performance.
*   The results are based on the total return of assets and assume that all received dividends and distributions are reinvested.
*   Compound annualized growth rate (CAGR) is the annualized geometric mean return of the portfolio. It is calculated from the portfolio start and end balance and is thus impacted by any cashflows.
*   The time-weighted rate of return (TWRR) is a measure of the compound rate of growth in a portfolio. This is calculated from the holding period returns (e.g. monthly returns), and TWRR will thus not be impacted by cashflows. If there are no external cashflows, TWRR will equal CAGR.
*   The money-weighted rate of return (MWRR) is the internal rate of return (IRR) taking into account cashflows. This is the discount rate at which the present value of cash inflows equals the present value of cash outflows.
*   Standard deviation (Stdev) is used to measure the dispersion of returns around the mean and is often used as a measure of risk. A higher standard deviation implies greater the dispersion of data points around the mean.
*   Sharpe Ratio is a measure of risk-adjusted performance of the portfolio, and it is calculated by dividing the mean monthly excess return of the portfolio over the risk-free rate by the standard deviation of excess return, and the displayed value is annualized.
*   Sortino Ratio is a measure of risk-adjusted return which is a modification of the Sharpe Ratio. While the latter is the ratio of average returns in excess of a risk-free rate divided by the standard deviation of those excess returns, the Sortino Ratio has the same denominator divided by the standard deviation of returns below the risk-free rate.
*   Treynor Ratio is a measure of risk-adjusted performance of the portfolio. It is similar to the Sharpe Ratio, but it uses portfolio beta (systematic risk) as the risk metric in the denominator.
*   Calmar Ratio is a measure of risk-adjusted performance of the portfolio. It is calculated as the annualized return over the past 36 months divided by the maximum drawdown over the past 36 months based on monthly returns.
*   Downside deviation measures the downside volatility of the portfolio returns unlike standard deviation, which includes both upside and downside deviations. Downside deviation is calculated based on negative returns that hurt the portfolio performance.
*   Risk-free returns are calculated based on U.S. 3-Month Treasury Bill Rate.
*   Inflation is calculated based on U.S. Consumer Price Index.
*   Correlation measures to what degree the returns of the two assets move in relation to each other. Correlation coefficient is a numerical value between -1 and +1. If one variable goes up by a certain amount, the correlation coefficient indicates which way the other variable moves and by how much. Asset correlations are calculated based on monthly returns.
*   Skewness is a measure of the asymmetry of the probability distribution or returns from a normal Gaussian distribution shape about its mean. Negative skewness is associated with the left (typically negative returns) tail of the distribution extending further than the right tail; and positive skewness is associated with the right (typically positive returns) tail of the distribution extending further than the left tail.
*   Excess kurtosis is a measure of whether a data distribution is peaked or flat relative to a normal distribution. Distributions with high kurtosis tend to have a distinct peak near the mean, decline rather rapidly, and have heavy or fat tails.
*   A drawdown refers to the decline in value of a single investment or an investment portfolio from a relative peak value to a relative trough. A maximum drawdown (Max Drawdown) is the maximum observed loss from a peak to a trough of a portfolio before a new peak is attained. Drawdown values are calculated based on monthly returns.
*   Value at Risk (VaR) measures the scale of loss at a given confidence level. For example, if the 95% confidence one-month VaR is 3%, there is 95% confidence that over the next month the portfolio will not lose more than 3%. Value at Risk can be calculated directly based on historical returns based on a given percentile or analytically based on the mean and standard deviation of the returns.
*   Conditional Value at Risk (CVaR) measures the scale of the expected loss once the specific Value at Risk (VaR) breakpoint has been breached, i.e., it calculates the average tail loss by taking a weighted average between the value at risk and losses exceeding the value at risk.
*   Beta is a measure of systematic risk and measures the volatility of a particular investment relative to the market or its benchmark. Alpha measures the active return of the investment compared to the market benchmark return. R-squared is the percentage of a portfolio's movements that can be explained by movements in the selected benchmark index.
*   Active return is the investment return minus the return of its benchmark. For periods longer than 12 months this is displayed as annualized value, i.e., annualized investment return minus annualized benchmark return.
*   Tracking error, also known as active risk, is the standard deviation of active return. This is displayed as annualized value based on the standard deviation of monthly active returns.
*   Information ratio is the active return divided by the tracking error. It measures whether the investment outperformed its benchmark consistently.
*   Gain/Loss ratio is a measure of downside risk, and it is calculated as the average positive return in up periods divided by the average negative return in down periods.
*   Upside Capture Ratio measures how well the fund performed relative to the benchmark when the market was up, and Downside Capture Ratio measures how well the fund performed relative to the benchmark when the market was down. An upside capture ratio greater than 100 would indicate that the fund outperformed its benchmark when the market was up, and a downside capture ratio below 100 would indicate that the fund lost less than its benchmark when the market was down. To calculate upside capture ratio a new series from the portfolio returns is constructed by dropping all time periods where the benchmark return is less than equal to zero. The up capture is then the quotient of the annualized return of the resulting manager series, divided by the annualized return of the resulting benchmark series. The downside capture ratio is calculated analogously.
*   All risk measures for the portfolio and portfolio assets are calculated based on monthly returns.
*   Allocation constraints are only applied to the optimized portfolio, not to compared allocations and benchmarks.
*   The annual results for 2016 are based on full calendar months from August to December.
*   The annual results for 2026 are based on full calendar months from January to July.
*   The optimization results assume monthly rebalancing of portfolio assets to match the specified allocation.

© 2026 SRL Global

[Contact](contact)

[Pricing](pricing)

[Affiliates](affiliates)

[Terms of Service](terms-of-service)

[Privacy Policy](privacy-policy)
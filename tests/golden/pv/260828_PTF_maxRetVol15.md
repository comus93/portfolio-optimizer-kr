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

Portfolio optimization results with the goal to maximize return subject to 15.00% targeted annual volatility. The possible range of expected annual portfolio returns for the given period taking into account the specified constraints is 16.23% to 26.24%. Refer to the efficient frontier section for additional details.

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

Created with Highcharts 10.3.320.0 %10.0 %10.0 %10.0 %15.0 %15.0 %10.0 %10.0 %Invesco QQQ TrustInvesco S&P 500 Momentum ETFVanEck Gold Miners ETFiShares Silver TrustiShares Asia 50 ETFState StreetEngySelSectSPDRETFInvesco Dorsey Wright Technology MomtETFProShares Ultra QQQ

#### Maximum Return at 15.00% Volatility

| Ticker | Name | Allocation |
| --- | --- | --- |
| QQQ | Invesco QQQ Trust | 14.19% |
| SPMO | Invesco S&P 500 Momentum ETF | 44.30% |
| GLD | SPDR Gold Shares | 30.00% |
| XLE | State StreetEngySelSectSPDRETF | 2.20% |
| QLD | ProShares Ultra QQQ | 9.31% |
| Save Portfolio |

Created with Highcharts 10.3.314.2 %44.3 %30.0 %9.3 %Invesco QQQ TrustInvesco S&P 500 Momentum ETFSPDR Gold SharesState StreetEngySelSectSPDRETFProShares Ultra QQQ

#### Performance Summary

Portfolio performance statistics

| Metric | Provided Portfolio | Maximum Return at 15.00% Volatility | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- |
| Start Balance | $10,000 | $10,000 | $10,000 |
| End Balance | $57,949 | $57,769 | $40,420 |
| Annualized Return (CAGR) | 19.21% | 19.17% | 14.99% |
| Expected Return | 19.42% | 18.76% | 15.22% |
| Standard Deviation | 18.71% | 14.89% | 15.32% |
| Best Year | 44.10% | 36.88% | 31.22% |
| Worst Year | \-14.75% | \-15.25% | \-18.17% |
| Maximum Drawdown | \-24.58% | \-22.44% | \-23.93% |
| Sharpe Ratio (ex-ante) | 0.91 | 1.10 | 0.84 |
| Sharpe Ratio (ex-post) | 0.91 | 1.10 | 0.84 |
| Sortino Ratio | 1.56 | 1.95 | 1.32 |
| Active Return | 4.22% | 4.18% | N/A |
| Tracking Error | 8.38% | 6.63% | N/A |
| Information Ratio | 0.50 | 0.63 | N/A |
| Results based on historical returns. Expected return is the annualized monthly arithmetic mean return. |

#### Portfolio Growth

Created with Highcharts 10.3.3YearPortfolio Balance ($)Provided PortfolioMaximum Return at 15.00% VolatilityState Street SPDR S&P 500 ETF2017201820192020202120222023202420252026$0$10,000$20,000$30,000$40,000$50,000$60,000$70,000

 Logarithmic scale     Inflation adjusted

#### Annual Returns

Created with Highcharts 10.3.3YearAnnual ReturnProvided PortfolioMaximum Return at 15.00% VolatilityState Street SPDR S&P 500 ETF20162017201820192020202120222023202420252026\-30.0%\-20.0%\-10.0%0.0%10.0%20.0%30.0%40.0%50.0%

#### Trailing Returns

Trailing Returns

| Name | Total Return | Annualized Return | Annualized Standard Deviation |
| --- | --- | --- | --- |
| 3 Month | Year To Date | 1 year | 3 year | 5 year | 10 year | Full | 3 year | 5 year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Provided Portfolio | \-1.20% | 18.65% | 45.36% | 30.16% | 19.64% | 19.21% | 19.21% | 16.87% | 19.19% |
| Maximum Return at 15.00% Volatility | 0.89% | 12.83% | 27.68% | 32.61% | 19.60% | 19.17% | 19.17% | 14.91% | 16.29% |
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
| 8 | Invesco Dorsey Wright Technology MomtETF | 24.31% | 28.89% | 0.760 | 0.00% | 30.00% |
| 9 | ProShares Ultra QQQ | 35.86% | 38.81% | 0.863 | 0.00% | 30.00% |
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

Created with Highcharts 10.3.3Expected ReturnStandard DeviationEfficient Frontier (Aug 2016 - Jul 2026)Tangency PortfolioProShares Ultra QQQInvesco Dorsey Wright Technology MomtETFState StreetEngySelSectSPDRETFiShares Asia 50 ETFiShares Silver TrustSPDR Gold SharesVanEck Gold Miners ETFInvesco S&P 500 Momentum ETFInvesco QQQ TrustState Street SPDR S&P 500 ETFMaximum Return at 15.00% VolatilityProvided Portfolio10.0%15.0%20.0%25.0%30.0%35.0%40.0%10.0%20.0%30.0%40.0%12.5%15.0%17.5%22.5%25.0%27.5%32.5%35.0%37.5%42.5%

Created with Highcharts 10.3.3Standard DeviationAllocationEfficient Frontier Transition Map (Aug 2016 - Jul 2026)Invesco QQQ TrustInvesco S&P 500 Momentum ETFVanEck Gold Miners ETFSPDR Gold SharesiShares Asia 50 ETFState StreetEngySelSectSPDRETFInvesco Dorsey Wright Technology MomtETFProShares Ultra QQQ14.0%16.0%18.0%20.0%22.0%24.0%26.0%0.0%10.0%20.0%30.0%40.0%50.0%60.0%70.0%80.0%90.0%100.0%

#### Efficient Frontier Portfolios

Efficient Frontier Assets

| # | Invesco QQQ Trust | Invesco S&P 500 Momentum ETF | VanEck Gold Miners ETF | SPDR Gold Shares | iShares Silver Trust | iShares Asia 50 ETF | State StreetEngySelSectSPDRETF | Invesco Dorsey Wright Technology MomtETF | ProShares Ultra QQQ | Expected Return \* | Standard Deviation \* | Sharpe Ratio \* |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 5.69% | 43.10% | 0.00% | 30.00% | 0.00% | 10.42% | 10.80% | 0.00% | 0.00% | 16.23% | 12.74% | 1.089 |
| 2 | 7.58% | 42.96% | 0.00% | 30.00% | 0.00% | 9.10% | 10.36% | 0.00% | 0.00% | 16.33% | 12.74% | 1.096 |
| 3 | 9.47% | 42.82% | 0.00% | 30.00% | 0.00% | 7.78% | 9.93% | 0.00% | 0.00% | 16.43% | 12.75% | 1.103 |
| 4 | 11.35% | 42.69% | 0.00% | 30.00% | 0.00% | 6.46% | 9.50% | 0.00% | 0.00% | 16.53% | 12.77% | 1.110 |
| 5 | 13.24% | 42.55% | 0.00% | 30.00% | 0.00% | 5.14% | 9.06% | 0.00% | 0.00% | 16.63% | 12.80% | 1.115 |
| 6 | 15.13% | 42.41% | 0.00% | 30.00% | 0.00% | 3.83% | 8.63% | 0.00% | 0.00% | 16.73% | 12.83% | 1.120 |
| 7 | 17.02% | 42.27% | 0.00% | 30.00% | 0.00% | 2.51% | 8.20% | 0.00% | 0.00% | 16.83% | 12.87% | 1.125 |
| 8 | 18.91% | 42.14% | 0.00% | 30.00% | 0.00% | 1.19% | 7.77% | 0.00% | 0.00% | 16.93% | 12.92% | 1.128 |
| 9 | 20.83% | 41.94% | 0.00% | 30.00% | 0.00% | 0.00% | 7.23% | 0.00% | 0.00% | 17.04% | 12.97% | 1.131 |
| 10 | 23.08% | 41.22% | 0.00% | 30.00% | 0.00% | 0.00% | 5.70% | 0.00% | 0.00% | 17.14% | 13.04% | 1.133 |
| 11 | 25.33% | 40.49% | 0.00% | 30.00% | 0.00% | 0.00% | 4.17% | 0.00% | 0.00% | 17.24% | 13.13% | 1.134 |
| 12 | 27.58% | 39.77% | 0.00% | 30.00% | 0.00% | 0.00% | 2.65% | 0.00% | 0.00% | 17.34% | 13.23% | 1.132 |
| 13 | 27.40% | 39.84% | 0.00% | 30.00% | 0.00% | 0.00% | 2.26% | 0.00% | 0.50% | 17.44% | 13.35% | 1.130 |
| 14 | 26.38% | 40.18% | 0.00% | 30.00% | 0.00% | 0.00% | 2.25% | 0.00% | 1.18% | 17.54% | 13.46% | 1.128 |
| 15 | 25.37% | 40.52% | 0.00% | 30.00% | 0.00% | 0.00% | 2.25% | 0.00% | 1.86% | 17.64% | 13.58% | 1.125 |
| 16 | 24.35% | 40.87% | 0.00% | 30.00% | 0.00% | 0.00% | 2.24% | 0.00% | 2.54% | 17.74% | 13.70% | 1.123 |
| 17 | 23.34% | 41.21% | 0.00% | 30.00% | 0.00% | 0.00% | 2.24% | 0.00% | 3.21% | 17.85% | 13.82% | 1.121 |
| 18 | 22.32% | 41.55% | 0.00% | 30.00% | 0.00% | 0.00% | 2.23% | 0.00% | 3.89% | 17.95% | 13.94% | 1.118 |
| 19 | 21.30% | 41.90% | 0.00% | 30.00% | 0.00% | 0.00% | 2.23% | 0.00% | 4.57% | 18.05% | 14.06% | 1.116 |
| 20 | 20.29% | 42.24% | 0.00% | 30.00% | 0.00% | 0.00% | 2.23% | 0.00% | 5.25% | 18.15% | 14.17% | 1.114 |
| 21 | 19.27% | 42.58% | 0.00% | 30.00% | 0.00% | 0.00% | 2.22% | 0.00% | 5.92% | 18.25% | 14.29% | 1.112 |
| 22 | 18.25% | 42.93% | 0.00% | 30.00% | 0.00% | 0.00% | 2.22% | 0.00% | 6.60% | 18.35% | 14.41% | 1.110 |
| 23 | 17.24% | 43.27% | 0.00% | 30.00% | 0.00% | 0.00% | 2.21% | 0.00% | 7.28% | 18.45% | 14.53% | 1.107 |
| 24 | 16.22% | 43.61% | 0.00% | 30.00% | 0.00% | 0.00% | 2.21% | 0.00% | 7.96% | 18.55% | 14.65% | 1.105 |
| 25 | 15.20% | 43.96% | 0.00% | 30.00% | 0.00% | 0.00% | 2.21% | 0.00% | 8.64% | 18.66% | 14.77% | 1.103 |
| 26 | 14.19% | 44.30% | 0.00% | 30.00% | 0.00% | 0.00% | 2.20% | 0.00% | 9.31% | 18.76% | 14.89% | 1.101 |
| 27 | 13.17% | 44.64% | 0.00% | 30.00% | 0.00% | 0.00% | 2.20% | 0.00% | 9.99% | 18.86% | 15.01% | 1.099 |
| 28 | 12.15% | 44.99% | 0.00% | 30.00% | 0.00% | 0.00% | 2.19% | 0.00% | 10.67% | 18.96% | 15.13% | 1.097 |
| 29 | 11.14% | 45.33% | 0.00% | 30.00% | 0.00% | 0.00% | 2.19% | 0.00% | 11.35% | 19.06% | 15.25% | 1.095 |
| 30 | 10.12% | 45.67% | 0.00% | 30.00% | 0.00% | 0.00% | 2.19% | 0.00% | 12.02% | 19.16% | 15.37% | 1.093 |
| 31 | 9.10% | 46.02% | 0.00% | 30.00% | 0.00% | 0.00% | 2.18% | 0.00% | 12.70% | 19.26% | 15.49% | 1.091 |
| 32 | 8.09% | 46.36% | 0.00% | 30.00% | 0.00% | 0.00% | 2.18% | 0.00% | 13.38% | 19.36% | 15.61% | 1.090 |
| 33 | 7.07% | 46.70% | 0.00% | 30.00% | 0.00% | 0.00% | 2.17% | 0.00% | 14.06% | 19.46% | 15.73% | 1.088 |
| 34 | 6.05% | 47.04% | 0.00% | 30.00% | 0.00% | 0.00% | 2.17% | 0.00% | 14.73% | 19.57% | 15.85% | 1.086 |
| 35 | 5.04% | 47.39% | 0.00% | 30.00% | 0.00% | 0.00% | 2.16% | 0.00% | 15.41% | 19.67% | 15.97% | 1.084 |
| 36 | 4.02% | 47.73% | 0.00% | 30.00% | 0.00% | 0.00% | 2.16% | 0.00% | 16.09% | 19.77% | 16.09% | 1.082 |
| 37 | 3.00% | 48.07% | 0.00% | 30.00% | 0.00% | 0.00% | 2.16% | 0.00% | 16.77% | 19.87% | 16.21% | 1.080 |
| 38 | 1.99% | 48.42% | 0.00% | 30.00% | 0.00% | 0.00% | 2.15% | 0.00% | 17.44% | 19.97% | 16.33% | 1.079 |
| 39 | 0.97% | 48.76% | 0.00% | 30.00% | 0.00% | 0.00% | 2.15% | 0.00% | 18.12% | 20.07% | 16.45% | 1.077 |
| 40 | 0.00% | 49.07% | 0.00% | 30.00% | 0.00% | 0.00% | 2.14% | 0.00% | 18.79% | 20.17% | 16.57% | 1.075 |
| 41 | 0.00% | 48.58% | 0.00% | 30.00% | 0.00% | 0.00% | 2.04% | 0.00% | 19.38% | 20.27% | 16.69% | 1.073 |
| 42 | 0.00% | 48.09% | 0.00% | 30.00% | 0.00% | 0.00% | 1.94% | 0.00% | 19.97% | 20.38% | 16.81% | 1.072 |
| 43 | 0.00% | 47.60% | 0.00% | 30.00% | 0.00% | 0.00% | 1.84% | 0.00% | 20.56% | 20.48% | 16.93% | 1.070 |
| 44 | 0.00% | 47.11% | 0.00% | 30.00% | 0.00% | 0.00% | 1.74% | 0.00% | 21.15% | 20.58% | 17.06% | 1.068 |
| 45 | 0.00% | 46.62% | 0.00% | 30.00% | 0.00% | 0.00% | 1.64% | 0.00% | 21.74% | 20.68% | 17.18% | 1.066 |
| 46 | 0.00% | 46.13% | 0.00% | 30.00% | 0.00% | 0.00% | 1.54% | 0.00% | 22.33% | 20.78% | 17.31% | 1.064 |
| 47 | 0.00% | 45.64% | 0.00% | 30.00% | 0.00% | 0.00% | 1.44% | 0.00% | 22.92% | 20.88% | 17.43% | 1.063 |
| 48 | 0.00% | 45.15% | 0.00% | 30.00% | 0.00% | 0.00% | 1.34% | 0.00% | 23.51% | 20.98% | 17.56% | 1.061 |
| 49 | 0.00% | 44.66% | 0.00% | 30.00% | 0.00% | 0.00% | 1.24% | 0.00% | 24.10% | 21.08% | 17.68% | 1.059 |
| 50 | 0.00% | 44.18% | 0.00% | 30.00% | 0.00% | 0.00% | 1.14% | 0.00% | 24.69% | 21.19% | 17.81% | 1.057 |
| 51 | 0.00% | 43.69% | 0.00% | 30.00% | 0.00% | 0.00% | 1.04% | 0.00% | 25.27% | 21.29% | 17.93% | 1.055 |
| 52 | 0.00% | 43.20% | 0.00% | 30.00% | 0.00% | 0.00% | 0.94% | 0.00% | 25.86% | 21.39% | 18.06% | 1.054 |
| 53 | 0.00% | 42.71% | 0.00% | 30.00% | 0.00% | 0.00% | 0.84% | 0.00% | 26.45% | 21.49% | 18.19% | 1.052 |
| 54 | 0.00% | 42.22% | 0.00% | 30.00% | 0.00% | 0.00% | 0.74% | 0.00% | 27.04% | 21.59% | 18.32% | 1.050 |
| 55 | 0.00% | 41.73% | 0.00% | 30.00% | 0.00% | 0.00% | 0.64% | 0.00% | 27.63% | 21.69% | 18.45% | 1.048 |
| 56 | 0.00% | 41.24% | 0.00% | 30.00% | 0.00% | 0.00% | 0.54% | 0.00% | 28.22% | 21.79% | 18.57% | 1.046 |
| 57 | 0.00% | 40.75% | 0.00% | 30.00% | 0.00% | 0.00% | 0.44% | 0.00% | 28.81% | 21.89% | 18.70% | 1.044 |
| 58 | 0.00% | 40.26% | 0.00% | 30.00% | 0.00% | 0.00% | 0.34% | 0.00% | 29.40% | 22.00% | 18.83% | 1.043 |
| 59 | 0.00% | 39.77% | 0.00% | 30.00% | 0.00% | 0.00% | 0.24% | 0.00% | 29.99% | 22.10% | 18.97% | 1.041 |
| 60 | 0.00% | 41.11% | 0.00% | 28.89% | 0.00% | 0.00% | 0.00% | 0.00% | 30.00% | 22.20% | 19.11% | 1.038 |
| 61 | 0.00% | 42.40% | 0.00% | 27.60% | 0.00% | 0.00% | 0.00% | 0.00% | 30.00% | 22.30% | 19.26% | 1.035 |
| 62 | 0.00% | 43.69% | 0.00% | 26.31% | 0.00% | 0.00% | 0.00% | 0.00% | 30.00% | 22.40% | 19.41% | 1.032 |
| 63 | 0.00% | 44.75% | 0.00% | 25.10% | 0.00% | 0.00% | 0.00% | 0.14% | 30.00% | 22.50% | 19.57% | 1.029 |
| 64 | 0.00% | 44.93% | 0.00% | 24.23% | 0.00% | 0.00% | 0.00% | 0.84% | 30.00% | 22.60% | 19.72% | 1.026 |
| 65 | 0.00% | 45.10% | 0.00% | 23.36% | 0.00% | 0.00% | 0.00% | 1.54% | 30.00% | 22.70% | 19.89% | 1.023 |
| 66 | 0.00% | 45.27% | 0.00% | 22.49% | 0.00% | 0.00% | 0.00% | 2.24% | 30.00% | 22.81% | 20.05% | 1.020 |
| 67 | 0.00% | 45.45% | 0.00% | 21.62% | 0.00% | 0.00% | 0.00% | 2.94% | 30.00% | 22.91% | 20.21% | 1.017 |
| 68 | 0.00% | 45.62% | 0.00% | 20.75% | 0.00% | 0.00% | 0.00% | 3.63% | 30.00% | 23.01% | 20.38% | 1.013 |
| 69 | 0.00% | 45.79% | 0.00% | 19.87% | 0.00% | 0.00% | 0.00% | 4.33% | 30.00% | 23.11% | 20.55% | 1.010 |
| 70 | 0.00% | 45.97% | 0.00% | 19.00% | 0.00% | 0.00% | 0.00% | 5.03% | 30.00% | 23.21% | 20.72% | 1.007 |
| 71 | 0.00% | 46.14% | 0.00% | 18.13% | 0.00% | 0.00% | 0.00% | 5.73% | 30.00% | 23.31% | 20.89% | 1.003 |
| 72 | 0.00% | 46.32% | 0.00% | 17.26% | 0.00% | 0.00% | 0.00% | 6.42% | 30.00% | 23.41% | 21.06% | 1.000 |
| 73 | 0.00% | 46.49% | 0.00% | 16.39% | 0.00% | 0.00% | 0.00% | 7.12% | 30.00% | 23.51% | 21.24% | 0.996 |
| 74 | 0.00% | 46.66% | 0.00% | 15.52% | 0.00% | 0.00% | 0.00% | 7.82% | 30.00% | 23.62% | 21.41% | 0.993 |
| 75 | 0.00% | 46.84% | 0.00% | 14.65% | 0.00% | 0.00% | 0.00% | 8.52% | 30.00% | 23.72% | 21.59% | 0.989 |
| 76 | 0.00% | 47.01% | 0.00% | 13.78% | 0.00% | 0.00% | 0.00% | 9.22% | 30.00% | 23.82% | 21.77% | 0.986 |
| 77 | 0.00% | 47.18% | 0.00% | 12.90% | 0.00% | 0.00% | 0.00% | 9.91% | 30.00% | 23.92% | 21.95% | 0.982 |
| 78 | 0.00% | 47.36% | 0.00% | 12.03% | 0.00% | 0.00% | 0.00% | 10.61% | 30.00% | 24.02% | 22.13% | 0.979 |
| 79 | 0.00% | 47.53% | 0.00% | 11.16% | 0.00% | 0.00% | 0.00% | 11.31% | 30.00% | 24.12% | 22.32% | 0.975 |
| 80 | 0.00% | 47.70% | 0.00% | 10.29% | 0.00% | 0.00% | 0.00% | 12.01% | 30.00% | 24.22% | 22.50% | 0.972 |
| 81 | 0.00% | 47.88% | 0.00% | 9.42% | 0.00% | 0.00% | 0.00% | 12.70% | 30.00% | 24.32% | 22.69% | 0.968 |
| 82 | 0.44% | 47.80% | 0.00% | 8.51% | 0.00% | 0.00% | 0.00% | 13.25% | 30.00% | 24.42% | 22.88% | 0.965 |
| 83 | 0.96% | 47.73% | 0.24% | 7.40% | 0.00% | 0.00% | 0.00% | 13.67% | 30.00% | 24.53% | 23.07% | 0.961 |
| 84 | 1.40% | 47.75% | 0.70% | 6.12% | 0.00% | 0.00% | 0.00% | 14.03% | 30.00% | 24.63% | 23.26% | 0.958 |
| 85 | 1.84% | 47.76% | 1.17% | 4.85% | 0.00% | 0.00% | 0.00% | 14.38% | 30.00% | 24.73% | 23.45% | 0.954 |
| 86 | 2.28% | 47.78% | 1.63% | 3.57% | 0.00% | 0.00% | 0.00% | 14.74% | 30.00% | 24.83% | 23.64% | 0.951 |
| 87 | 2.72% | 47.79% | 2.10% | 2.29% | 0.00% | 0.00% | 0.00% | 15.10% | 30.00% | 24.93% | 23.83% | 0.947 |
| 88 | 3.16% | 47.81% | 2.56% | 1.02% | 0.00% | 0.00% | 0.00% | 15.45% | 30.00% | 25.03% | 24.02% | 0.944 |
| 89 | 3.49% | 47.56% | 2.85% | 0.00% | 0.00% | 0.00% | 0.00% | 16.10% | 30.00% | 25.13% | 24.21% | 0.941 |
| 90 | 3.36% | 46.29% | 2.44% | 0.00% | 0.00% | 0.00% | 0.00% | 17.90% | 30.00% | 25.23% | 24.41% | 0.937 |
| 91 | 3.23% | 45.03% | 2.04% | 0.00% | 0.00% | 0.00% | 0.00% | 19.71% | 30.00% | 25.34% | 24.61% | 0.934 |
| 92 | 3.10% | 43.76% | 1.63% | 0.00% | 0.00% | 0.00% | 0.00% | 21.51% | 30.00% | 25.44% | 24.81% | 0.930 |
| 93 | 2.97% | 42.49% | 1.23% | 0.00% | 0.00% | 0.00% | 0.00% | 23.31% | 30.00% | 25.54% | 25.02% | 0.926 |
| 94 | 2.85% | 41.22% | 0.82% | 0.00% | 0.00% | 0.00% | 0.00% | 25.11% | 30.00% | 25.64% | 25.23% | 0.923 |
| 95 | 2.72% | 39.96% | 0.41% | 0.00% | 0.00% | 0.00% | 0.00% | 26.91% | 30.00% | 25.74% | 25.45% | 0.919 |
| 96 | 2.59% | 38.69% | 0.01% | 0.00% | 0.00% | 0.00% | 0.00% | 28.71% | 30.00% | 25.84% | 25.66% | 0.915 |
| 97 | 6.94% | 33.06% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 30.00% | 30.00% | 25.94% | 25.89% | 0.911 |
| 98 | 17.96% | 22.04% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 30.00% | 30.00% | 26.04% | 26.16% | 0.905 |
| 99 | 28.98% | 11.02% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 30.00% | 30.00% | 26.15% | 26.49% | 0.898 |
| 100 | 40.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 30.00% | 30.00% | 26.25% | 26.86% | 0.889 |
| \*Annualized ex-ante values shown for portfolio return and volatility. Ex-ante Sharpe Ratio calculated using historical U.S. 3-Month Treasury Bill Rate returns as the risk-free rate. |

#### Annualized Active Return

Created with Highcharts 10.3.3YearActive ReturnAnnualized Active ReturnActive Return vs. State Street SPDR S&P 500 ETFProvided PortfolioMaximum Return at 15.00% Volatility20162017201820192020202120222023202420252026\-20.0%\-10.0%0.0%10.0%20.0%30.0%

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

Created with Highcharts 10.3.3Cumulative Active ReturnCumulative Active ReturnMaximum Return at 15.00% Volatility vs. State Street SPDR S&P 500 ETFInvesco QQQ TrustInvesco S&P 500 Momentum ETFSPDR Gold SharesState StreetEngySelSectSPDRETFProShares Ultra QQQAug 2016Sep 2016Oct 2016Nov 2016Dec 2016Jan 2017Feb 2017Mar 2017Apr 2017May 2017Jun 2017Jul 2017Aug 2017Sep 2017Oct 2017Nov 2017Dec 2017Jan 2018Feb 2018Mar 2018Apr 2018May 2018Jun 2018Jul 2018Aug 2018Sep 2018Oct 2018Nov 2018Dec 2018Jan 2019Feb 2019Mar 2019Apr 2019May 2019Jun 2019Jul 2019Aug 2019Sep 2019Oct 2019Nov 2019Dec 2019Jan 2020Feb 2020Mar 2020Apr 2020May 2020Jun 2020Jul 2020Aug 2020Sep 2020Oct 2020Nov 2020Dec 2020Jan 2021Feb 2021Mar 2021Apr 2021May 2021Jun 2021Jul 2021Aug 2021Sep 2021Oct 2021Nov 2021Dec 2021Jan 2022Feb 2022Mar 2022Apr 2022May 2022Jun 2022Jul 2022Aug 2022Sep 2022Oct 2022Nov 2022Dec 2022Jan 2023Feb 2023Mar 2023Apr 2023May 2023Jun 2023Jul 2023Aug 2023Sep 2023Oct 2023Nov 2023Dec 2023Jan 2024Feb 2024Mar 2024Apr 2024May 2024Jun 2024Jul 2024Aug 2024Sep 2024Oct 2024Nov 2024Dec 2024Jan 2025Feb 2025Mar 2025Apr 2025May 2025Jun 2025Jul 2025Aug 2025Sep 2025Oct 2025Nov 2025Dec 2025Jan 2026Feb 2026Mar 2026Apr 2026May 2026Jun 2026Jul 2026\-200.0%\-100.0%0.0%100.0%200.0%300.0%

Cumulative Active Return - Maximum Return at 15.00% Volatility vs. State Street SPDR S&P 500 ETF

| Asset | 1-year | 3-year | 5-year | 10-year | Full |
| --- | --- | --- | --- | --- | --- |
| Invesco QQQ Trust | 1.75% | 5.38% | 5.49% | 33.17% | 33.17% |
| Invesco S&P 500 Momentum ETF | 12.41% | 94.54% | 73.26% | 89.27% | 89.27% |
| SPDR Gold Shares | 8.08% | 35.85% | 39.71% | \-26.49% | \-26.49% |
| State StreetEngySelSectSPDRETF | 2.33% | \-0.34% | 6.86% | \-0.74% | \-0.74% |
| ProShares Ultra QQQ | 7.65% | 19.88% | 17.77% | 78.28% | 78.28% |

#### Rolling Active Return

Created with Highcharts 10.3.3Active ReturnTracking ErrorRolling Active Return and Risk (36 months)Provided Portfolio vs. State Street SPDR S&P 500 ETFActive ReturnTracking Error2020202120222023202420252026\-10.0%\-5.0%0.0%5.0%10.0%15.0%20.0%5.6%6.4%7.2%8.0%8.8%9.6%10.4%

Created with Highcharts 10.3.3Active ReturnTracking ErrorRolling Active Return and Risk (36 months)Maximum Return at 15.00% Volatility vs. State Street SPDR S&P 500 ETFActive ReturnTracking Error2020202120222023202420252026\-10.0%\-5.0%0.0%5.0%10.0%15.0%20.0%4.2%4.8%5.4%6.0%6.6%7.2%7.8%

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

##### Maximum Return at 15.00% Volatility vs. State Street SPDR S&P 500 ETF

Up vs. Down Market Performance - Maximum Return at 15.00% Volatility vs. State Street SPDR S&P 500 ETF

| Market Type | Occurrences | Average Active Return |
| --- | --- | --- |
| Above Benchmark | Below Benchmark | Total | % Above Benchmark | Above Benchmark | Below Benchmark | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Up Market | 49 | 36 | 85 | 58% | 1.11% | \-1.70% | \-0.08% |
| Down Market | 25 | 10 | 35 | 71% | 1.95% | \-0.65% | 1.21% |
| Total | 74 | 46 | 120 | 62% | 1.39% | \-1.47% | 0.30% |

Created with Highcharts 10.3.3Benchmark ReturnReturnReturn vs. BenchmarkMaximum Return at 15.00% Volatility vs. State Street SPDR S&P 500 ETFMaximum Return at 15.00% VolatilityState Street SPDR S&P 500 ETF\-9.2%\-5.8%\-4.1%\-2.5%\-1.4%\-0.6%0.1%0.5%1.2%1.7%2.0%2.3%2.6%3.2%3.6%4.1%5.0%5.8%7.0%10.1%\-12.0%\-10.0%\-8.0%\-6.0%\-4.0%\-2.0%0.0%2.0%4.0%6.0%8.0%10.0%12.0%

#### Risk and Return Metrics

Portfolio return and risk metrics

| Metric | Provided Portfolio | Maximum Return at 15.00% Volatility | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- |
| Arithmetic Mean (monthly) | 1.62% | 1.56% | 1.27% |
| Arithmetic Mean (annualized) | 21.25% | 20.46% | 16.32% |
| Geometric Mean (monthly) | 1.47% | 1.47% | 1.17% |
| Geometric Mean (annualized) | 19.21% | 19.17% | 14.99% |
| Standard Deviation (monthly) | 5.40% | 4.30% | 4.42% |
| Standard Deviation (annualized) | 18.71% | 14.89% | 15.32% |
| Downside Deviation (monthly) | 3.08% | 2.35% | 2.72% |
| Maximum Drawdown | \-24.58% | \-22.44% | \-23.93% |
| Benchmark Correlation | 0.90 | 0.90 | 1.00 |
| Beta(\*) | 1.10 | 0.88 | 1.00 |
| Alpha (annualized) | 2.74% | 5.39% | 0.00% |
| R2 | 80.57% | 81.73% | 100.00% |
| Sharpe Ratio | 0.91 | 1.10 | 0.84 |
| Sortino Ratio | 1.56 | 1.95 | 1.32 |
| Treynor Ratio (%) | 15.56 | 18.66 | 12.86 |
| Calmar Ratio | 3.01 | 4.44 | 2.31 |
| Modigliani–Modigliani Measure | 16.34% | 19.28% | 15.22% |
| Active Return | 4.22% | 4.18% | N/A |
| Tracking Error | 8.38% | 6.63% | N/A |
| Information Ratio | 0.50 | 0.63 | N/A |
| Skewness | \-0.12 | \-0.14 | \-0.42 |
| Excess Kurtosis | 0.71 | 0.12 | 0.63 |
| Historical Value-at-Risk (5%) | 7.27% | 6.54% | 6.96% |
| Analytical Value-at-Risk (5%) | 7.23% | 5.48% | 6.01% |
| Conditional Value-at-Risk (5%) | 10.41% | 7.60% | 9.24% |
| Upside Capture Ratio (%) | 115.95 | 96.67 | 100.00 |
| Downside Capture Ratio (%) | 100.32 | 75.39 | 100.00 |
| Safe Withdrawal Rate | 16.24% | 16.58% | 15.91% |
| Perpetual Withdrawal Rate | 13.32% | 13.29% | 10.14% |
| Positive Periods | 80 out of 120 (66.67%) | 81 out of 120 (67.50%) | 85 out of 120 (70.83%) |
| Gain/Loss Ratio | 1.09 | 1.20 | 0.85 |
| \* State Street SPDR S&P 500 ETF is used as the benchmark for calculations. Value-at-risk metrics are monthly values. |

#### Annual Returns

Annual returns for the configured portfolios

| Year | Inflation | Provided Portfolio | Maximum Return at 15.00% Volatility | State Street SPDR S&P 500 ETF | Invesco QQQ Trust (QQQ) | Invesco S&P 500 Momentum ETF (SPMO) | VanEck Gold Miners ETF (GDX) | iShares Silver Trust (SLV) | iShares Asia 50 ETF (AIA) | State StreetEngySelSectSPDRETF (XLE) | Invesco Dorsey Wright Technology MomtETF (PTF) | ProShares Ultra QQQ (QLD) | SPDR Gold Shares (GLD) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Return | Balance | Return | Balance | Return | Balance |
| --- | --- | --- | --- | --- | --- |
| 2026 | 3.04% | 18.65% | $57,949 | 12.83% | $57,769 | 10.13% | $40,420 | 12.26% | 21.06% | \-13.61% | \-18.72% | 37.35% | 35.01% | 28.31% | 18.94% | \-6.25% |
| 2025 | 2.68% | 44.10% | $48,839 | 36.88% | $51,202 | 17.72% | $36,702 | 20.77% | 26.57% | 154.71% | 144.66% | 47.79% | 7.88% | 5.67% | 30.36% | 63.68% |
| 2024 | 2.89% | 26.12% | $33,893 | 36.46% | $37,406 | 24.89% | $31,178 | 25.58% | 45.81% | 10.63% | 20.89% | 20.26% | 5.52% | 43.65% | 42.81% | 26.66% |
| 2023 | 3.35% | 27.19% | $26,874 | 28.60% | $27,411 | 26.19% | $24,966 | 54.85% | 17.55% | 9.96% | \-1.09% | 4.90% | \-0.64% | 33.73% | 117.13% | 12.69% |
| 2022 | 6.45% | \-14.75% | $21,128 | \-15.25% | $21,315 | \-18.17% | $19,784 | \-32.58% | \-10.46% | \-8.98% | 2.37% | \-23.76% | 64.17% | \-31.75% | \-60.52% | \-0.77% |
| 2021 | 7.04% | 18.33% | $24,784 | 18.38% | $25,149 | 28.75% | $24,178 | 27.42% | 22.65% | \-9.52% | \-12.45% | \-10.90% | 53.31% | 18.10% | 54.67% | \-4.15% |
| 2020 | 1.36% | 35.33% | $20,946 | 34.63% | $21,244 | 18.37% | $18,780 | 48.62% | 28.28% | 23.66% | 47.30% | 33.74% | \-32.51% | 82.06% | 88.90% | 24.81% |
| 2019 | 2.29% | 33.91% | $15,477 | 30.00% | $15,780 | 31.22% | $15,865 | 38.96% | 25.93% | 39.79% | 14.88% | 22.19% | 11.74% | 46.71% | 81.69% | 17.86% |
| 2018 | 1.91% | \-6.60% | $11,558 | \-1.37% | $12,138 | \-4.56% | $12,090 | \-0.12% | \-0.90% | \-8.79% | \-9.19% | \-14.23% | \-18.21% | 0.02% | \-8.32% | \-1.94% |
| 2017 | 2.11% | 27.10% | $12,375 | 26.74% | $12,307 | 21.70% | $12,667 | 32.66% | 27.75% | 11.97% | 5.82% | 45.00% | \-0.90% | 32.06% | 70.34% | 12.81% |
| 2016 | 0.33% | \-2.64% | $9,736 | \-2.89% | $9,711 | 4.09% | $10,409 | 3.38% | 1.26% | \-31.41% | \-21.91% | \-0.22% | 13.06% | \-0.31% | 5.67% | \-15.02% |
| Annual return for 2016 is from 08/01/2016 to 12/31/2016 and annual return for 2026 is from 01/01/2026 to 07/31/2026 |

Show 123660All entries

*   First
*   Previous
*   Next
*   Last

#### Monthly Returns

Monthly returns for the configured portfolios

| Year | Month | Provided Portfolio | Maximum Return at 15.00% Volatility | State Street SPDR S&P 500 ETF | Invesco QQQ Trust (QQQ) | Invesco S&P 500 Momentum ETF (SPMO) | VanEck Gold Miners ETF (GDX) | iShares Silver Trust (SLV) | iShares Asia 50 ETF (AIA) | State StreetEngySelSectSPDRETF (XLE) | Invesco Dorsey Wright Technology MomtETF (PTF) | ProShares Ultra QQQ (QLD) | SPDR Gold Shares (GLD) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Return | Balance | Return | Balance | Return | Balance |
| --- | --- | --- | --- | --- | --- |
| 2026 | 7 | \-6.00% | $57,949 | \-6.52% | $57,769 | 0.03% | $40,420 | \-6.57% | \-10.96% | \-1.79% | \-2.08% | \-5.79% | 12.13% | \-28.00% | \-13.53% | 0.86% |
| 2026 | 6 | \-3.40% | $61,648 | \-0.50% | $61,801 | \-1.03% | $40,406 | \-0.15% | 7.43% | \-15.69% | \-21.75% | \-0.12% | \-4.98% | 5.62% | \-1.66% | \-11.68% |
| 2026 | 5 | 8.81% | $63,817 | 8.48% | $62,110 | 5.26% | $40,827 | 10.57% | 12.56% | 1.36% | 2.51% | 14.43% | \-5.63% | 15.85% | 21.48% | \-1.54% |
| 2026 | 4 | 12.85% | $58,650 | 13.33% | $57,257 | 10.51% | $38,786 | 15.69% | 19.34% | \-3.79% | \-2.17% | 17.17% | \-2.63% | 29.05% | 32.87% | \-1.54% |
| 2026 | 3 | \-7.24% | $51,972 | \-7.34% | $50,521 | \-4.93% | $35,099 | \-4.84% | \-5.90% | \-20.78% | \-19.83% | \-10.06% | 10.26% | \-6.21% | \-10.26% | \-11.05% |
| 2026 | 2 | 6.02% | $56,026 | 1.86% | $54,526 | \-0.86% | $36,921 | \-2.34% | \-0.33% | 22.97% | 12.66% | 7.92% | 9.54% | 8.61% | \-5.19% | 8.72% |
| 2026 | 1 | 8.20% | $52,844 | 4.54% | $53,529 | 1.47% | $37,243 | 1.23% | 0.46% | 9.83% | 17.11% | 12.15% | 14.18% | 10.79% | 1.85% | 12.27% |
| 2025 | 12 | 2.87% | $48,839 | 0.18% | $51,202 | 0.08% | $36,702 | \-0.67% | \-0.43% | 3.78% | 25.80% | 4.12% | \-0.30% | \-2.94% | \-1.92% | 2.17% |
| 2025 | 11 | 1.77% | $47,478 | 0.51% | $51,108 | 0.19% | $36,673 | \-1.56% | \-1.30% | 15.50% | 16.36% | \-3.71% | 2.63% | \-4.21% | \-3.92% | 5.37% |
| 2025 | 10 | 3.21% | $46,652 | 2.78% | $50,850 | 2.38% | $36,602 | 4.78% | 0.53% | \-5.68% | 3.87% | 4.62% | \-1.35% | 9.96% | 8.95% | 3.56% |
| 2025 | 9 | 9.03% | $45,202 | 7.07% | $49,473 | 3.56% | $35,750 | 5.38% | 4.10% | 20.94% | 17.08% | 11.48% | \-0.32% | 10.26% | 10.48% | 11.76% |
| 2025 | 8 | 3.99% | $41,457 | 2.12% | $46,205 | 2.05% | $34,521 | 0.95% | 0.68% | 22.33% | 8.61% | 2.05% | 3.65% | \-3.35% | 1.18% | 4.99% |

Show 123660All entries

*   First
*   Previous
*   [Next](#)
*   [Last](#)

#### Drawdowns

Created with Highcharts 10.3.3YearDrawdownProvided PortfolioMaximum Return at 15.00% VolatilityState Street SPDR S&P 500 ETF2017201820192020202120222023202420252026\-30.0%\-25.0%\-20.0%\-15.0%\-10.0%\-5.0%0.0%

#### Historical Market Stress Periods

Drawdowns for Historical Market Stress Periods

| Stress Period | Start | End | Provided Portfolio | Maximum Return at 15.00% Volatility | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- | --- | --- |
| COVID-19 Start | Jan 2020 | Mar 2020 | \-22.17% | \-13.29% | \-19.43% |

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

#### Drawdowns for Maximum Return at 15.00% Volatility

Drawdowns for Maximum Return at 15.00% Volatility (worst 10)

| Rank | Start | End | Length | Recovery By | Recovery Time | Underwater Period | Drawdown |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Jan 2022 | Sep 2022 | 9 months | Nov 2023 | 1 year 2 months | 1 year 11 months | \-22.44% |
| 2 | Feb 2020 | Mar 2020 | 2 months | May 2020 | 2 months | 4 months | \-13.29% |
| 3 | Oct 2018 | Dec 2018 | 3 months | Mar 2019 | 3 months | 6 months | \-11.45% |
| 4 | Mar 2026 | Mar 2026 | 1 month | Apr 2026 | 1 month | 2 months | \-7.34% |
| 5 | Sep 2020 | Oct 2020 | 2 months | Dec 2020 | 2 months | 4 months | \-7.30% |
| 6 | Jun 2026 | Jul 2026 | 2 months |  |  |  | \-6.99% |
| 7 | Sep 2021 | Sep 2021 | 1 month | Oct 2021 | 1 month | 2 months | \-4.71% |
| 8 | Oct 2016 | Nov 2016 | 2 months | Jan 2017 | 2 months | 4 months | \-4.69% |
| 9 | Feb 2018 | Mar 2018 | 2 months | Jul 2018 | 4 months | 6 months | \-4.45% |
| 10 | May 2019 | May 2019 | 1 month | Jun 2019 | 1 month | 2 months | \-3.51% |
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

| Ticker | Name | QQQ | SPMO | GDX | SLV | AIA | XLE | PTF | QLD | GLD | Provided Portfolio | Maximum Return at 15.00% Volatility | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QQQ | Invesco QQQ Trust | 1.00 | 0.83 | 0.24 | 0.26 | 0.58 | 0.29 | 0.83 | 1.00 | 0.12 | 0.87 | 0.92 | 0.91 |
| SPMO | Invesco S&P 500 Momentum ETF | 0.83 | 1.00 | 0.17 | 0.20 | 0.48 | 0.33 | 0.76 | 0.83 | 0.03 | 0.78 | 0.91 | 0.85 |
| GDX | VanEck Gold Miners ETF | 0.24 | 0.17 | 1.00 | 0.73 | 0.37 | 0.20 | 0.14 | 0.24 | 0.84 | 0.55 | 0.46 | 0.30 |
| SLV | iShares Silver Trust | 0.26 | 0.20 | 0.73 | 1.00 | 0.40 | 0.14 | 0.22 | 0.27 | 0.76 | 0.56 | 0.46 | 0.29 |
| AIA | iShares Asia 50 ETF | 0.58 | 0.48 | 0.37 | 0.40 | 1.00 | 0.26 | 0.54 | 0.59 | 0.35 | 0.74 | 0.62 | 0.57 |
| XLE | State StreetEngySelSectSPDRETF | 0.29 | 0.33 | 0.20 | 0.14 | 0.26 | 1.00 | 0.24 | 0.31 | \-0.03 | 0.53 | 0.34 | 0.53 |
| PTF | Invesco Dorsey Wright Technology MomtETF | 0.83 | 0.76 | 0.14 | 0.22 | 0.54 | 0.24 | 1.00 | 0.83 | 0.06 | 0.78 | 0.79 | 0.74 |
| QLD | ProShares Ultra QQQ | 1.00 | 0.83 | 0.24 | 0.27 | 0.59 | 0.31 | 0.83 | 1.00 | 0.12 | 0.88 | 0.91 | 0.92 |
| GLD | SPDR Gold Shares | 0.12 | 0.03 | 0.84 | 0.76 | 0.35 | \-0.03 | 0.06 | 0.12 | 1.00 | 0.39 | 0.37 | 0.13 |

#### Portfolio Return Decomposition

Portfolio return decomposition

| Ticker | Name | Provided Portfolio | Maximum Return at 15.00% Volatility |
| --- | --- | --- | --- |
| QQQ | Invesco QQQ Trust | $8,770 | $6,508 |
| SPMO | Invesco S&P 500 Momentum ETF | $4,913 | $22,615 |
| GDX | VanEck Gold Miners ETF | $4,159 |  |
| SLV | iShares Silver Trust | $4,165 |  |
| AIA | iShares Asia 50 ETF | $6,554 |  |
| XLE | State StreetEngySelSectSPDRETF | $6,388 | $975 |
| PTF | Invesco Dorsey Wright Technology MomtETF | $5,499 |  |
| QLD | ProShares Ultra QQQ | $7,502 | $7,306 |
| GLD | SPDR Gold Shares |  | $10,364 |
| Return attribution decomposes portfolio gains into its constituent parts and identifies the contribution to returns by each of the assets. |

#### Portfolio Risk Decomposition

Portfolio risk decomposition

| Ticker | Name | Provided Portfolio | Maximum Return at 15.00% Volatility |
| --- | --- | --- | --- |
| QQQ | Invesco QQQ Trust | 17.72% | 16.56% |
| SPMO | Invesco S&P 500 Momentum ETF | 7.47% | 48.50% |
| GDX | VanEck Gold Miners ETF | 9.96% |  |
| SLV | iShares Silver Trust | 8.90% |  |
| AIA | iShares Asia 50 ETF | 12.80% |  |
| XLE | State StreetEngySelSectSPDRETF | 12.87% | 1.49% |
| PTF | Invesco Dorsey Wright Technology MomtETF | 12.03% |  |
| QLD | ProShares Ultra QQQ | 18.25% | 22.21% |
| GLD | SPDR Gold Shares |  | 11.24% |
| Risk attribution decomposes portfolio risk into its constituent parts and identifies the contribution to overall volatility by each of the assets. |

#### Annual Asset Returns

Created with Highcharts 10.3.3YearReturnAnnual Returns of Portfolio AssetsInvesco QQQ TrustInvesco S&P 500 Momentum ETFVanEck Gold Miners ETFSPDR Gold SharesiShares Silver TrustiShares Asia 50 ETFState StreetEngySelSectSPDRETFInvesco Dorsey Wright Technology MomtETFProShares Ultra QQQ20162017201820192020202120222023202420252026\-100.0%0.0%100.0%200.0%

#### Rolling Returns

Rolling returns summary

| Roll Period | Provided Portfolio | Maximum Return at 15.00% Volatility | State Street SPDR S&P 500 ETF |
| --- | --- | --- | --- |
| Average | High | Low | Average | High | Low | Average | High | Low |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 year | 21.22% | 81.63% | \-19.44% | 21.15% | 51.97% | \-16.08% | 15.78% | 56.25% | \-18.17% |
| 3 years | 17.83% | 39.07% | 4.13% | 18.59% | 39.03% | 6.49% | 14.30% | 25.99% | 5.05% |
| 5 years | 17.07% | 23.40% | 10.19% | 17.34% | 22.72% | 10.62% | 14.09% | 18.81% | 9.16% |
| 7 years | 17.61% | 25.91% | 13.23% | 18.31% | 24.33% | 13.16% | 14.20% | 17.28% | 12.09% |

#### Annualized Rolling Return - 3 Years

Created with Highcharts 10.3.3YearAnnualized ReturnProvided PortfolioMaximum Return at 15.00% VolatilityState Street SPDR S&P 500 ETF20202021202220232024202520260.0%5.0%10.0%15.0%20.0%25.0%30.0%35.0%40.0%45.0%

#### Annualized Rolling Return - 5 Years

Created with Highcharts 10.3.3YearAnnualized ReturnProvided PortfolioMaximum Return at 15.00% VolatilityState Street SPDR S&P 500 ETFJan 2022Jul 2022Jan 2023Jul 2023Jan 2024Jul 2024Jan 2025Jul 2025Jan 2026Jul 20267.5%10.0%12.5%15.0%17.5%20.0%22.5%25.0%

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
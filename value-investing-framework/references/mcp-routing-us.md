# 미국 시장 MCP 라우팅

NYSE/NASDAQ 종목 분석 시 사용할 MCP 도구표. 우선 → 백업 순.

## 종목 식별·검색

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 티커 → CIK | `sec-edgar:get_cik_by_ticker` | - |
| 티커 → 회사 기본정보 | `finnhub:finnhub_company_profile2` | `sec-edgar:get_company_info`, `yfinance:yfinance_get_ticker_info` |
| 회사명 → 티커 | `finnhub:finnhub_symbol_lookup` | `sec-edgar:search_companies` |
| 시장 구분 (NYSE/NASDAQ) | `finnhub:finnhub_stock_symbols` (exchange 필드) | `finviz-plus:get_stock_fundamentals` |

종목 모호 시 `cross-market-equity-router` 위임.

## 재무제표 (AV·EPV 계산용)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 5년 재무제표 | `sec-edgar:get_financials` | `finnhub:finnhub_filings`, `yfinance:yfinance_get_financials` |
| Key Metrics (ROIC, ROE 등) | `sec-edgar:get_key_metrics` | `finviz-plus:get_stock_fundamentals`, `finnhub:finnhub_company_basic_financials` |
| 세그먼트 데이터 | `sec-edgar:get_segment_data` | - |
| Company Facts (전체 XBRL) | `sec-edgar:get_company_facts` | `finnhub` |
| 10-K, 10-Q 본문 | `sec-edgar:get_filing_content`, `sec-edgar:get_filing_sections` | - |
| Recent filings | `sec-edgar:get_recent_filings` | - |

추천 도구 자동 선택: `sec-edgar:get_recommended_tools`

## 시세·OHLCV

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 실시간/일일 시세 | `finnhub:finnhub_quote` | `yfinance:yfinance_get_ticker_info`, `marketstack:marketstack_stockprice` |
| 일/주봉 OHLCV | `yfinance:yfinance_get_price_history` | `finnhub:finnhub_stock_candles`, `marketstack:marketstack_eod`, `tiingo-mcp-python:tiingo_eod_prices` |
| 52주 고저 | `finnhub:finnhub_company_basic_financials` | - |

## 공시·이벤트 (Catalyst, 산업 분석용)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 8-K 분석 (자동) | `sec-edgar:analyze_8k` | - |
| 8-K 본문 | `sec-edgar:get_filing_content` | - |
| 10-K/10-Q | `sec-edgar:get_filing_sections` | - |
| Proxy (DEF 14A) | `sec-edgar:get_recent_filings` (filter by form="DEF 14A") | - |
| Schedule 13D/13G (활동가) | `sec-edgar:search_companies` 또는 직접 filings 검색 | `finviz-plus:get_major_sec_filings` |
| Periods 비교 (YoY 등) | `sec-edgar:compare_periods` | - |

## 인사이더 거래 (Catalyst 핵심)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| Form 4 거래 내역 | `sec-edgar:get_insider_transactions` | `finnhub:finnhub_company_news`, `finviz-plus:get_insider_sec_filings`, `finviz-plus:finviz_plus_insider_feed` |
| Insider 요약 | `sec-edgar:get_insider_summary` | - |
| Sentiment 분석 | `sec-edgar:analyze_insider_sentiment` | - |
| Form 4 세부 | `sec-edgar:get_form4_details`, `sec-edgar:analyze_form4_transactions` | - |

## 산업·Peer 분석

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| Peer 종목 리스트 | `finnhub:finnhub_company_peers` | `finviz-plus:finviz_plus_quote_peer` |
| 섹터 성과 | `finviz-plus:get_sector_performance` | `finnhub`, `marketstack:marketstack_index_list` |
| 산업 성과 | `finviz-plus:get_industry_performance` | - |
| ETF 보유 (피인용 우회) | `finviz-plus:finviz_plus_quote_etf_holders`, `marketstack:marketstack_etf_holdings` | - |

## 거시 지표 (WACC 계산용)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| UST 10년 수익률 (Rf) | `fred:fred_get_series` (series_id="DGS10") | `marketstack:marketstack_bond_info`, `finnhub:finnhub_economic_data` |
| Investment Grade Credit Spread | `fred:fred_get_series` (BAMLC0A0CM) | - |
| High Yield Spread | `fred:fred_get_series` (BAMLH0A0HYM2) | - |
| Inflation (CPI) | `fred:fred_get_series` (CPIAUCSL) | - |
| GDP 성장률 | `fred:fred_get_series` (A191RL1Q225SBEA) | - |
| S&P 500 지수 (β 계산용) | `yfinance:yfinance_get_price_history` (ticker="^GSPC") | `marketstack` |

ERP는 기본 5.0% (Damodaran 최신값 확인 권장).

## 뉴스·심리 (Catalyst, 역발상 보조)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 종목 뉴스 | `finnhub:finnhub_company_news` | `marketaux:marketaux_get_news`, `yfinance:yfinance_get_ticker_news`, `tiingo-mcp-python:tiingo_news_list` |
| 시장 뉴스 | `marketaux`, `finnhub:finnhub_general_news` | `newsdata:newsdata_get_latest_news` |
| 뉴스 감성 | `adanos:adanos_news_stocks_stock` | `marketaux:marketaux_search_entities` |
| X(Twitter) 감성 | `adanos:adanos_x_stocks_stock` | - |
| Reddit 감성 | `adanos:adanos_reddit_stocks_stock` | - |
| Polymarket 베팅 | `adanos:adanos_polymarket_stocks_stock` | - |
| Form 8-K 자동 분석 | `sec-edgar:analyze_8k` | - |

## Earnings (분기 실적 - 필요 시 위임)

분기 실적 업데이트 자체는 `earnings-analysis-codex` 스킬에 위임. 본 스킬은 정규화 EBIT 산출에 사용:

| 작업 | 우선 MCP |
|---|---|
| 실적 발표 일정 | `finnhub:finnhub_earnings_calendar` |
| EPS Estimate | `finnhub:finnhub_company_eps_estimates` |
| 수익 컨센서스 | `finnhub:finnhub_company_revenue_estimates` |
| Earnings Transcript | `mcp__25aad980-...__earningsTranscript` |
| Recommendation Trends | `finnhub:finnhub_recommendation_trends` |
| Price Targets | `finnhub:finnhub_price_target` |

## 13F 보유 (정통한 가치투자자 추적)

| 작업 | 우선 MCP |
|---|---|
| 13F 보유 종목 | `mcp__25aad980-...__form13F` |

## 우선순위 의사결정 가이드

1. **재무제표가 필요?** → `sec-edgar:get_financials` 우선 (XBRL 정확). 빠른 비교는 `finnhub`.
2. **OHLCV 시계열?** → `yfinance` (편의), 대량은 `marketstack` 또는 `tiingo`.
3. **공시 본문?** → `sec-edgar:get_filing_content` + `get_filing_sections`.
4. **거시 지표?** → `fred`가 표준. 다른 도구로 검증.
5. **뉴스 감성?** → 단일 종목 → `finnhub_company_news`, 멀티소스 → `adanos` (X/Reddit/News 통합).

## 데이터 결손 시 폴백

- `sec-edgar` 실패 (NOT_FOUND 등) → CIK 확인 후 재시도, 그래도 실패 시 `finnhub:finnhub_filings`
- `yfinance` 실패 → `finnhub`, `marketstack` 순차
- 큰 회사 데이터 결손은 드물지만, 신규 상장·M&A 직후 종목은 데이터 불완전할 수 있음 → 사용자에게 데이터 한계 알림

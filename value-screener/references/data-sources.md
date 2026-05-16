# Data Sources Reference

---

## 1. 스프레드시트 컬럼 매핑

| 필드 | 한국어 | 영어 |
|------|------|------|
| per | PER, 주가수익비율 | PER, P/E, pe_ratio |
| pbr | PBR, 주가순자산비율 | PBR, P/B, pb_ratio |
| roe | ROE, 자기자본이익률 | ROE, return_on_equity |
| eps_growth | EPS성장률 | eps_growth, eps_cagr |
| debt_equity | D/E비율, 부채비율 | D/E, debt_equity |
| current_ratio | 유동비율 | current_ratio |
| dividend_years | 배당연수 | dividend_years |
| ev | EV, 기업가치 | EV, enterprise_value |
| ebit | EBIT, 영업이익 | EBIT, operating_income |
| ebitda | EBITDA | EBITDA |
| fcf | FCF, 잉여현금흐름 | FCF, free_cash_flow |
| ncav | NCAV, 순유동자산 | NCAV, net_current_asset_value |
| tangible_bv | 유형순자산, 유형BV | tangible_book |
| price | 현재가, 주가 | price, current_price |
| high_52w | 52주고가 | high_52w, week52_high |
| low_52w | 52주저가 | low_52w, week52_low |
| revenue_growth | 매출성장률 | revenue_growth |
| quarterly_eps_growth | 분기EPS성장 | quarterly_eps_growth |
| relative_strength_6m | 6개월수익률 | return_6m, rs_6m |
| interest_coverage | 이자보상배율 | interest_coverage |
| listing_years | 상장연수 | listing_years |
| roc | ROC, 투자자본수익률 | ROC, return_on_capital |
| ey | EY, 이익수익률 | EY, earnings_yield |
| peg | PEG | PEG, peg_ratio |

인식 우선순위: 정확매칭 → 대소문자무시 → 특수문자제거 → 부분문자열

---

## 2. MCP 도구 가이드

### Kiwoom (mcp__kiwoom-openapi__*)
- kiwoom_stock_basic_info(stock_code): PER/PBR/ROE/EPS 기본정보
- kiwoom_stock_daily_price(stock_code, start, end): 52주 고저가 계산용
- kiwoom_rank_volume / kiwoom_rank_price_change: 랭킹 조회
- kiwoom_stock_info_list(market): 전종목 리스트

### Korea Stock (mcp__korea-stock__*)
- get_corp_code(company_name): DART 법인코드
- get_financial_statement(corp_code, year, report_type): 재무제표 상세
- get_stock_base_info / get_disclosure_list / get_market_type

### KRX (mcp__krx__*)
- krx_get_sto_stk_isu_base_info(date): KOSPI 전종목 PER/PBR 일괄
- krx_get_sto_ksq_isu_base_info(date): KOSDAQ 전종목 일괄

### Naver Stock (mcp__naver-stock__*)
- naver_stock_get_quote(stock_code): 현재가
- naver_stock_list_rankings(category, market): 랭킹 (rise/fall/per/pbr/roe)
- naver_stock_search_codes(keyword): 코드 검색

### KIS (mcp__kis-openapi-mcp__*)
- kis_domestic_stock: 실시간 국내 주식
- kis_overseas_stock: 해외 주식

---

## 3. 시나리오별 조합

**A — KOSPI 전체 가치주**: krx 전종목 → PER/PBR 필터 → get_financial_statement → Graham/Buffett/Greenblatt
**B — 단일 종목 심층**: kiwoom_basic_info → get_financial_statement 5년 → daily_price 52주 → 8개 마스터
**C — 모멘텀 발굴**: naver_rankings("rise") → daily_price 신고가 → financial_statement 분기EPS → Momentum Score
**D — 역발상 바닥**: naver_rankings("fall") → krx 하위필터 → NCAV/유형순자산 계산 → Schloss/Klarman/Contrarian

---

## 4. 데이터 대체 처리

| 지표 | 대체 |
|-----|------|
| NCAV | 유동자산 - 총부채 |
| EBIT | 영업이익 근사 |
| EV | 시총 + 장기부채 - 현금 |
| ROC | ROE x (1 - D/A비율) |
| PEG | PER / 3년EPS CAGR |
| 유형순자산 | 총자산 - 무형자산 - 부채 |
| FCF | 영업현금흐름 - CAPEX |
| 이자보상배율 | EBIT / 이자비용 |
| 52주고저 | kiwoom_stock_daily_price 계산 |
| 상대강도 | 종목수익률 - 코스피수익률 |

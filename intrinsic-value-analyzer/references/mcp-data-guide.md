# MCP 데이터 수집 가이드 (MCP Data Acquisition Guide)

## 거래소별 MCP 선택 매핑

| 거래소 | 주 MCP | 보조 MCP |
|---|---|---|
| KRX (KOSPI/KOSDAQ) | korea-stock | naver-stock, krx |
| NYSE/NASDAQ | FMP (25aad980) | finnhub, eodhd, yfmcp |
| 홍콩/중국 | FMP | eodhd |
| 일본 | japan-corporate | eodhd |
| 기타 글로벌 | eodhd | FMP |

---

## 한국 주식 데이터 수집

### 1. 기업 기본정보 & 주가
```
mcp__korea-stock__get_stock_base_info
  → corp_code (DART 코드) 또는 stock_code 입력
  → 반환: 기업명, 대표자, 업종, 상장일, 자본금

mcp__naver-stock__naver_stock_get_quote
  → symbol: 종목코드 (예: "005930" 삼성전자)
  → 반환: 현재가, 시가총액, PER, PBR, EPS, BPS, 배당수익률

mcp__korea-stock__get_stock_trade_info
  → 반환: 거래량, 거래대금, 외국인 보유 비율
```

### 2. 재무제표 (최근 5개년)
```
mcp__korea-stock__get_financial_statement
  → corp_code: DART 고유번호
  → bsns_year: "2024" (사업연도)
  → reprt_code: "11011" (사업보고서) or "11013" (1Q) or "11012" (반기)
  → fs_div: "CFS" (연결) or "OFS" (별도)
  → 반환: 손익/재무상태/현금흐름 XBRL 데이터

mcp__korea-stock__get_corp_code
  → corp_name으로 DART 코드 검색 (corp_code 모를 때)
```

### 3. 공시 정보
```
mcp__korea-stock__get_disclosure_list
  → 최근 공시 확인 (주요사항, 사업보고서 등)

mcp__korea-stock__get_disclosure
  → 특정 공시 전문 조회
```

### 4. 업종 비교 (한국)
```
mcp__kiwoom-openapi__kiwoom_sector_current_price
  → sector_code로 업종 지수 조회

mcp__naver-stock__naver_stock_list_rankings
  → type: "PER", "PBR" 등으로 업종 내 비교 가능
```

### 5. 금리 / 거시 (한국)
```
mcp__ecos__ecos_statistic_resolve_and_fetch
  → 국고채 10년 수익률: 통계코드 검색 후 조회
  → 기준금리, CPI 등 한국은행 데이터

mcp__ecos__ecos_statistic_search
  → keyword: "국고채" or "기준금리" 검색
```

---

## 해외 주식 데이터 수집 (FMP 중심)

### 1. 기업 프로필 & 주가
```
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__profile-symbol
  → symbol: "AAPL", "MSFT" 등
  → 반환: 기업 개요, 섹터, 시총, β, 직원수

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__quote
  → 현재가, 변동, 시가총액, 52주 고/저
```

### 2. 재무제표 (최근 5개년)
```
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__income-statement
  → symbol, period: "annual" or "quarter", limit: 5

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__balance-sheet-statement
  → 자산/부채/자기자본 상세

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__cashflow-statement
  → 영업현금흐름, CAPEX, 잉여현금흐름

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__income-statements-ttm
  → TTM (최근 12개월) 손익 — 가장 최신 실적 반영
```

### 3. 핵심 밸류에이션 지표
```
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__key-metrics-ttm
  → PE, PB, PS, EV/EBITDA, ROE, ROIC, FCF Yield 등 TTM 기준

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__key-metrics
  → 연도별 핵심 지표 (트렌드 파악)

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__enterprise-values
  → EV, EV/EBITDA, EV/Sales 연도별
```

### 4. 성장률 및 재무비율 성장
```
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__income-statement-growth
  → 매출/영업이익/순이익 성장률 추이

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__balance-sheet-statement-growth
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__cashflow-statement-growth
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__financial-statement-growth
  → 종합 성장 지표
```

### 5. DCF 참조값 (FMP 자체 DCF)
```
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__dcf-levered
  → FMP의 레버드 DCF 결과 (참고용 — 독립 검증 필요)

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__dcf-advanced
  → 고급 DCF 파라미터 설정 가능
```

### 6. 업종/섹터 비교
```
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__industry-PE-snapshot
  → 현재 업종별 P/E

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__sector-PE-snapshot
  → 섹터별 P/E

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__peers
  → 피어 기업 목록

mcp__tradingview-screener__tradingview_scan
  → 동일 섹터 필터 + 멀티플 스캔 (피어 그룹 구성)
```

### 7. 분석가 추정치 & 등급
```
mcp__25aad980-dcfe-4508-b9dc-86a30452caca__financial-estimates
  → 컨센서스 EPS/매출 추정치 (향후 2년)

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__price-target-consensus
  → 분석가 목표주가 평균/최고/최저

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__grades-summary
  → 매수/보유/매도 등급 분포
```

---

## 금리/거시 데이터 (FRED)

```
mcp__fred__fred_get_series
  → series_id: "DGS10"  (미국 10년 국채 수익률)
  → series_id: "DGS2"   (미국 2년 국채)
  → series_id: "FEDFUNDS" (연방기금금리)
  → series_id: "T10YIE"   (10년 기대 인플레이션)
  → series_id: "CPIAUCSL"  (소비자물가지수)

mcp__25aad980-dcfe-4508-b9dc-86a30452caca__treasury-rates
  → 미국 국채 전 만기 금리 일괄 조회
```

**ERP 참고**: Damodaran(NYU) 사이트 기준값 사용 — 한국 ~5.5%, 미국 ~5.0% (연간 업데이트)

---

## 핀비즈 / TradingView 피어 스캔

```
mcp__finviz-plus__get_stock_fundamentals
  → 개별 종목 종합 펀더멘털

mcp__finviz-plus__finviz_plus_quote_peer
  → 피어 기업 빠른 비교

mcp__tradingview-screener__tradingview_scan
  → filters: [{field: "sector", operation: "equal", value: "Technology"}]
  → columns: ["close", "P.E", "EV.EBITDA", "ROE.TTM", "revenue_growth"]
  → 섹터 내 멀티플 분포 파악
```

---

## 데이터 미확보 시 대안 처리

| 상황 | 대안 |
|---|---|
| 재무제표 없음 | 최근 공시/IR 자료 텍스트에서 추출 |
| β 없음 | 업종 평균 β 사용 (un-lever → re-lever) |
| 피어 없음 | 글로벌 유사 기업으로 대체 |
| 성장률 추정 불가 | GDP 성장률 + 인플레이션 = 보수적 기본값 |
| 세율 불명 | 법정 세율 사용 (한국 22%, 미국 21%) |
| ERP 불명 | 한국 5.5%, 미국 5.0%, 신흥국 6~8% |

→ 대안 사용 시 **반드시 가정으로 명시** 후 민감도에 포함

---

## 데이터 수집 순서 권장

```
1. 기업 식별 → 티커/코드 확인
2. 프로필 조회 → 섹터, 시총, β
3. 재무제표 5년 → 손익/재무상태/현금흐름
4. 현재 주가 + 시가총액
5. TTM 핵심 지표 (PE, PB, EV/EBITDA, ROE, ROIC, FCF)
6. 피어 그룹 + 업종 멀티플 중앙값
7. 금리 (Rf) + ERP
8. 분석가 컨센서스 (참고용)
```

# 07. 데이터 수집 · MCP 호출 가이드

> **언제 이 파일을 읽을까?**
> - Mode B STEP 1 자료 수집 단계 진입 시
> - 기업명/티커가 주어졌는데 재무 데이터가 아직 없을 때
> - 거시지표·뉴스·리서치 보조 자료가 필요할 때
>
> **핵심 원칙:**
> - 본 스킬은 MCP를 **직접 호출하지 않고**, Claude Desktop이 보유한 MCP를 **호출하도록 안내**합니다.
> - MCP 응답이 실패하거나 스키마가 바뀌어 있으면 2순위·3순위로 자동 폴백합니다.
> - 모든 데이터 수집은 **출처를 명시**하고 수치와 함께 보고서에 기록합니다.

---

## 1. 한국 상장기업 데이터 수집

### 1.1 korea-stock MCP (DART) — 최우선 · 공식 공시 원본

DART는 한국 법정 공시이므로 **재무제표 원본 진실의 원천**. Mode B 분석은 DART 원본부터 시작합니다.

```text
// 기업 고유코드(CORP_CODE) 확인
korea-stock:get_corp_code({ corp_name: "삼성전자" })
  → { corp_code: "00126380", ... }

// 연간 재무제표 (사업보고서)
korea-stock:get_financial_statement({
  corp_code: "00126380",
  bsns_year: "2024",
  reprt_code: "11011",       // 11011: 사업보고서, 11012: 반기, 11013: 1분기, 11014: 3분기
  fs_div: "CFS"              // CFS: 연결, OFS: 별도
})

// 공시 목록 (최근 연도)
korea-stock:get_disclosure_list({
  corp_code: "00126380",
  bgn_de: "20200101",
  end_de: "20241231"
})
```

### 1.2 open-dart-reader MCP — DART 심층 텍스트·주석 추출

사업보고서 **주석·서술 섹션·XBRL 세부 계정**이 필요할 때.

```text
// 기업 검색 + 고유코드 조회
open-dart-reader:opendart_company_by_name({ name: "삼성전자" })
open-dart-reader:opendart_find_corp_code({ keyword: "삼성전자" })

// 재무제표 모든 계정 (세부 XBRL)
open-dart-reader:opendart_finstate_all({
  corp_code: "00126380",
  bsns_year: "2024",
  reprt_code: "11011"
})

// 사업보고서 섹션 추출 (주석·MD&A·사업의 내용)
open-dart-reader:opendart_extract_document_sections({
  rcept_no: "20250314000XXX",     // 공시 접수번호
  sections: ["사업의 내용", "주석"]
})

// 첨부문서 다운로드 (감사보고서 PDF)
open-dart-reader:opendart_attach_files({ rcept_no: "..." })

// 주요주주·임원 현황
open-dart-reader:opendart_major_shareholders({ corp_code: "00126380" })
```

### 1.3 KIS MCP (한국투자증권) — 실시간 재무비율·시세

> ⚠️ 모든 KIS API 호출에 `env_dv: "real"` 파라미터 필수 포함

```text
// 재무비율 (연간 or 분기)
kis:domestic_stock({
  api_id: "FHKST66430100",
  params: {
    fid_input_iscd: "005930",
    fid_div_cls_code: "0",          // 0: 연간, 1: 분기
    env_dv: "real"
  }
})

// 손익계산서
kis:domestic_stock({
  api_id: "FHKST66430200",
  params: { fid_input_iscd: "005930", fid_div_cls_code: "0", env_dv: "real" }
})

// 주식 기본 정보 (시총·상장주식수 등)
kis:domestic_stock({
  api_id: "CTPF1604R",
  params: { pdno: "005930", env_dv: "real" }
})
```

### 1.4 Kiwoom / naver-stock / pykrx — 보조 데이터

```text
// Kiwoom (KIS 미제공 데이터 폴백)
kiwoom:kiwoom_stock_basic_info({ stock_code: "005930", normalize: true })
kiwoom:kiwoom_stock_daily_price({ stock_code: "005930", normalize: true })

// naver-stock (투자자별 매매동향, 간이 시세)
naver-stock:naver_stock_get_quote({ code: "005930" })

// pykrx (과거 가격·시총·펀더멘털 벌크 조회)
pykrx:get_stock_ohlcv({ ticker: "005930", fromdate: "20200101", todate: "20241231" })
pykrx:get_market_fundamental_by_date({ ticker: "005930", fromdate: "20200101", todate: "20241231" })
```

---

## 2. 글로벌 기업 데이터 수집

### 2.1 sec-edgar MCP — 미국 상장기업 최우선

```text
// 티커 → CIK 변환
sec-edgar:get_cik_by_ticker({ ticker: "AAPL" })

// 최근 10-K (연간보고서) 목록
sec-edgar:get_recent_filings({ cik: "0000320193", form_type: "10-K", count: 5 })

// 재무제표 전체 (3재무제표)
sec-edgar:get_financials({ cik: "0000320193", filing_type: "10-K" })

// 핵심 지표 자동 추출
sec-edgar:get_key_metrics({ cik: "0000320193" })

// 세그먼트 데이터 (사업부별 매출)
sec-edgar:get_segment_data({ cik: "0000320193" })

// 8-K 이벤트 분석 (경영 중요 변동)
sec-edgar:analyze_8k({ cik: "0000320193" })

// 내부자 거래 요약 (Form 4)
sec-edgar:get_insider_summary({ cik: "0000320193" })
```

### 2.2 Financial Modeling Prep MCP — 재무비율·Peer 리스트

```text
// 3재무제표 (연간 5개년)
Financial Modeling Prep:statements({
  symbol: "AAPL",
  statement: "income",      // income / balance / cashflow
  period: "annual",
  limit: 5
})

// 전체 재무비율
Financial Modeling Prep:company({ symbol: "AAPL", endpoint: "ratios", period: "annual" })

// Peer 리스트 자동 추출
Financial Modeling Prep:company({ symbol: "AAPL", endpoint: "peers" })

// DCF 추정값 (참고용 — 심층 DCF는 intrinsic-value-analyzer 위임)
Financial Modeling Prep:discountedCashFlow({ symbol: "AAPL" })
```

### 2.3 yfmcp (yfinance) — 주가·시총·배당 이력

```text
yfmcp:yfinance_get_ticker_info({ ticker: "AAPL" })
yfmcp:yfinance_get_price_history({ ticker: "AAPL", period: "5y", interval: "1mo" })
yfmcp:yfinance_get_ticker_news({ ticker: "AAPL" })
```

### 2.4 finnhub — 재무 메트릭·EPS 컨센서스·애널리스트 추천

```text
finnhub:finnhub_company_profile2({ symbol: "AAPL" })
finnhub:finnhub_company_basic_financials({ symbol: "AAPL", metric: "all" })
finnhub:finnhub_company_peers({ symbol: "AAPL" })
finnhub:finnhub_recommendation_trends({ symbol: "AAPL" })
finnhub:finnhub_price_target({ symbol: "AAPL" })
```

### 2.5 japan-corporate — 일본 상장기업 (EDINET)

```text
japan-corporate:search_company({ keyword: "Toyota" })
japan-corporate:get_edinet_reports({ corporate_number: "...", year: "2024" })
japan-corporate:get_company_finance({ corporate_number: "...", year: "2024" })
```

---

## 3. 거시경제·산업 데이터

### 3.1 ecos (한국은행) — 국내 거시지표

```text
ecos:ecos_statistic_search({ keyword: "GDP 성장률" })
ecos:ecos_statistic_resolve_and_fetch({
  stat_name: "국내총생산",
  cycle_type: "A",              // A: 연간, Q: 분기, M: 월간
  start_time: "2020",
  end_time: "2024"
})
```

### 3.2 kosis (통계청) — 산업·업종 통계

```text
kosis:kosis_statistics_search({ search_nm: "제조업 생산지수" })
kosis:kosis_statistics_data({ list_id: "MT_ZTITLE", itmId: "T40301" })
```

### 3.3 fred (미국 연준) — 글로벌 거시지표

```text
fred:fred_search({ search_text: "corporate profit margin" })
fred:fred_get_series({
  series_id: "CP",
  observation_start: "2020-01-01",
  observation_end: "2024-12-31"
})
```

### 3.4 oecd-data — OECD 국가별 비교

```text
oecd-data:oecd_list_dataflows()
oecd-data:oecd_get_data({ dataflow: "...", filters: {...} })
```

---

## 4. 리서치·뉴스·뉴스플로우

### 4.1 korean-research — 국내 증권사 리포트

```text
korean-research:research_scan_recent_reports({ company: "삼성전자", days: 30 })
korean-research:research_extract_key_issues({ company: "삼성전자" })
korean-research:research_get_report_digest({ report_id: "..." })
```

### 4.2 marketaux / finnhub / newsdata — 뉴스 메타데이터

```text
marketaux:marketaux_get_news({ symbols: "005930.KS" })
finnhub:finnhub_company_news({ symbol: "AAPL", from: "2024-01-01", to: "2024-12-31" })
newsdata:newsdata_get_market_news({ q: "Samsung Electronics", language: "ko" })
```

### 4.3 adanos — 소셜 센티먼트

```text
adanos:adanos_get_stock_sentiment_overview({ ticker: "AAPL" })
adanos:adanos_reddit_stocks_stock({ ticker: "AAPL" })
```

---

## 5. 우선순위 매트릭스 (기업 국적 × 데이터 유형)

```
데이터 유형          | 한국 상장         | 미국 상장              | 일본 상장       | 글로벌
────────────────────|-----------------|----------------------|---------------|-----
재무제표 원본       | korea-stock (1) | sec-edgar (1)        | japan-corp (1)| —
주석·서술 섹션      | open-dart (1)   | sec-edgar filing (1) | japan-corp (1)| —
재무비율             | KIS (1)          | FMP (1), finnhub (2) | japan-corp (1)| FMP
시계열 주가          | pykrx (1)        | yfmcp (1)             | yfmcp (2)      | yfmcp
Peer 리스트          | KIS 업종(1)      | FMP peers(1)          | FMP(2)         | FMP, finnhub
애널리스트 컨센서스 | korean-research | finnhub(1), FMP(2)    | —              | finnhub
뉴스                 | marketaux, newsdata | finnhub, marketaux | — | marketaux
거시지표             | ecos (1), kosis(2)| fred (1)             | —              | fred, oecd-data
```

> 1순위가 실패하면 2순위로 폴백. 재무제표 원본은 **법정 공시 우선** — DART / SEC는
> 타 상용 데이터 서비스보다 정확합니다.

---

## 6. 데이터 수집 체크리스트 (Mode B STEP 1)

```
□ 기업 고유코드/CIK 확인
□ 최근 5개년 연간 재무제표 (연결)
□ 최근 4분기 분기 실적 (트렌드 확인용)
□ 감사보고서 감사의견 + 핵심감사사항(KAM)
□ 주석: 수익인식 정책, 금융상품, 특수관계자 거래, 우발부채
□ 업종 분류 코드 (KSIC / SIC / GICS)
□ 최근 6개월 공시 주요 이슈 (M&A·유상증자·회계정책 변경)
□ 필요 시 Peer 3~5개사 데이터
□ 필요 시 거시지표 · 업종 지표
```

---

## 7. 수집 실패 시 폴백 원칙

1. **1순위 MCP 실패** → 2순위 MCP 재시도, 스키마 차이 반영
2. **모든 MCP 실패** → `alphaear-search` 스킬 또는 사용자에게 **직접 재무제표 첨부 요청**
3. **일부 데이터만 수집** → 분석 가능 범위를 명시하고, **누락 데이터로 인해 판단 유보된 항목**을 보고서에 명기
4. **환율·기준연도 불일치** → 기능통화 기준 원본값을 우선 기재하고 환산값을 별도 표기

---

## 8. 데이터 품질 원칙

- **회계 기준 일관성**: K-IFRS / US GAAP / J-GAAP 간 비교 시 §5/§2.2(05_industries_peer.md) 정규화 적용
- **기간 정합성**: 3월 결산 vs 12월 결산 기업 비교 시 대응 회계연도 매칭
- **중복 수집 방지**: 동일 지표를 여러 MCP에서 받았다면 **공식 공시(DART/SEC) 우선**, 그 외는 참고용
- **출처 메모**: 각 수치 옆에 `(출처: DART 2024 사업보고서 p.XX)` 수준의 주석 유지

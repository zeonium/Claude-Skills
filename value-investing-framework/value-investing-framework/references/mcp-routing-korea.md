# 한국 시장 MCP 라우팅

KOSPI/KOSDAQ 종목 분석 시 사용할 MCP 도구표. 우선 → 백업 순.

## 종목 식별·검색

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 종목명 → 코드 변환 | `naver-stock:naver_stock_search_codes` | `korea-stock-mcp:get_corp_code`, `finance-data-reader:fdr_resolve_symbol` |
| 코드 → 기업 기본정보 | `korea-stock-mcp:get_stock_base_info` | `kiwoom:kiwoom_stock_basic_info`, `naver-stock:naver_stock_get_quote` |
| 시장 구분 (KOSPI/KOSDAQ) | `korea-stock-mcp:get_market_type` | `krx:krx_get_sto_stk_isu_base_info` |

종목 식별이 모호하면 `cross-market-equity-router` 스킬에 위임.

## 재무제표 (AV·EPV 계산용)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 5년 재무제표 (B/S, I/S, C/F) | `open-dart-reader:opendart_finstate_all` | `korea-stock-mcp:get_financial_statement` |
| 단일 연도 상세 | `open-dart-reader:opendart_finstate` | - |
| XBRL 분류체계 | `open-dart-reader:opendart_xbrl_taxonomy` | - |
| 우발부채 등 주석 | `open-dart-reader:opendart_extract_document_sections` (사업보고서 본문 검색) | - |

DART 회사 코드 변환:
- `open-dart-reader:opendart_find_corp_code` (회사명 → corp_code)
- `open-dart-reader:opendart_resolve_corp` (티커/회사명 통합)

## 시세·OHLCV (역발상 적합성, 안전마진 계산용)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 실시간 시세 | `naver-stock:naver_stock_get_quote` | `kiwoom:kiwoom_stock_basic_info`, `krx` |
| 일/주봉 OHLCV | `finance-data-reader:fdr_data_reader` | `kiwoom:kiwoom_chart_ohlcv`, `krx:krx_get_sto_stk_bydd_trd` |
| 52주 고저 | `naver-stock:naver_stock_get_quote` (info에 포함) | - |

## 공시·이벤트 (Catalyst, 산업 분석용)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 공시 목록 | `open-dart-reader:opendart_list` | - |
| 특정 공시 본문 | `open-dart-reader:opendart_document` | `opendart_document_all` |
| 주요사항보고 (M&A 등) | `open-dart-reader:opendart_event` | - |
| 최대주주·임원 변동 | `open-dart-reader:opendart_major_shareholders`, `opendart_major_shareholders_exec` | - |
| 사업보고서 등 정기공시 | `open-dart-reader:opendart_report` | - |
| 첨부 파일 | `open-dart-reader:opendart_attach_file_list`, `opendart_attach_files` | - |

## 산업 분류

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 산업 코드 | `korea-stock-mcp:get_market_type` (KSIC 포함) | `krx:krx_get_sto_stk_isu_base_info` |
| 산업 통계 | `kosis:kosis_statistics_data` | - |
| 산업 동향 (정성) | `market-research` 스킬 위임 | - |

## 거시 지표 (WACC 계산용)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 국고채 10년 수익률 (Rf) | `ecos:ecos_statistic_resolve_and_fetch` (검색어: "국고채 10년") | - |
| 회사채 등급별 수익률 (Rd) | `ecos:ecos_statistic_search` | - |
| KOSPI 지수 (β 계산용) | `finance-data-reader:fdr_data_reader` (ticker="KS11") | `kiwoom:kiwoom_sector_index_all` |
| 인플레이션·CPI | `ecos`, `kosis` | `fred` (글로벌) |

ECOS는 한 번에 통계 코드를 찾기 어려울 수 있다. 다음 순서로 접근:
1. `ecos:ecos_statistic_search`로 키워드 검색
2. `ecos:ecos_statistic_meta`로 메타 확인
3. `ecos:ecos_statistic_resolve_and_fetch`로 직접 호출

## 뉴스·심리 (역발상, Catalyst 보조)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 종목 뉴스 | `naver-doc:naver_doc_search`, `marketaux` | `korean-research:research_scan_recent_reports` |
| 뉴스 감성·트렌드 | `adanos:adanos_news_stocks_stock`, `adanos:adanos_x_stocks_stock` | `alphaear-news` 스킬 |
| 증권사 리포트 | `korean-research:research_scan_recent_reports` | - |
| 커뮤니티 (반응 참고) | `adanos:adanos_reddit_stocks_stock` (글로벌만), 한국 커뮤니티는 별도 도구 부족 | - |

## 내부자·주주 (Catalyst 핵심)

| 작업 | 우선 MCP | 백업 |
|---|---|---|
| 임원·주요주주 거래 | `open-dart-reader:opendart_major_shareholders_exec` | - |
| 5% 보유 신고 | `open-dart-reader:opendart_major_shareholders` | - |

## 우선순위 의사결정 가이드

1. **재무제표가 필요한가?** → `open-dart-reader` 먼저, 실패 시 `korea-stock-mcp`
2. **현재 시세만 필요?** → `naver-stock` 가장 빠름
3. **장기 OHLCV?** → `finance-data-reader` (Python pandas 친화)
4. **공시 본문 검색?** → `open-dart-reader:opendart_extract_document_sections`
5. **거시 데이터?** → 한국 → `ecos`/`kosis`, 미국 또는 글로벌 → `fred`

## 호출 시 주의

- 한국 종목 코드는 6자리, 미국과 충돌 안 함
- DART는 corp_code (8자리)와 stock_code (6자리)가 다름. 호출 전 정규화 필요
- 영업일/거래일 차이로 데이터 불일치 가능 → 가장 최근 가능한 날짜 사용

## 데이터 결손 시 폴백

- DART 5년 재무 실패 → `korea-stock-mcp`로 백업, 그것도 실패 시 3년만 사용
- 시세 실패 → `naver-stock` → `kiwoom` → `krx` 순차
- 공시 검색 실패 → 사용자에게 회사명 정확성 확인 요청

---
name: value-investing-framework
description: 그린월드(Bruce Greenwald)·그레이엄 학파 가치투자 의사결정 프레임워크 전담 오케스트레이터. 단일 기업 또는 종목 리스트(text/csv/xlsx)를 받아 자산가치(AV)→수익력가치(EPV)→성장가치 3계층 평가와 AV vs EPV 매트릭스 Case A/B/C 분류로 투자 적합성을 판정하고, 적합 종목에 심층 분석+안전마진 기반 BUY/HOLD/AVOID 투자전략을 수립한다. 한국(KOSPI/KOSDAQ)+미국(NYSE/NASDAQ) 지원. 활성화 키워드 -- "가치투자 프레임워크", "value investing framework", "그린월드", "Greenwald", "AV vs EPV", "EPV", "Earnings Power Value", "재생산 비용", "Reproduction Cost", "청산 가치", "Liquidation Value", "Case A/B/C", "가치 함정", "Value Trap", "프랜차이즈 비즈니스", "franchise value", "투자 적합성/부적합 판정", "안전마진 평가", "BUY/HOLD/AVOID", "투자전략 수립"; 종목명/종목코드 + "가치투자/저평가/투자대상 선별" 맥락; CSV/Excel/text 종목 리스트 + "가치투자 스크리닝/심층 분석" 요청. [위임] 단순 메서드 valuation(DCF/RIM/SOTP/rNPV/Real Options)만은 intrinsic-value-analyzer; 멀티 대가 점수 랭킹(그레이엄·버핏·그린블라트·린치)은 value-screener; 해자 정성 분석 단독은 eco-moat-codex; 재무 비율·DuPont·Z-Score 진단 단독은 financial-analysis; 종목 식별·시장 라우팅 단독은 cross-market-equity-router; 분기 실적 업데이트만은 earnings-analysis-codex 사용. 본 스킬은 그린월드 3계층+매트릭스 Case 분류+의사결정 트리+투자전략 워크플로우 전체를 전담한다.
---

# Value Investing Framework (Greenwald · Graham)

브루스 그린월드와 벤저민 그레이엄의 가치투자 의사결정 프레임워크를 충실히 구현하는 오케스트레이터다. DCF의 먼 미래 불확실성을 의도적으로 회피하고, 신뢰성 있는 데이터부터 순차적으로(자산 → 수익력 → 성장) 가치를 추정한다. 단일 종목 심층 분석과 종목 리스트 스크리닝을 모두 지원한다.

## Operating Principle

- **DCF 회피 원칙**: 먼 미래의 추정 현금흐름에 의존하지 않는다. 현재 확인 가능한 자산과 수익력부터 평가한다.
- **3계층 순차 평가**: 자산가치(AV) → 수익력가치(EPV) → 성장가치(Growth). 성장가치는 Case C 프랜차이즈에서만 추가한다.
- **의사결정 트리**: AV vs EPV 비율로 Case A/B/C를 분류하고 각각 다른 후속 분석을 수행한다.
- **사실·추정·판단 분리**: 보고서에서 데이터(facts), 계산값(derived), 추정값(estimates), 판단(judgment)을 명시적으로 구분한다.
- **보수성 우선**: 가치 추정은 항상 보수적으로 한다. 안전마진은 그 다음에 더 보수적으로 확보한다.
- **오케스트레이션 원칙**: 종목 식별·재무 진단·해자 정성·일반 valuation 메서드 등은 기존 전문 스킬에 위임하고, 본 스킬은 그린월드 워크플로우 전담에 집중한다.
- **비-자문 고지**: 최종 응답에 정보 제공 목적이며 투자 자문이 아님을 반드시 명시한다.

## Mode Selection

입력을 보고 다음 두 모드 중 하나로 진입한다.

| 모드 | 트리거 | 처리 |
|---|---|---|
| **Mode A** Full Deep Dive | 단일 종목명 또는 단일 종목코드 | 그린월드 풀 프레임워크 적용 |
| **Mode B** List Screening | 2개 이상 종목, CSV/Excel/text 파일, "리스트", "후보들" | 2-Stage Pipeline (Quick Screen → Pass 종목 Deep Dive) |

모호한 경우(예: "삼성전자 005930" 같이 단일 종목이지만 두 표기 동시) Mode A로 진입한다.

상세 절차:
- Mode A → `references/mode-a-deep-dive.md` 로드
- Mode B → `references/mode-b-list-screening.md` 로드

## Workflow (Mode A 풀 흐름)

```
[입력 수신]
   │
[1] 종목 정규화·시장 식별
   ├ 한국 6자리(예: 005930) → KRX 라우팅
   ├ 미국 티커(예: AAPL) → SEC/yfinance 라우팅
   ├ 모호 시 cross-market-equity-router 위임
   │
[2] 기업·산업 개요 + 역발상 적합성
   ├ MCP로 기본 정보 수집
   ├ 52주 위치, PER/PBR 분위, 모멘텀
   ├ 산업 분류 (사양 vs 존속)
   │
[3] 자산가치 AV 계산  → references/asset-value-calculation.md
   ├ 사양 산업 → 청산가치 (scripts/compute_av_liquidation.py)
   ├ 존속 산업 → 재생산 비용 (scripts/compute_av_reproduction.py)
   │
[4] 수익력가치 EPV 계산  → references/epv-calculation.md
   ├ 영업이익 정규화 (5~7년 평균, 일회성 제외)
   ├ D&A vs Maintenance CapEx 조정
   ├ WACC 산정 (scripts/compute_wacc.py)
   ├ EPV = NOPAT / WACC  (scripts/compute_epv.py)
   │
[5] AV vs EPV 매트릭스 분류  → references/matrix-classification.md
   ├ EPV/AV < 0.7  → Case A (가치 함정 의심)
   ├ 0.7 ≤ EPV/AV ≤ 1.3 → Case B (평범)
   ├ EPV/AV > 1.3 → Case C (프랜차이즈)
   └ ROIC vs WACC 교차 검증
   │
[6] Case별 분기 분석
   ├ Case A → references/case-a-catalyst.md   (촉매제 검색, 위임: financial-analysis 보조)
   ├ Case B → 평범 판정, 내재가치 = AV/EPV 평균
   ├ Case C → references/case-c-franchise.md  (위임: eco-moat-codex, intrinsic-value-analyzer)
   │
[7] 안전마진 평가  → scripts/compute_margin_of_safety.py
   ├ 보수적 내재가치 vs 현 주가
   ├ 1/3 할인 → 검토, 1/2 할인 → 강력
   │
[8] 최종 의견 BUY/HOLD/AVOID
   ├ 매수가격대, 분할매수 전략
   ├ 모니터링 포인트, 리스크
   │
[9] 보고서 출력  → assets/report-template-ko.md
   └ (선택) xlsx/pptx 위임
```

## Input Parsing

- 단일 종목: 메시지 본문 또는 첨부 파일에서 종목명/코드 추출
- 종목 리스트 파일: `scripts/parse_ticker_list.py` 사용 (csv/xlsx/txt 모두 처리)
- 입력 형식 자동 판별 가이드: `references/input-parsing.md`

종목코드 정규식:
- `^\d{6}$` → 한국 (KOSPI/KOSDAQ)
- `^[A-Z]{1,5}$` → 미국 (NYSE/NASDAQ)
- 종목명만 → 검색 MCP로 코드 변환 (`naver-stock:search_codes`, `finnhub:finnhub_symbol_lookup`)

## MCP Routing

시장별 우선 MCP는 다음 reference 문서에 정리되어 있다:
- 한국 시장: `references/mcp-routing-korea.md`
- 미국 시장: `references/mcp-routing-us.md`

핵심 한 줄 요약:
- 한국 재무제표: `open-dart-reader:opendart_finstate_all`
- 미국 재무제표: `sec-edgar:get_financials`
- 한국 시세: `naver-stock`, `finance-data-reader`
- 미국 시세: `yfinance`, `finnhub`
- 무위험수익률: `fred:fred_get_series(DGS10)` (미국), `ecos` (한국)

## Delegation Map (다른 스킬과 합주)

본 스킬은 다음 시점에 다른 스킬을 호출한다. 워크플로우 도중 자연스럽게 위임하라.

| 시점 | 호출 대상 | 목적 |
|---|---|---|
| 종목·시장 모호 | `cross-market-equity-router` | 정규화·라우팅 |
| Stage 1 빠른 재무 진단 보조 | `financial-analysis` | DuPont/Altman Z/Beneish M |
| Case A 정성 분석 보강 | `qualitative-company-analysis-codex` | 경영진·사업모델 진단 |
| Case C 해자 정성 검증 | `eco-moat-codex` (`anthropic-skills:eco-moat-ai`) | Buffett 게이트, owner earnings |
| Case C 성장가치 Reverse DCF 교차 검증 | `intrinsic-value-analyzer` | market-implied expectations |
| 보고서 Excel 산출 (사용자 요청 시) | `xlsx` | 계산 내역 워크북 |
| 차트 시각화 (사용자 요청 시) | `plotly` 또는 `seaborn` | AV/EPV 비교 차트 등 |

본 스킬이 **직접 하지 말아야 할 것**:
- 단순 DCF/RIM/DDM/SOTP/rNPV 메서드만 단독 요청 → `intrinsic-value-analyzer`로 라우팅
- 멀티 대가 점수 랭킹 요청 → `value-screener`로 라우팅
- 해자 점수만 요청 → `eco-moat-codex`로 라우팅
- 종목 식별·시장 라우팅만 요청 → `cross-market-equity-router`로 라우팅
- 재무 진단만 요청 → `financial-analysis`로 라우팅

## Tooling

`sequential thinking`을 사용해야 하는 시점:
- Mode B에서 다수 종목을 어떤 순서로 깊이 분석할지 결정할 때
- Case 분류 결과가 ROIC와 모순될 때 재검증
- 데이터 결손으로 보수적 대체값 선정이 복잡할 때
- AV/EPV 산식에서 어떤 정규화 방식을 쓸지 분기가 많을 때

그 외 단순 분석은 sequential thinking 없이 직접 진행한다.

## Resource Loading Rule

진입 시 본 파일(SKILL.md)만 읽고, 필요할 때마다 다음 reference 파일을 로드한다 (Progressive Disclosure).

- `references/mode-a-deep-dive.md` — Mode A 풀 절차 (단일 종목 진입 시)
- `references/mode-b-list-screening.md` — Mode B 2-Stage 절차 (리스트 진입 시)
- `references/asset-value-calculation.md` — AV 계산 상세 (Step 3)
- `references/epv-calculation.md` — EPV 계산 상세 (Step 4)
- `references/matrix-classification.md` — 매트릭스 분류 (Step 5)
- `references/case-a-catalyst.md` — Case A 분기 (Step 6, Case A 시)
- `references/case-c-franchise.md` — Case C 분기 (Step 6, Case C 시)
- `references/mcp-routing-korea.md` — 한국 시장 MCP 사용표 (한국 종목 진입 시)
- `references/mcp-routing-us.md` — 미국 시장 MCP 사용표 (미국 종목 진입 시)
- `references/input-parsing.md` — 입력 파일 파싱 가이드 (파일 첨부 시)
- `references/report-template.md` — 한국어 보고서 양식 상세

## Scripts

계산 일관성을 위해 다음 헬퍼 스크립트를 우선 사용한다. 직접 계산을 다시 짜지 말고 이 스크립트들을 호출하라.

- `scripts/parse_ticker_list.py` — csv/xlsx/txt 입력 파싱
- `scripts/compute_av_liquidation.py` — 청산가치
- `scripts/compute_av_reproduction.py` — 재생산 비용
- `scripts/compute_epv.py` — 수익력가치
- `scripts/compute_wacc.py` — 자본비용
- `scripts/matrix_classify.py` — Case A/B/C 분류 + ROIC 검증
- `scripts/compute_margin_of_safety.py` — 안전마진

각 스크립트는 표준 입력 JSON을 받고 표준 출력 JSON을 반환한다. 단독 실행해도 되고 다른 도구에서 호출해도 된다.

## Output Contract

### Mode A (단일 종목) 응답 순서

1. **Snapshot**: 기업명·시장·코드·최종 판정·내재가치·안전마진·Case 분류
2. **Evidence (사실)**: 데이터 출처, 기간, 핵심 수치
3. **자산가치 AV**: 산업 분류 → 청산 또는 재생산 → 산출값
4. **수익력가치 EPV**: 정규화 영업이익 → WACC → EPV
5. **매트릭스**: EPV/AV 비율, Case, ROIC vs WACC 검증
6. **Case별 분석**: A=촉매제 / B=평범 / C=해자+성장
7. **안전마진**: 보수적 내재가치 대비 할인율, 목표 매수가
8. **투자 전략**: BUY/HOLD/AVOID, 분할매수 가격대, 모니터링, 리스크
9. **데이터 갭/한계**: 추정·대체·결손 명시
10. **비-자문 고지**

### Mode B (리스트) 응답 순서

1. **Snapshot**: 입력 N개, 시장 분포, Stage 1 통과율
2. **Stage 1 결과 표**: 종목별 Pass/Special/Fail + 사유 (1~2줄)
3. **Pass 종목 우선순위**: EPV/AV·안전마진 기준 정렬
4. **다음 단계 안내**: 우선순위 상위 N개에 대해 Mode A 진행 의사 확인
5. **데이터 갭/한계**
6. **비-자문 고지**

상세 출력 양식은 `references/report-template.md`와 `assets/report-template-ko.md` 참조.

## Error and Fallback

- **데이터 결손**: 5년 미만 재무제표만 있으면 3년 평균 적용, 그것도 부족하면 EPV는 N/A로 두고 AV만 산출
- **자본잠식**: 청산가치 모드로 전환하고 별도 'Special' 분류로 보고
- **거래정지/상장폐지 종목**: 분석 불가로 표시
- **MCP 실패**: 백업 MCP로 즉시 전환, 둘 다 실패 시 사용자 데이터 요청
- **산업 분류 모호**: 사용자에게 확인하지 말고 보수적으로 사양 산업 가정 (낮은 가치)
- **비-한국·비-미국 시장 요청**: 본 스킬은 한국·미국만 지원. 다른 시장은 `cross-market-equity-router`로 안내

## Non-Advisory Note

이 스킬의 모든 산출물은 정보 제공 목적이며, 투자 자문이 아니다. 매매 의사결정은 사용자 본인의 판단으로 한다.

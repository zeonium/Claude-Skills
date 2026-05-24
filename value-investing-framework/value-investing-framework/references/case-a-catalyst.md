# Case A: Value Trap 진단과 촉매제 검색

EPV < AV (특히 < 0.7 × AV)인 상태. 자산은 있는데 수익을 못 내는 기업. 외부 촉매(Catalyst)가 가치를 실현시켜야 의미가 있다.

## Step 1: 가치 함정 진단 (필요 시 financial-analysis 위임)

다음 신호들로 부실 경영 vs 사양 산업을 구별한다:

### 부실 경영 신호 (Bad Management)

- ROIC < WACC가 3~5년 지속되지만 산업 평균은 양호
- 동일 산업 경쟁사 대비 영업이익률 큰 차이
- 자본 배분 부실: 비핵심 사업 인수, 자사주 매입보다 비효율 투자
- 경영진 보상이 EPS·ROIC 아닌 매출 성장에 연동
- 부채로 무리한 확장 → 자본구조 악화

**보조 도구 위임**:
- 재무 비율·DuPont·Z-Score → `financial-analysis`
- 경영진 자본배분 정성 → `qualitative-company-analysis-codex`

### 사양 산업 신호 (Declining Industry)

- 산업 매출 5년 CAGR < 0
- 산업 전체 ROIC 침체
- 대체 기술/제품의 점유율 확대
- 산업 종사자 수 감소
- 주요 경쟁사 다수도 동일한 부진

**보조 도구 위임**:
- 산업 동향 → `market-research`

판정:
- 부실 경영 → 촉매제 검색으로 진행
- 사양 산업 → 청산가치만 의미, 촉매제 없으면 AVOID

## Step 2: 촉매제 (Catalyst) 검색

가치를 실현시킬 가능한 외부 사건.

### 카테고리 1: 경영진 교체

- 신임 CEO 임명 (특히 외부 영입, turnaround 경력)
- 이사회 개편
- 대주주 교체

데이터 소스:
- 한국: `open-dart-reader:opendart_event`, `opendart_major_shareholders`, `opendart_major_shareholders_exec`
- 미국: `sec-edgar:get_recent_filings` (8-K Item 5.02), `finnhub:finnhub_company_news`

### 카테고리 2: 행동주의 투자자 개입

- 5% 보유 신고 (한국 5% rule, 미국 13D)
- 주주제안, 위임장 대결
- 유명 활동가 진입

데이터 소스:
- 한국: DART 주요주주 변동 보고
- 미국: `sec-edgar:get_filing_content` (Schedule 13D/13G)

### 카테고리 3: M&A 시그널

- 인수 루머/제안
- 동종 업계 M&A 활발 → 본 종목도 타깃 가능성
- 지배구조 단순화 (지주사 vs 자회사 합병)

데이터 소스:
- 뉴스: `finnhub:finnhub_company_news`, `marketaux:marketaux_get_news`, `alphaear-news`, `korean-research`
- 공시: 한국 DART '풍문 또는 보도', 미국 8-K Item 1.01

### 카테고리 4: 자산 매각

- 비핵심 자산 매각으로 자본 회수
- 자회사 분할/매각 (스핀오프)
- 부동산 매각

데이터 소스:
- 공시 모니터링 (DART/EDGAR)
- 자산 평가: 사업보고서 부동산 명세

### 카테고리 5: 자본 배치 변화

- 대규모 자사주 매입 발표
- 배당 정책 변경
- 부채 상환 또는 자본구조 단순화

데이터 소스:
- 한국: DART 자기주식 취득 결정 공시
- 미국: 10-Q 자사주 매입 내역, `sec-edgar:analyze_8k`

## Step 3: 내부자 거래 추적

가치투자에서 가장 신뢰성 있는 시그널 중 하나.

### 내부자 매수 신호 (강함)

- 임원·이사 다수가 동시에 매수
- 큰 금액 매수 (개인 자산 대비 의미 있는 규모)
- CEO/CFO 직접 매수
- 가격 하락 중 매수 (저점 매수 시도)

### 내부자 매도 신호 (해석 필요)

- 일상적 자사주 옵션 행사 매도는 무시
- 비정상적 대량 매도는 우려
- 다수 임원 동시 매도는 강한 부정 신호

데이터 소스:
- 한국: `open-dart-reader:opendart_major_shareholders_exec` (임원·주요주주)
- 미국: `sec-edgar:get_insider_transactions`, `sec-edgar:get_insider_summary`, `finnhub`, `finviz-plus:get_insider_sec_filings`

## Step 4: 정통한 가치투자자 보유 확인 (선택)

전문 가치투자자들이 보유하고 있다면 추가 신호.

데이터 소스:
- 미국: `mcp__25aad980-...__form13F`, `sec-edgar` 13F 보유
- 한국: 자산운용사 공시 (DART에서 검색)

## 촉매제 강도 평가

각 카테고리별로 강도를 평가:

| 강도 | 의미 |
|---|---|
| **Strong** | 명확한 트리거(13D, M&A 제안 등), 가시적 일정 |
| **Moderate** | 신호 있음(경영진 교체, 활동가 진입), 효과 시간 필요 |
| **Weak** | 정황만 있음, 확정 시점 불명 |
| **None** | 촉매 없음 |

## Case A 최종 판정

| 진단 | 촉매제 | 의견 |
|---|---|---|
| 부실 경영 | Strong | **CONDITIONAL BUY** (목표 시간 12~24개월) |
| 부실 경영 | Moderate | **HOLD** 또는 소량 매수 |
| 부실 경영 | Weak/None | **AVOID** (가치 함정 가능성) |
| 사양 산업 | Strong + 자산 매각 | **CONDITIONAL BUY** (청산가치 대비 할인) |
| 사양 산업 | Moderate/Weak/None | **AVOID** |

## Case A 내재가치 추정

```
시나리오 1 (촉매 성공): EPV가 정상화되어 산업 평균 ROIC 회복
   → 정상화 EPV = AV × 평균 ROIC / WACC
시나리오 2 (촉매 실패): 청산가치
   → 청산가치 (보수적)

내재가치 = p × 시나리오1 + (1 - p) × 시나리오2
p = 촉매 성공 확률 (Strong 70%, Moderate 40%, Weak 20%)
```

안전마진 평가는 위 내재가치 추정에 기반.

## 모니터링 포인트

Case A로 분류된 종목은 다음을 주기적으로 모니터링:

- 분기별 ROIC 추세 (촉매 효과 가시화 여부)
- 신규 공시 (M&A, 자산매각, 경영진 변화)
- 내부자 거래 변화
- 활동가 지분 변화
- 산업 동향 (사양 산업이면 가속화/감속화)

데이터가 변하면 즉시 재평가.

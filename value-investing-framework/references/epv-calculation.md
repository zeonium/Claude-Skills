# 수익력 가치 (Earnings Power Value, EPV) 계산 상세

기업이 현재 상태로 영원히 (성장 없이 G=0) 현재 수익을 유지한다고 가정할 때의 가치. AV 다음으로 신뢰성 있는 가치 추정치다.

## 핵심 공식

```
EPV(Enterprise) = NOPAT / WACC
EPV(Equity)     = EPV(Enterprise) - Net Debt
EPV per Share   = EPV(Equity) / Shares Outstanding
```

`scripts/compute_epv.py`가 자동화한다.

## Step 1: 영업이익(EBIT) 시계열 확보

- 최근 **5~7년** EBIT (한국 영업이익, 미국 Operating Income)
- 최소 3년 (그 이하면 EPV 신뢰도 Low로 표기)
- 한국: `open-dart-reader:opendart_finstate_all`
- 미국: `sec-edgar:get_financials` 또는 `yfinance:yfinance_get_financials`

## Step 2: 일회성 항목 제거

장부상 영업이익에서 다음을 제외하고 진짜 지속 가능한 수익으로 환원:

| 항목 | 처리 |
|---|---|
| 자산매각 차익/손실 | 차익은 빼고, 손실은 더함 (영업외로 옮기지 말고 정규화에서 제외) |
| 일회성 구조조정 비용 | 환원 (더함) |
| 손상차손 | 환원 |
| 소송 충당금 | 일회성으로 큰 금액이면 환원 |
| 외환 손익 | 평균값 또는 0으로 평탄화 |
| 보조금·정부지원 | 비반복성이면 제외 |
| 일회성 인수 비용 | 환원 |

## Step 3: 경기 정규화 (Cycle Normalization)

산업이 경기민감(반도체, 화학, 건설, 자동차 등)이면 단순 평균만으로는 부족. 다음 방법 중 적합한 것 선택:

### 방법 A: 평균 영업이익률 × 최근 매출

```
정규화 영업이익률 = 평균(최근 5~7년 영업이익률)
정규화 EBIT      = 정규화 영업이익률 × 최근 12개월 매출
```

경기 사이클이 5~7년 이내에 한 번 도는 산업에 적합.

### 방법 B: Shiller-style CAPE

```
정규화 EBIT = 평균(최근 10년 EBIT, 인플레이션 조정)
```

10년 데이터가 있고 매우 순환적인 산업에 적합.

### 방법 C: 단순 가중평균 (비순환 산업)

```
정규화 EBIT = 0.5 × 최근 EBIT + 0.3 × 1년전 + 0.2 × 2년전
```

소비재·서비스 등 안정적 산업에 적합.

### 방법 D: 신중함 우선 - 보수적 하한

위 방법 중 둘을 계산하고 **낮은 값** 채택. 보고서에는 두 값 모두 표기.

## Step 4: D&A vs Maintenance CapEx 조정

GAAP/IFRS 감가상각비는 실제 유지보수에 필요한 CapEx와 다를 수 있다. EPV 정규화 시 둘의 차이를 조정한다.

### Maintenance CapEx 추정

방법 1 — Bruce Greenwald 공식:
```
Maintenance CapEx = 총 CapEx × (PP&E / 5년 평균 매출) ÷ (당해 매출 / 5년 평균 매출)
또는 더 단순히:
Maintenance CapEx = 총 CapEx - 매출 증가에 대한 추가 CapEx
                  = 총 CapEx - (매출 증가율 × 평균 CapEx/매출 비율 × 최근 매출)
```

방법 2 — 단순 추정:
```
Maintenance CapEx ≈ GAAP D&A × 0.80 ~ 1.20
```

성장 정체 기업은 D&A ≈ Maintenance CapEx로 둠. 성장 중이면 더 작게.

### 조정 적용

```
조정 EBIT = 정규화 EBIT + D&A - Maintenance CapEx
```

D&A는 보통 정규화 EBIT 산식에 이미 포함되어 있으므로(영업이익 = 매출 - COGS - SG&A - D&A), 위 식은 실제로 다음과 같다:

```
조정 EBIT = (영업이익 + D&A) - Maintenance CapEx
           = EBITDA - Maintenance CapEx
```

즉, EBITDA에서 진짜 유지보수 비용만 차감.

## Step 5: NOPAT 계산

```
NOPAT = 조정 EBIT × (1 - 유효세율)
```

유효세율:
- 한국 평균 22% (대기업), 중소기업 더 낮음
- 미국 평균 21%
- 실제 사용: 최근 5년 평균 (법인세비용 ÷ 세전이익)
- 일회성 세금조정(이연법인세 환입 등) 제외

## Step 6: WACC 산정

`scripts/compute_wacc.py` 사용.

```
WACC = (E/V) × Re + (D/V) × Rd × (1 - T)
```

- E = 시가총액
- D = 총 차입금 (단기차입금 + 장기차입금 + 사채)
- V = E + D
- Re = Rf + β × ERP  (CAPM)
- Rd = 평균 차입이자율 또는 회사채 yield

### 무위험수익률 (Rf)

- 미국: `fred:fred_get_series(series_id="DGS10")` — UST 10년
- 한국: `ecos` MCP → 국고채 10년 (통계코드 확인 후 호출)

### 베타 (β)

- 5년 주간 베타 (`yfinance`, `finnhub:finnhub_company_basic_financials`)
- 한국 종목: `naver-stock` 또는 산업 평균값 사용 가능
- 베타 < 0.5 또는 > 2.0 극단값은 1년 일간 베타로 교차 검증

### 시장 위험 프리미엄 (ERP)

- 미국: 5.0% 기본 (Damodaran 최신값 권장)
- 한국: 6.0% 기본 (선진국 + 컨트리 리스크 0.5~1.0%)

### Rd (타인자본비용)

- 회사채 등급 알려진 경우: 등급별 회사채 yield + 무위험수익률
- 모르는 경우: 이자비용 / 평균 차입금
- 둘 다 어려우면: Rf + 신용 스프레드 200~400bp (기업 규모·신용에 따라)

## Step 7: EPV 산출

```
EPV(Enterprise) = NOPAT / WACC
EPV(Equity)     = EPV(Enterprise) - Net Debt
Net Debt        = 총 차입금 - 현금성자산
EPV per Share   = EPV(Equity) / 발행주식수
```

## 출력 (보고서 항목)

- 정규화 EBIT 산식 명시 (방법 A/B/C 중 어떤 것)
- 일회성 항목 조정 내역
- D&A, Maintenance CapEx 산출
- 유효세율 평균
- WACC 구성 요소 (Rf, β, ERP, Re, Rd, T, E/V, D/V)
- EPV (Enterprise) / EPV (Equity) / EPV per Share
- 추정 신뢰도 (High / Medium / Low)

## 신뢰도 평가

- **High**: 5년+ 데이터, 일회성 적음, 비순환 산업, 부채구조 단순
- **Medium**: 3~4년 데이터, 일부 정규화 필요, 약간의 순환성
- **Low**: 3년 미만, 일회성 많음, 강한 순환성, 복잡한 부채

신뢰도 Low면 안전마진 요구치를 더 높게(예: 0.50 이상) 적용한다.

## 흔한 함정

- **고성장 기업에 적용 금지**: EPV는 성장 없는 정상 상태 가정. 고성장 기업의 시장가가 EPV보다 훨씬 높은 게 정상. Case C 프랜차이즈 + 성장 가치 별도 산출이 답.
- **금융기업**: NOPAT/WACC 프레임이 작동하지 않음. `intrinsic-value-analyzer` (RIM, P/B 기반)에 위임 권장.
- **REIT**: 동일. FFO/AFFO·NAV 기반 → `intrinsic-value-analyzer` 위임.
- **자본잠식 또는 만성적자**: EPV 산출 불가. AV(청산가치)만 사용하고 Case A 처리.

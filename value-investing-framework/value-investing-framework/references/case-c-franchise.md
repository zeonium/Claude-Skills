# Case C: 프랜차이즈 검증과 성장 가치

EPV > AV × 1.3, ROIC > WACC + 2~3%p. 진입장벽(해자)이 존재한다는 정량적 신호. 정성적 검증이 필수다.

## Step 1: 해자 정성 검증 (eco-moat-codex 위임 권장)

본 스킬이 직접 해자 점수를 매기지 않는다. `eco-moat-codex` (또는 `anthropic-skills:eco-moat-ai`) 스킬에 위임:

호출 시 다음 정보 전달:
- 종목명·코드·시장
- 모드: `Standard` (기본) 또는 `Deep` (사용자가 명시적으로 요청 시)
- 컨텍스트: "Case C 검증 - EPV/AV=X.X, ROIC=Y%, WACC=Z% 정량 결과 확인용"

수신 후 본 스킬에서 활용할 결과:
- 해자 점수/등급
- 해자 종류 (Customer Captivity / Scale / Resources / Network / Regulation)
- Buffett Gate 통과 여부
- Owner Earnings 추정

## Step 2: 그린월드 식 해자 분류

eco-moat-codex 결과를 다음 그린월드 분류에 매핑:

### 1) 고객 캡티브 (Customer Captivity)

증거:
- 전환 비용 (학습, 데이터, 통합)
- 습관 (Habit) - 일상 의존도
- 검색 비용 (대안 찾기 비싸거나 귀찮음)
- 락인 효과

정량 지표:
- 고객 유지율 > 90%
- 동일 고객 반복 매출 비중 높음
- ARPU 안정 또는 상승

### 2) 규모의 경제 (Economies of Scale)

증거:
- 로컬 시장 압도적 점유율 (시장 1위 점유율 > 2배 차이)
- 광고 등 고정비를 큰 매출로 분산
- 물류·유통 네트워크 우위

정량 지표:
- 영업이익률이 경쟁사 대비 명백히 높음
- 시장 점유율 안정 또는 확대
- 신규 진입자 5년 부재

### 3) 독점적 자원·기술

증거:
- 핵심 특허 보유
- 정부 면허 (방송, 카지노 등)
- 자원 매장 독점
- 특수 입지

정량 지표:
- 특허 가치 (피인용도, 패밀리 수) — 필요 시 `patent-portfolio-strategist` 스킬 위임 가능

### 4) 네트워크 효과 (현대 추가)

증거:
- 사용자 수가 증가할수록 가치 상승
- 플랫폼 비즈니스 (마켓플레이스, 결제, SNS)

정량 지표:
- 사용자 증가율 vs 매출 증가율 동조
- 양면 시장 균형 (수요·공급 모두 안정)

### 5) 규제 우위

증거:
- 신규 진입 제한 규제
- 환경·안전 규제로 진입 비용 상승
- 라이센스 발급 제한

## Step 3: 해자 지속 가능성 평가

해자가 있는 것과 유지되는 것은 다르다.

지속 가능성 신호:
- 5~10년 ROIC 일관성 (변동성 < 30%)
- 시장 점유율 안정 또는 확대
- 신규 진입자 부재 또는 실패 사례
- R&D·마케팅 등 해자 강화 투자 지속

해자 약화 신호:
- 신규 진입자 증가
- 기술 paradigm 변화 (예: 디지털 전환)
- 규제 완화
- 경영진 자본배분 실수 (해자 약한 영역 확장)

## Step 4: 성장 가치 (Growth Value) 산출

해자가 검증되면 성장이 가치를 창출할 수 있다. 그린월드 공식:

```
Growth Value = (g × IC) × (ROIC - WACC) / (WACC × (WACC - g))
              + 단순화하면
Growth Value ≈ Invested Capital × g × (ROIC/WACC - 1) / (WACC - g)
```

또는 더 단순한 형태:
```
Growth Value = EPV × g / (WACC - g) × (1 - 재투자율 × WACC/ROIC)
```

### 입력 값

- `g`: 지속 가능한 성장률 (보수적으로 산업 명목 GDP 성장률 또는 인플레이션 + 2~3%p, 최대 WACC - 2%p)
- `ROIC`: 5년 평균
- `WACC`: 산정 값
- `IC`: 투자 자본 (자기자본 + 차입금 - 현금)

### 보수성 가이드라인

- `g < WACC - 2%p` 강제
- ROIC < WACC 이면 Growth Value = 0 (성장이 가치 파괴)
- ROIC ≈ WACC 이면 Growth Value 매우 작음 (사실상 0으로 둠)
- g는 절대 10%를 넘기지 않음 (어떤 기업도 영원히 두 자리 성장 못 함)

## Step 5: Reverse DCF로 시장 implied expectations 교차 검증

성장 가치 산출 후, 현재 주가가 시장이 기대하는 성장률을 함축한다.

위임 권장: `intrinsic-value-analyzer` 스킬에 "reverse DCF로 implied growth 산출" 요청. 결과를 본 스킬의 g 가정과 비교.

- 시장 implied g > 본 스킬 g + 3%p → 시장이 성장을 과도 평가 (조심)
- 시장 implied g ≈ 본 스킬 g → 합리적 평가
- 시장 implied g < 본 스킬 g → 저평가 가능성

## Case C 최종 내재가치

```
내재가치 = AV + (EPV - AV) + Growth Value
         = EPV + Growth Value
주당 내재가치 = (EPV(Equity) + Growth Value) / Shares Outstanding
```

또는 단순히:
```
내재가치 = EPV × (1 + Franchise Premium + Growth Premium)
```

세 가지 시나리오 제시 (Bear / Base / Bull):
- Bear: g = 0 (해자 약화), 내재가치 = EPV
- Base: g = 보수 가정, 표준 산식
- Bull: g = 다소 적극적, 단 WACC - 2%p 이내

## Case C 의견 매핑

| 안전마진 (Base 기준) | 의견 |
|---|---|
| ≥ 0.40 | **STRONG BUY** |
| 0.25 ~ 0.40 | **BUY** |
| 0.10 ~ 0.25 | **HOLD** (좋은 회사지만 가격이 매력적이지 않음) |
| < 0.10 | **AVOID** (좋은 회사라도 비싸면 매수 불가) |

Case C는 일반적으로 시장에서 프리미엄을 받으므로 안전마진 요구치를 Case B/A보다 낮게 설정해도 됨 (단 0.25는 확보).

## 보고서 출력 항목

- 해자 검증 결과 (eco-moat-codex 산출 요약)
- 해자 종류 (그린월드 5분류 매핑)
- 해자 지속 가능성 평가
- 성장률 g 가정 (Bear/Base/Bull)
- Growth Value 산출
- Reverse DCF implied growth (교차 검증)
- 시나리오별 내재가치
- 권장 매수 가격대 (Base 시나리오 안전마진 0.25 지점)

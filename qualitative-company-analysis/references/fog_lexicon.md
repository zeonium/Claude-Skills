# FOG 어휘 사전 (Fact-deficient, Obfuscating Generalities)

> **출처**: Rittenhouse, *Investing Between the Lines* (2013) FOG 분류 체계.
> 사용 방법: `scripts/fog_lexicon_scorer.py --input letter.txt --lang [en|ko]`로 자동 채점.

---

## 1. FOG의 3가지 형태

| 유형 | 정의 | 가점/감점 |
|------|------|----------|
| **상투어 (Clichés)** | 데이터·실행계획 없이 비판적 사고를 마비시키는 포장 문구 | **-3점/문구** |
| **위즐 워드 (Weasel Words)** | 문장의 실질적 의미를 증발시키는 빈껍데기 단어 | **-3점/단어** |
| **오웰적 미사여구 (Orwellian Nonsense)** | 비논리적·자기모순적 문장으로 리스크 은폐 | **-5점/문장** |
| **전략적 부조화** | 핵심가치 선언과 실제 자본배분·보상이 모순 | **-10점/사례** |

> "엔론 2000년 서한은 단 한 문단에서 FOG로 -26점 감점"

---

## 2. 위즐 워드 (Weasel Words) — 단어당 -3점

### 영어 사전

| 영어 | 한국어 대응 | 비고 |
|------|------------|------|
| solid | 견고한, 탄탄한 | 수치 없는 형용사 |
| robust | 견조한 | LM 사전 'Positive'에도 포함 |
| momentum | 모멘텀 | 측정 기준 부재 |
| enhanced | 강화된 | 무엇이 얼마나 강화됐는지 미정의 |
| synergy | 시너지 | M&A 정당화의 단골 |
| leverage (동사) | 활용하다, 레버리지 | "leverage our scale" 등 |
| proactive | 선제적인 | 대개 사후 합리화 |
| optimize | 최적화 | 정량 목표 부재 |
| streamline | 합리화, 간소화 | 구조조정 미화 |
| best-in-class | 업계 최고 | 비교 기준 부재 |
| world-class | 세계적 수준 | 동일 |
| transformative | 변혁적인 | 정량 결과 부재 |
| disruptive | 파괴적인 | 자기 선언 |
| empower | 권한 부여하다 | 측정 불가 |
| ecosystem | 생태계 | 경계 모호 |
| journey | 여정 | 종착점 부재 |
| meaningful | 의미 있는 | 의미의 정량 부재 |
| significant | 상당한 | 정량 부재 |
| substantial | 실질적인 | 동일 |
| considerable | 상당한 | 동일 |

### 한국어 사전

| 한국어 | 비고 |
|--------|------|
| 견조한 | 수치 없는 낙관 |
| 견고한 | 동일 |
| 양호한 | 정량 부재 |
| 건전한 | 동일 |
| 긍정적인 | 정량 부재 |
| 우호적인 | 동일 |
| 충분한 | 정량 부재 |
| 상당한 | 정량 부재 |
| 유의미한 | 정량 부재 |
| 고무적인 | 동일 |
| 탄탄한 | 동일 |
| 안정적인 | 정량 부재 |
| 회복세 | 추세 미정량 |
| 모멘텀 | 측정 기준 부재 |
| 시너지 | 정량 부재 |
| 최적화 | 동일 |
| 선제적 | 동일 |
| 혁신적 | 자기 선언 |
| 전략적 | 모호 강조어 |

---

## 3. 상투어 (Clichés) — 문구당 -3점

### 영어 사전

| 영어 | 한국어 대응 |
|------|-------------|
| talented people | 재능 있는 인재들 |
| our greatest asset(s) | 우리의 가장 큰 자산 |
| employees are our greatest assets | 직원은 우리의 가장 큰 자산 |
| global presence | 글로벌 입지 |
| financial strength | 재무적 강점 |
| significant value for our shareholders | 주주를 위한 상당한 가치 |
| value creation for shareholders | 주주 가치 창출 |
| our future is bright | 미래는 밝다 |
| customer-centric | 고객 중심 |
| customer-first | 고객 우선 |
| people-first | 사람 우선 |
| innovation engine | 혁신 엔진 |
| accelerate growth | 성장 가속화 |
| accelerate their growth | 성장 가속화 |
| transformation journey | 변화의 여정 |
| massive market knowledge | 방대한 시장 지식 |
| deep expertise | 깊은 전문성 |
| world-class team | 세계적인 팀 |
| best-in-class platform | 업계 최고의 플랫폼 |
| relentless focus on execution | 실행에 대한 끊임없는 집중 |
| unwavering commitment | 흔들림 없는 헌신 |

### 한국어 사전

| 한국어 |
|--------|
| 재능 있는 인재 |
| 우수한 인재 |
| 우리의 가장 큰 자산 |
| 직원은 우리의 가장 큰 자산 |
| 글로벌 입지 |
| 재무적 강점 |
| 주주 가치 창출 |
| 주주를 위한 상당한 가치 |
| 미래는 밝다 |
| 고객 중심 |
| 고객 우선 |
| 혁신 엔진 |
| 성장 가속화 |
| 변화의 여정 |
| 방대한 시장 지식 |
| 깊은 전문성 |
| 세계적인 팀 |
| 업계 최고 |
| 끊임없는 집중 |
| 흔들림 없는 헌신 |
| 끊임없는 노력 |
| 일류 기업 |
| 글로벌 리더 |

### 엔론의 '독성 6종 세트' (2000 서한)

> "재능 있는 인재 / 글로벌 입지 / 금융 실력 / 방대한 시장 지식 / 시너지 레버리지 / 주주를 위한 상당한 가치 창출"

한 문단에 몰아쓰며 실질 리스크를 가린 대표 사례. 패턴 자동 감지: `fog_lexicon_scorer.py --detect-enron-pattern`

---

## 4. 오웰적 미사여구 (Orwellian Nonsense) — 문장당 -5점

### 패턴 (정규식 기반 탐지)

| 패턴 | 영어 예시 | 한국어 예시 |
|------|-----------|-------------|
| **자기모순** (긍정→부정→긍정) | "We believe X is not material, but in certain periods may be material" | "중요하지 않을 것으로 믿지만 특정 기간에는 중요할 수도 있다" |
| **이중부정** | "We are not unconfident in our outlook" | "전망에 자신감이 없지 않다" |
| **모순 수식** (non-recurring vs recurring) | "non-recurring restructuring charges that recur annually" | "매년 발생하는 일회성 구조조정 비용" |
| **시점 모호** (may/could/might 남용) | "could potentially eventually possibly result in" | "결과적으로 잠재적으로 어쩌면 가능할 수도 있는" |
| **수동태 책임 회피** | "errors were made", "decisions were taken" | "오류가 발생하였습니다", "결정이 이루어졌습니다" |
| **의미 상쇄** (긍정어+부정 단서) | "strong results despite significant challenges and continued headwinds" | "도전적 환경에도 불구하고 강한 실적" (실은 부진을 강한 어조로 포장) |

### 대표 실패 사례

**AIG 2007 마틴 설리번 서한**:
> "114.7억 달러 파생상품 손실은 중요하지 않을 것으로 *믿지만*, 특정 보고 기간에는 중요한 수준이 될 *수도* 있다."

→ 이 한 문장만으로 -5점 + 전체 서한 톤 부정 신호.

---

## 5. 가점 패턴

### 5.1 정성적 목표 (+5점/문구)

| 영어 | 한국어 |
|------|--------|
| we aim to improve | 개선을 목표로 한다 |
| our goal is to | ~을 목표로 한다 |
| we are committed to | ~에 헌신한다 |
| we plan to expand | 확장을 계획한다 |

### 5.2 정량적 목표 (+10점/문구)

**탐지 패턴** (정규식):
- 영어: `(grow|increase|reduce|achieve)\s+\w+\s+by\s+\d+(\.\d+)?%`
- 영어: `(target|goal)\s+of\s+\$\d+\s*(billion|million|B|M)`
- 영어: `by\s+(20\d{2}|FY\d{2,4})`
- 한국어: `(매출|영업이익|EBITDA|점유율).*?(\d+(\.\d+)?%|\d+조|\d+억)`
- 한국어: `(20\d{2}년|FY\d{2,4})까지`

**예시**:
- "We aim to grow revenue by 4-6% in FY2026" → +10
- "2027년까지 영업이익률 15% 달성" → +10

### 5.3 목표 맥락·세부 (+5점/지표)

목표 옆에 (a) 측정 지표, (b) 달성 방안, (c) 책임 부서를 명시:

**예시**: "We aim to grow Services revenue by 8% by FY2026, *measured by total transactions* and *driven by App Store expansion in India and Indonesia*" → +10 +5 +5 = +20

### 5.4 Cash/Cash flow 언급 (+3점/언급)

단순 언급만으로 +3 (자본 수탁 의식의 1차 신호).

- 영어: `cash flow`, `free cash flow`, `operating cash flow`, `FCF`
- 한국어: `현금흐름`, `잉여현금흐름`, `영업현금흐름`, `FCF`

### 5.5 FCF 맥락·디테일 (+3점/설명)

다음 중 하나가 동반되면 추가 +3:
- FCF 정의 제시 ("FCF는 영업현금흐름에서 유지보수 CapEx를 제외한 금액")
- 5년 전과 대조 ("FY2019 $50B → FY2024 $100B")
- 사용처 명시 ("FCF의 60%는 자사주, 40%는 배당")
- 성장 CapEx와 유지 CapEx 분리

**J&J Ralph Larsen 2001 사례**: FCF를 정확히 정의 + 5년 전 대조 → +3 +3 = +6

---

## 6. 전략적 부조화 (-10점/사례)

핵심가치 선언과 실제 행동의 모순. 수동 분석 영역 (자동 탐지 불가).

### 탐지 체크리스트

| 선언 | 실제 행동 (모순) | 감점 |
|------|------------------|------|
| "고객 우선" | Me First 보상 구조 (예: 리먼 'sales credits 40% 증가') | -10 |
| "장기 가치" | 분기 EPS 맞추려 자사주 고점 매입 | -10 |
| "직원이 자산" | 대량 해고 + 임원 보너스 인상 | -10 |
| "투명한 보고" | 비GAAP 지표로 손실 은폐 | -10 |
| "리스크 관리" | 파생상품 익스포저 각주 은폐 | -10 |

---

## 7. 산식 적용 예시

**가상 서한 (단어수 2,000)**:
- 정성적 목표 3개 × +5 = +15
- 정량적 목표 2개 × +10 = +20
- 목표 맥락 4개 × +5 = +20
- Cash 언급 5회 × +3 = +15
- FCF 맥락 2회 × +3 = +6
- 상투어 6개 × -3 = -18
- 위즐워드 8개 × -3 = -24
- 오웰 문장 1개 × -5 = -5
- 전략적 부조화 0개

```
Net Candor Score = (15+20+20+15+6) - (18+24+5+0) = 76 - 47 = +29
FOG 비율          = 47 / (76+47) = 38.2%
Candor Index      = (1 - 0.382) × 100 = 61.8
Communication Eff = 29 / 2000 = 0.0145 (참고용)
```

→ **판정**: 경계 (50~74) — 추세 모니터링 필요. FOG 38%로 위즐워드 비중 높음.

---

## 8. 활용 가이드

1. **단년 점수만 보지 말 것** — 전년 대비 delta가 더 중요. Net Score (+) → (-) 전환은 알림 발동.
2. **업종 보정** — 금융·헬스케어는 규제 언어로 위즐워드 인플레 자연 발생. 동종 5사 평균과 비교.
3. **한국 사업보고서 보정** — 한국 사장의 인사말은 영어 서한 대비 짧고 형식적. 가점 기준 50% 완화 권장.
4. **단어 폭 vs 의미 폭** — Communication Efficiency가 낮아도 짧고 정직한 서한(Berkshire 스타일)은 가점.

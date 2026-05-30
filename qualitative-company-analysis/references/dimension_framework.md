# 5대 분석 차원 프레임워크 (D1~D5)

## 차원 개요

| 차원 | 이름 | 가중치 | 핵심 질문 | 주요 도구 |
|------|------|--------|-----------|---------|
| D1 | 경영진 신뢰도 & 자본배분 | 30% | 경영진을 믿을 수 있는가? | 컨퍼런스콜, SEC Form 4, DART |
| D2 | 경제적 해자 지속성 | 30% | 해자가 5~10년 유지되는가? | eco-moat-ai, Semantic Diff |
| D3 | ESG & 지배구조 투명성 | 15% | 주주 이익과 경영진 이익이 일치하는가? | DEF 14A, 기업지배구조 보고서 |
| D4 | 기업문화 & 혁신 역량 | 15% | 조직이 미래를 만들 역량이 있는가? | Glassdoor, 잡플래닛, KIPRIS |
| D5 | 시장 감성 & 대안 데이터 | 10% | 현장 신호가 공식 서사와 일치하는가? | alphaear-sentiment, ISQ |

---

## D1: 경영진 신뢰도 & 자본배분 (CANDOR-7 통합)

### D1 종합 산식

```
D1 = Quick Scorecard(5항목, 0-100) × 0.50
   + Candor Index(0-100, CANDOR-7 통합) × 0.30
   + Moving Targets 패턴(0-100) × 0.10
   + 내부자 거래 패턴(0-100) × 0.10
```

자세한 7-시스템 격자 + Net Candor Score: `references/candor7_framework.md`
FOG 어휘 사전: `references/fog_lexicon.md`

### Green Flags (10개 — 5 기존 + 5 CANDOR-7)
1. 가이던스 대비 실제 실적 일관 상회 (최근 4분기 이상)
2. 자사주 매입이 주가 조정 구간에 집중 (고점 소각 없음)
3. 내부자 매수 > 매도, 또는 10b5-1 계획 매도만 존재
4. Q&A 직접 답변 비율 70% 이상, 핵심 KPI 수치 명시
5. 경영진 스스로 실수 인정 후 대안 제시 (귀인 내부 지향)
6. **CEO 자기 집필 (1인칭 빈도 ≥ 평균, 구체 일화 포함)**
7. **FCF 정의 + 5년 전 대조 (J&J Larsen 2001 패턴)**
8. **정량 목표 + 기한 명시 ("2027년까지 X달성") — Net Candor +10/문구**
9. **변명 없는 실수 인정 (Expeditors 패턴)**
10. **박수받는 나쁜 소식 — 출시 지연 보고 시 책임 추궁 대신 정보 공유 강조 (Ford-Mulally 패턴)**

### Red Flags (10개 — 5 기존 + 5 CANDOR-7)
1. Moving Target 감지: 핵심 KPI 강조가 분기마다 교체
2. Q&A 회피 패턴: "좋은 질문" + 추상적 답변 반복
3. 실패 귀인 100% 외부 (매크로·환율·업황)
4. 가이던스 후퇴 또는 Non-GAAP으로 기준 이동
5. 임원 대규모 지분 매도 (10b5-1 계획 외)
6. **CEO 자기 집필 부재 (1인칭 < 5건, 일화 없음 → IR 대행 의심)**
7. **오웰적 자기모순 문장 — "중요하지 않을 것으로 믿지만 ~할 수도" (AIG 2007) → -5점/문장**
8. **엔론 '독성 6종 세트' 한 문단 집중 (`fog_lexicon_scorer.py --detect-enron-pattern`)**
9. **본질보다 외형 과시 — 과거 랭킹·시장점유율 홍보 (리먼/WaMu 패턴)**
10. **'Me First' 문화 — 고객가치 대신 자사 수수료를 성과로 제시 (리먼 'sales credits 40%')**

### CANDOR-7 7-시스템 매핑 (참고)

| 시스템 | 평가 영역 | 자동화 |
|--------|-----------|--------|
| ① Capital Stewardship | 자본배분·FCF 맥락 | `ceo_letter_forensics.py --check fcf` |
| ② Strategy | 전략 일관성·단순화 | `semantic_diff_kit.py` (서한 3년치) |
| ③ Accountability | 약속 vs 실제 수치 대조 | 수치 교차검증 (수동) |
| ④ Vision | 독창적 어휘·미래 그림 | `fog_lexicon_scorer.py` (상투어 역지표) |
| ⑤ Leadership | 실수 인정·투자자 교육 | `ceo_letter_forensics.py --check mistake` |
| ⑥ Stakeholder | 현장 스토리·균형 | 수동 검토 (case_library.md 참조) |
| ⑦ Candor | 종합 FOG 농도 | `fog_lexicon_scorer.py` (Net Candor Score) |

### 데이터 소스
- KR: DART 임원 공시, 컨퍼런스콜 대본 (open-dart-reader)
- US: SEC Form 4, DEF 14A, 컨퍼런스콜 (sec-edgar)
- 공통: alphaear-news (뉴스 교차검증)

### 정량 교차검증 지표
| 정성 가설 | 정량 지표 | 판정 기준 |
|-----------|---------|---------|
| 가이던스 신뢰성 | 가이던스 달성률 | ≥100% → Green |
| 자본배분 합리성 | FCF 대비 자사주 매입 타이밍 | 조정 구간 집중 → Green |
| 주주 이익 일치 | 경영진 보상 vs EPS 성장 상관 | r > 0.7 → Green |

---

## D2: 경제적 해자 지속성

### Green Flags (5개)
1. Gross Margin 5년 연속 방어 또는 상승
2. 전환비용 근거: NRR ≥ 110% 또는 고객 계약 기간 ≥ 3년
3. 네트워크 효과 정량 증거: MAU 성장 > 시장 성장
4. 특허 피인용 상위 10% 이상 (혁신 질적 우위)
5. 신규 경쟁자 3년 내 수익화 실패 이력

### Red Flags (5개)
1. 위험요인 Semantic Diff에서 경쟁 위협 신규 문장 추가 (cos < 0.65)
2. Gross Margin YoY 3%p 이상 하락
3. 핵심 고객 이탈 또는 NRR 100% 이하
4. 빅테크 자체 솔루션 개발 공식 발표
5. 주요 특허 만료 (5년 내) + 대체 특허 부재

### 데이터 소스
- KR: DART 사업보고서 위험요인 섹션 (open-dart-reader)
- US: 10-K Item 1A (sec-edgar)
- 공통: eco-moat-ai Stage 3, KIPRIS/USPTO 특허 데이터

### Semantic Diff 연계
- `scripts/semantic_diff_kit.py --lang [en|ko]` 실행
- 평균 cos ≥ 0.85: 소폭 변화 (D2 현상 유지)
- 평균 cos 0.70~0.85: 유의미한 변화 (D2 주의)
- 평균 cos < 0.70: 큰 변화 (D2 하향 검토)

---

## D3: ESG & 지배구조 투명성

### Green Flags (5개)
1. 독립 이사회 비율 ≥ 50%, 감사위원회 전원 사외이사
2. CEO 보상이 주주 수익과 연동 (장기 인센티브 비중 > 50%)
3. CoE (기업지배구조 핵심원칙) 전항목 준수 (KR)
4. 공시 Boilerplate 비율 < 40% (실질적 업데이트)
5. ESG 위원회 설치 + 독립 검증 보고서 발행

### Red Flags (5개)
1. 관련 당사자 거래 증가 (RPT 금액 YoY +30% 이상)
2. 감사인 교체 (Big 4 → 중소형 / 의견거절 이력)
3. 공시 Boilerplate 비율 > 60% (형식적 공시)
4. 집중투표제 미채택 + 황금주/차등의결권 존재
5. 공정공시 위반 이력 또는 내부자 거래 제재

### 정량 교차검증 지표
| 정성 가설 | 정량 지표 | 판정 기준 |
|-----------|---------|---------|
| 지배구조 투명성 | Boilerplate 비율 | < 40% → Green |
| 주주 이익 일치 | CEO Pay Ratio | 업종 하위 50% → Green |

---

## D4: 기업문화 & 혁신 역량

### Green Flags (5개)
1. Glassdoor/잡플래닛 종합 평점 ≥ 4.0, CEO 승인률 ≥ 80%
2. 핵심 직무(R&D/PM) 이직률 업종 평균 이하
3. 채용공고 방향이 전략 방향과 일치 (AI 투자 선언 → AI 채용 급증)
4. 특허 피인용 성장률 ≥ 20% (3년 CAGR)
5. R&D 투자 매출 대비 비율 상승 추세

### Red Flags (5개)
1. 독성 키워드 빈도 높음: 번아웃·마이크로매니지먼트·독성 ≥ 6건
2. 핵심 직무 이직률 업종 평균 2배 이상
3. 채용공고 방향이 전략 방향과 불일치
4. R&D 비율 하락 + 특허 출원 감소 동시 발생
5. 최근 1년 내 임원 3인 이상 이탈

### 데이터 소스
- KR: 잡플래닛, 사람인, KIPRIS (open-dart-reader 보조)
- US: Glassdoor, LinkedIn, USPTO
- 공통: `scripts/moving_targets_detector.py` (채용 키워드 추적)

---

## D5: 시장 감성 & 대안 데이터

### Green Flags (5개)
1. ISQ (alphaear-sentiment) 상위 25% (업종 대비)
2. Reddit/X 감성 추세 상승 (3개월 CAGR > 0)
3. 공식 서사 ↔ Scuttlebutt 신호 일치 (Divergence 없음)
4. 애널리스트 컨센서스 상향 조정 + 목표주가 분산 낮음
5. 공매도 비율 감소 추세

### Red Flags (5개)
1. ISQ 하위 25% 또는 급락 (1개월 내 10p 이상 하락)
2. 공식 서사 vs. 현장 신호 불일치 (Divergence 있음)
3. 핵심 고객사 소셜 언급 급감 (이탈 전조)
4. 공매도 비율 업종 상위 10%
5. 내부자 정보 기반 의심 매도 패턴 (SEC Form 4 클러스터링)

### 데이터 소스
- alphaear-sentiment (ISQ 점수, 멀티소스 감성)
- alphaear-news (뉴스 감성 시계열)
- brave-search / tavily (현장 검색)

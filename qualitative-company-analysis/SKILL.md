---
name: qualitative-company-analysis
description: |
  재무수치 너머의 'Why'를 분석하는 5단계 하이브리드 정성적 기업분석 오케스트레이터.
  Rittenhouse CANDOR-7(2013) + Net Candor Score + FOG 어휘 사전 통합 v2.0.
  MUST 사용: "정성적 분석", "Investment Memo", "경영진 신뢰도", "Moving Targets",
  "Pre-mortem", "QualScore", "공시 텍스트", "5단계 분석", "어조 분석", "KPI 이동",
  "Scuttlebutt", "해자 지속성", "주주 서한", "CEO letter", "CANDOR-7", "Net Candor Score",
  "Candor Index", "FOG 분석", "위즐워드", "오웰 문법", "상투어", "Rittenhouse",
  "Investing Between the Lines", "행간 읽기", "7-시스템", "자본 수탁", "FCF 정의".
  영어: "qualitative analysis", "investment memo", "management credibility",
  "moving targets", "pre-mortem", "QualScore", "shareholder letter", "CANDOR-7 framework",
  "Net Candor Score", "FOG lexicon", "weasel words", "Orwellian nonsense",
  "Capital Stewardship", "Berkshire gold standard".
  eco-moat-ai와의 차이: eco-moat-ai는 해자 점수화(D2), 이 스킬은 5차원 QualScore +
  경영진 신뢰도(CANDOR-7 + Net Candor Score) + Semantic Diff + Moving Targets +
  Investment Memo 최상위 오케스트레이터.
---

# 정성적 기업분석 오케스트레이터 (CANDOR-7 통합 v2.0)

## 핵심 철학

재무수치(정량)는 '무엇이 일어났는가'를 말하고, 정성은 '왜, 그리고 앞으로도 그럴 것인가'를 답한다.
이 스킬은 두 관점을 통합하여 투자 의사결정의 질을 높인다.

**핵심 가설 (Rittenhouse, 2013):** "경영진의 솔직함은 미래 재무성과의 강력한 선행 지표이며,
의사소통 리스크는 아직 선언되지 않은 재무 리스크다." Candor 상위 25%는 2005~2011년 누적
59.8%를 기록(S&P 36.4% / 하위 25% 15.3%).

## 사용 시점

- 종목에 대한 Investment Memo 작성 요청
- 경영진 신뢰도 또는 자본배분 능력 평가
- 컨퍼런스콜 어조·KPI 이동 분석
- **CEO 연례 주주 서한·사장의 인사말 포렌식 분석 (신규)**
- 사업보고서/10-K 위험요인 연도별 변화 분석
- 기업문화·직원 리뷰·특허 혁신성 점검
- 정량 분석(financial-analysis) 이후 정성 심화 분석
- Pre-mortem / Red Teaming 구조화 요청
- FOG(상투어·위즐워드·오웰문장) 정량 감점 및 Candor 프리미엄 후보 선별

## 5단계 워크플로우

자세한 내용: `references/workflow_5stage.md`

### [Step 1] 정량 스크리닝 → 정성 진입 결정
- **위임**: financial-analysis 스킬에 초기 재무 스크리닝 요청
- **Gate 조건**: Gross Margin 방어 + Beneish M-Score < -1.78 → Step 2 진행
- **산출물**: 분석 대상 확정 + 정성 집중 영역 선정

### [Step 2] 해자 & 경쟁 우위 (D2)
- **위임**: `eco-moat-ai` 스킬 Stage 3 정밀 평가 요청
- **직접 수행**: `scripts/semantic_diff_kit.py`로 위험요인 YoY Semantic Diff
- **템플릿**: `templates/moat_durability_hypothesis.md`
- **참조**: `references/dimension_framework.md` (D2 섹션)

### [Step 3] 경영진 신뢰도 & 자본배분 (CANDOR-7 + 5단계 포렌식)

**Step 3A — CEO 주주 서한 포렌식 (신규)**
- **5단계 포렌식**: Red Pen Test → 수치 교차검증 → FCF 맥락 → 전략 일관성 → 실수 대처법
- **직접 수행**: `scripts/fog_lexicon_scorer.py`로 Net Candor Score 자동 채점
- **직접 수행**: `scripts/ceo_letter_forensics.py`로 자기 집필도·오웰 모순·FCF 맥락 진단
- **템플릿**: `templates/ceo_letter_candor7_report.md`
- **참조**: `references/candor7_framework.md`, `references/fog_lexicon.md`, `references/case_library.md`

**Step 3B — 컨퍼런스콜 Q&A (기존 강화)**
- **직접 수행**: 컨퍼런스콜 Q&A 어조 분석 (`scripts/tone_analysis.py`)
- **직접 수행**: KPI 이동 감지 (`scripts/moving_targets_detector.py`)
- **템플릿**: `templates/management_credibility_scorecard.md` (Net Candor 병기)
- **템플릿**: `templates/earnings_qna_redflag_checklist.md` (FOG 카운팅 포함)
- **참조**: `references/us_market_specifics.md` 또는 `references/kr_market_specifics.md`

### [Step 4] Scuttlebutt & 대안 데이터 (D4, D5)
- **위임**: `alphaear-sentiment` 스킬에 ISQ 점수 요청
- **직접 수행**: 직원 리뷰·특허 데이터 수집
- **템플릿**: `templates/culture_innovation_check.md`
- **참조**: `references/data_source_tier.md`

### [Step 5] Red Teaming & 통합 Investment Memo
- **필수**: `references/bias_guardrails.md`의 5대 편향 점검
- **필수**: Pre-mortem 강제 질문 10개 (`references/workflow_5stage.md` §5)
- **직접 수행**: `scripts/rag_evidence_tracker.py`로 환각 검증
- **템플릿**: `templates/investment_memo.md` (최종 산출물)
- **템플릿**: `templates/green_red_flag_summary.md`

## MCP 우선순위 매트릭스

| 데이터 | KR 기업 | US 기업 |
|--------|---------|---------|
| 재무제표 | open-dart-reader (T1) | sec-edgar (T1) |
| **CEO 서한/사장 인사말** | open-dart-reader 사업보고서 (T1) | sec-edgar 10-K Annual Report PDF (T1) |
| 주가·재무요약 | kis MCP `env_dv:"real"` (T1) | yfinance (T2) |
| 뉴스·감성 | alphaear-news (T3) | alphaear-news (T3) |
| 경쟁사 동향 | brave-search / tavily (T3) | brave-search / tavily (T3) |
| Scuttlebutt | sequential-thinking (T4) | sequential-thinking (T4) |

## QualScore 산식

```
QualScore = D1×0.30 + D2×0.30 + D3×0.15 + D4×0.15 + D5×0.10
```

**D1 세부 (CANDOR-7 통합)**:
```
D1 = Quick Scorecard(5항목, 0-100) × 0.50
   + Candor Index(Net Candor Score 정규화, 0-100) × 0.30
   + Moving Targets 패턴(0-100) × 0.10
   + 내부자 거래 패턴(0-100) × 0.10
```

등급: A+(90~100) Buy | A(80~89) Buy | B+(70~79) Watch | B(60~69) Hold | C(50~59) Avoid | D(~49) Strong Avoid

자세한 산식·케이스별 행동지침: `references/decision_matrix.md`

## CANDOR-7 7-시스템 진단 격자 (요약)

| 시스템 | 위치(비유) | 핵심 질문 |
|--------|-----------|----------|
| ① Capital Stewardship | 중심축(Hub) | 자본을 주주로부터 '수탁'받은 것으로 다루는가 |
| ② Strategy | 좌뇌 | 복잡한 계획을 명료하게 단순화하는가 |
| ③ Accountability | 좌뇌 | 약속 목표와 실제 결과를 수치로 대조하는가 |
| ④ Vision | 우뇌 | 존재 목적과 혁신적 사고가 있는가 |
| ⑤ Leadership | 우뇌 | 투자자를 교육하려 하고 실수를 인정하는가 |
| ⑥ Stakeholder | 척추 | 고객·직원·주주 필요를 균형 있게 충족하는가 |
| ⑦ Candor | 척추 | 모든 시스템을 관통하는 투명성 (FOG 제거) |

각 시스템 0~5점 평가 → 레이더 프로필. 자세히: `references/candor7_framework.md`

## Net Candor Score (정량 채점)

```
가점:  정성적 목표 +5  |  정량적 목표 +10  |  목표 맥락 +5  |  Cash/FCF 언급 +3  |  FCF 맥락 +3
감점:  상투어 -3       |  위즐워드 -3      |  오웰 문장 -5  |  전략적 부조화 -10

Net Candor Score = Σ(가점) - Σ(감점)
Candor Index    = (1 - FOG비율) × 100,  FOG비율 = Σ감점 / (Σ가점 + Σ감점)
```

| Candor Index | 등급 | 의미 |
|--------------|------|------|
| 75~100 (FOG ≤ 25%) | 모범 | Candor Premium 후보 |
| 50~74 (FOG 25~50%) | 경계 | 추세·항목 모니터링 필요 |
| < 50 (Net Score < 0) | 위험 | 중대 문제 임박 신호 |

자세히: `references/fog_lexicon.md`

## 출력 형식

- 한국어 기본 (영문 용어 괄호 병기)
- HTML 절대 금지 — Markdown 전용
- 최종 산출물: `templates/investment_memo.md` 양식 준수
- 단계별 중간 산출물: 해당 템플릿 양식 사용

## 스킬 위임 매트릭스

| 요청 유형 | 이 스킬 | 위임 대상 |
|-----------|---------|---------|
| 종합 정성 분석·Investment Memo | ✅ 직접 수행 | — |
| **CEO 서한 CANDOR-7 분석** | ✅ 직접 수행 | — |
| **Net Candor Score 채점** | ✅ 직접 수행 | — |
| 해자 정밀 점수 (D2) | 결과 활용 | eco-moat-ai Stage 3 |
| 초기 재무 스크리닝 | 결과 활용 | financial-analysis |
| DCF 내재가치 | 결과 활용 | intrinsic-value-analyzer |
| ISQ 감성 점수 (D5) | 결과 활용 | alphaear-sentiment |
| 분기 Beat/Miss 정량 | 결과 활용 | earnings-analysis |
| 단순 주가 조회 | — | stock-analysis |

## 참조 파일 안내

- `references/dimension_framework.md` — D1~D5 차원 상세 + Green/Red Flag 정의 (D1에 CANDOR-7 매핑 추가)
- `references/candor7_framework.md` — **NEW** CANDOR-7 7-시스템 격자 + Net Candor Score 산식
- `references/fog_lexicon.md` — **NEW** Weasel/Cliché/Orwellian 영·한 사전 + 가점/감점 룰
- `references/case_library.md` — **NEW** 모범 5사(버크셔·포드·J&J·Expeditors·Dominion) + 실패 5사(엔론·AIG·리먼·WaMu·GM)
- `references/data_source_tier.md` — 4단계 신뢰도 + MCP 매핑
- `references/workflow_5stage.md` — 5단계 상세 + Gate + Pre-mortem 10문 (Step 3A 서한 포렌식 추가)
- `references/ai_nlp_techniques.md` — Semantic Diff / Tone / Moving Targets / RAG / FOG / Letter Forensics 기법
- `references/bias_guardrails.md` — 5대 편향 가드레일
- `references/decision_matrix.md` — 점수화 + 6케이스 행동지침 + Candor Index 매핑
- `references/kr_market_specifics.md` — DART 공시 코드 + open-dart-reader 패턴
- `references/us_market_specifics.md` — SEC Form 매핑 + sec-edgar 패턴

## 주의사항

- KIS MCP 호출 시 항상 `env_dv: "real"` 포함
- `import koreanize_matplotlib` 스크립트 최상단 (try/except 묵살 금지)
- 주장 생성 후 반드시 `scripts/rag_evidence_tracker.py`로 원문 교차검증
- eco-moat-ai가 "기업평가", "해자분석" 키워드로 이미 트리거된 경우 D2 결과를 활용하고 재호출 금지
- **CEO 서한 분석 시 반드시 수치 교차검증(Step 3A-2) 동반** — 언어 분석만으로는 정교한 은폐를 잡지 못함
- **Net Candor Score 절대값 < 전년 대비 delta** — 점수 급락이 펀더멘털 악화에 선행

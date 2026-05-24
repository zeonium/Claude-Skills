---
name: qualitative-company-analysis
description: |
  재무수치 너머의 'Why'를 분석하는 5단계 하이브리드 정성적 기업분석 오케스트레이터.
  다음 상황에서 MUST 사용: "정성적 분석", "Investment Memo", "경영진 신뢰도", "Moving Targets",
  "Pre-mortem", "하이브리드 투자 분석", "QualScore", "공시 텍스트 분석", "5단계 분석",
  "어조 분석", "KPI 이동", "Scuttlebutt", "적신호 청신호", "해자 지속성 가설".
  영어 트리거: "qualitative analysis", "investment memo", "management credibility",
  "moving targets", "pre-mortem analysis", "hybrid investment", "QualScore",
  "disclosure diff", "tone analysis".
  eco-moat-ai와의 차이: eco-moat-ai는 해자 점수화(D2 위임 수신자), 이 스킬은 5차원
  QualScore 통합 + 경영진 신뢰도 + Semantic Diff + Moving Targets + Investment Memo를
  담당하는 최상위 오케스트레이터.
---

# 정성적 기업분석 오케스트레이터

## 핵심 철학

재무수치(정량)는 '무엇이 일어났는가'를 말하고, 정성은 '왜, 그리고 앞으로도 그럴 것인가'를 답한다.
이 스킬은 두 관점을 통합하여 투자 의사결정의 질을 높인다.

## 사용 시점

- 종목에 대한 Investment Memo 작성 요청
- 경영진 신뢰도 또는 자본배분 능력 평가
- 컨퍼런스콜 어조·KPI 이동 분석
- 사업보고서/10-K 위험요인 연도별 변화 분석
- 기업문화·직원 리뷰·특허 혁신성 점검
- 정량 분석(financial-analysis) 이후 정성 심화 분석
- Pre-mortem / Red Teaming 구조화 요청

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

### [Step 3] 경영진 신뢰도 & 자본배분 (D1)
- **직접 수행**: 컨퍼런스콜 Q&A 어조 분석 (`scripts/tone_analysis.py`)
- **직접 수행**: KPI 이동 감지 (`scripts/moving_targets_detector.py`)
- **템플릿**: `templates/management_credibility_scorecard.md`
- **템플릿**: `templates/earnings_qna_redflag_checklist.md`
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
| 주가·재무요약 | kis MCP `env_dv:"real"` (T1) | yfinance (T2) |
| 뉴스·감성 | alphaear-news (T3) | alphaear-news (T3) |
| 경쟁사 동향 | brave-search / tavily (T3) | brave-search / tavily (T3) |
| Scuttlebutt | sequential-thinking (T4) | sequential-thinking (T4) |

## QualScore 산식

```
QualScore = D1×0.30 + D2×0.30 + D3×0.15 + D4×0.15 + D5×0.10
```

등급: A+(90~100) Buy | A(80~89) Buy | B+(70~79) Watch | B(60~69) Hold | C(50~59) Avoid | D(~49) Strong Avoid

자세한 산식·케이스별 행동지침: `references/decision_matrix.md`

## 출력 형식

- 한국어 기본 (영문 용어 괄호 병기)
- HTML 절대 금지 — Markdown 전용
- 최종 산출물: `templates/investment_memo.md` 양식 준수
- 단계별 중간 산출물: 해당 템플릿 양식 사용

## 스킬 위임 매트릭스

| 요청 유형 | 이 스킬 | 위임 대상 |
|-----------|---------|---------|
| 종합 정성 분석·Investment Memo | ✅ 직접 수행 | — |
| 해자 정밀 점수 (D2) | 결과 활용 | eco-moat-ai Stage 3 |
| 초기 재무 스크리닝 | 결과 활용 | financial-analysis |
| DCF 내재가치 | 결과 활용 | intrinsic-value-analyzer |
| ISQ 감성 점수 (D5) | 결과 활용 | alphaear-sentiment |
| 분기 Beat/Miss 정량 | 결과 활용 | earnings-analysis |
| 단순 주가 조회 | — | stock-analysis |

## 참조 파일 안내

- `references/dimension_framework.md` — D1~D5 차원 상세 + Green/Red Flag 정의
- `references/data_source_tier.md` — 4단계 신뢰도 + MCP 매핑
- `references/workflow_5stage.md` — 5단계 상세 + Gate + Pre-mortem 10문
- `references/ai_nlp_techniques.md` — Semantic Diff / Tone / Moving Targets / RAG 기법
- `references/bias_guardrails.md` — 5대 편향 가드레일
- `references/decision_matrix.md` — 점수화 + 6케이스 행동지침
- `references/kr_market_specifics.md` — DART 공시 코드 + open-dart-reader 패턴
- `references/us_market_specifics.md` — SEC Form 매핑 + sec-edgar 패턴

## 주의사항

- KIS MCP 호출 시 항상 `env_dv: "real"` 포함
- `import koreanize_matplotlib` 스크립트 최상단 (try/except 묵살 금지)
- 주장 생성 후 반드시 `scripts/rag_evidence_tracker.py`로 원문 교차검증
- eco-moat-ai가 "기업평가", "해자분석" 키워드로 이미 트리거된 경우 D2 결과를 활용하고 재호출 금지

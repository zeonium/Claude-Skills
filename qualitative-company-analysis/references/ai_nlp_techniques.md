# AI/NLP 기법 가이드 — qualitative-company-analysis

이 파일은 4가지 AI/NLP 분석 기법의 원리, 적용 방법, scripts/ 연결을 설명한다.
Claude는 각 기법의 입출력 형식을 이해하고 사용자에게 실행 안내를 제공한다.

---

## A1: Semantic Diff (공시 텍스트 YoY 의미론적 차이)

### 원리
두 연도의 공시 텍스트(위험요인, 사업 개요)를 문장 단위로 분리하고,
sentence-transformers 임베딩의 코사인 유사도로 신규·삭제·유지·표현 강도 변화를 탐지한다.

### 핵심 임계값

| 임계값 | 의미 |
|--------|------|
| cos < 0.65 | 신규 추가 또는 삭제 문장 |
| 0.65 ≤ cos < 0.95 | 변형된 문장 (hedging 강도 변화 탐지 구간) |
| cos ≥ 0.95 | Boilerplate (판에 박힌 문구) |

**Boilerplate 비율 해석**:
- < 40%: 실질적 업데이트 (D3 긍정)
- 40~60%: 중립
- > 60%: 공시 투명성 우려 (D3 하향)

### 한국어 vs 영어 차이

| 항목 | 영어 (EN) | 한국어 (KO) |
|------|-----------|-------------|
| 임베딩 모델 | all-MiniLM-L6-v2 | jhgan/ko-sroberta-multitask |
| 문장 분리 | 약어 보정 포함 | 마침표·느낌표·물음표 기준 |
| 데이터 소스 | SEC 10-K Item 1A | DART 사업보고서 위험요인 |

### scripts/semantic_diff_kit.py 연결

```bash
# 영어 (NVIDIA FY2023 vs FY2024)
python3 scripts/semantic_diff_kit.py \
  --prev nvda_2023_item1a.txt \
  --curr nvda_2024_item1a.txt \
  --lang en --company NVIDIA --out nvda_diff

# 한국어 (삼성전자 FY2023 vs FY2024)
python3 scripts/semantic_diff_kit.py \
  --prev samsung_2023_risk.txt \
  --curr samsung_2024_risk.txt \
  --lang ko --company 삼성전자 --out samsung_diff
```

**출력**: `{out}.json` + `{out}.md` (신규 문장 목록, 삭제 문장 목록, hedging 변화, 보일러플레이트 비율)

**D3 공시 투명성 점수 연동**:
- avg_cos < 0.70 + boilerplate < 40% → D3 점수 상향
- boilerplate > 60% + 신규 문장 수 < 10개 → D3 점수 하향

---

## A2: Tone Analysis (어조 분석)

### 원리
컨퍼런스콜 Q&A 텍스트에서 경영진의 언어 패턴을 4개 차원으로 정량화한다.

| 차원 | 내용 |
|------|------|
| 모호한 형용사 | "견조", "양호", "robust", "solid" 등 — 수치 없는 낙관 |
| 책임귀속(외부 탓) | 거시경제·공급망·규제·계절성 탓으로 실적 설명 |
| 과도한 낙관 | "역대 최고", "unprecedented growth" 등 |
| 방어적 표현 | "challenging", "cautious", "구체적 수치 어렵습니다" |

### 어조 판정 로직

```
외부 탓 ≥ 7건 OR 방어적 표현 ≥ 5건 → "방어적"
긍정(LM) > 부정(LM) × 2 AND 과도낙관 ≥ 3건 → "과도한 낙관"
그 외 → "중립/사실 위주"
```

### 영어 (Loughran-McDonald 사전)
금융 텍스트 특화 단어 분류:
- Negative / Positive / Uncertainty / Litigious / ModalWeak / ModalStrong

### 한국어 (KR-FinBert)
- 모델: snunlp/KR-FinBert-SC (문장 수준 긍정/부정 분류)
- 의존성: `pip3 install transformers torch --break-system-packages`
- 최대 200문장 처리 (컨퍼런스콜 Q&A 분량 기준 충분)

### scripts/tone_analysis.py 연결

```bash
# 영어
python3 scripts/tone_analysis.py \
  --input nvda_q4_transcript.txt --lang en --company NVIDIA --out nvda_tone

# 한국어
python3 scripts/tone_analysis.py \
  --input samsung_q4_transcript.txt --lang ko --company 삼성전자 --out samsung_tone
```

**출력**: `{out}.json` + `{out}.md` (패턴별 건수, 예시, 어조 판정)

**D1 경영진 신뢰도 연동**: 어조 판정 결과를 management_credibility_scorecard.md §2에 반영

---

## A3: Moving Targets Detector (KPI 이동 감지)

### 원리
분기별 컨퍼런스콜 트랜스크립트에서 KPI 키워드 언급 빈도를 집계하고,
직전 분기 대비 ±50% 이상 변화한 KPI를 "이동 목표"로 표시한다.

**급락 (≤ -50%)**: 경영진이 해당 KPI를 회피하는 신호 → 부정적 전망 은폐 의심
**급등 (≥ +50%)**: 새로운 성장 동력 강조로 투자자 시선 전환 의도 가능성

### KPI 사전 구성

**영어 KPI 사전** (주요 20개):
Revenue, Gross Margin, Operating Income, EBITDA, EPS, Free Cash Flow,
Data Center, Cloud, AI, Backlog, NRR, ARR, DAU/MAU, Inventory, Guidance,
HBM, CUDA, CapEx, Buyback, Dividend

**한국어 KPI 사전** (주요 21개):
매출, 영업이익, 순이익, 매출총이익, EBITDA, EPS, 잉여현금흐름,
HBM, DRAM, NAND, 파운드리, 데이터센터, AI, 수주잔고, 가동률,
재고, 가이던스, 자사주, 배당, 점유율, 수율, CapEx

### 감지 조건
- 전 분기 대비 변화율 ≥ 50% (절댓값)
- 이전 분기 기준 최소 언급 2회 이상 (노이즈 제거)

### scripts/moving_targets_detector.py 연결

```bash
# 4분기 영어 트랜스크립트
python3 scripts/moving_targets_detector.py \
  --transcripts q1.txt q2.txt q3.txt q4.txt \
  --quarters FY24Q1 FY24Q2 FY24Q3 FY24Q4 \
  --lang en --company NVIDIA --out nvda_kpi

# 차트 없이 실행
python3 scripts/moving_targets_detector.py \
  --transcripts q1.txt q2.txt q3.txt q4.txt \
  --quarters FY24Q1 FY24Q2 FY24Q3 FY24Q4 \
  --lang ko --company 삼성전자 --out samsung_kpi --no-chart
```

**출력**: `{out}.json` + `{out}.md` + `{out}_chart.html` (Plotly 대화형 차트)

**D1/D3 연동**:
- 급락 KPI ≥ 2개 → management_credibility_scorecard.md §3 적신호 기록
- 급락 KPI가 핵심 사업 KPI와 일치 → D1 점수 하향

---

## A4: RAG Evidence Tracker (주장-원문 매핑 환각 검출)

### 원리
Claude가 생성한 분석 주장(claim)과 원문 코퍼스(공시, 트랜스크립트) 간
코사인 유사도를 측정하여 AI 환각(hallucination)을 탐지한다.

### 임계값

| cos 범위 | 판정 |
|----------|------|
| ≥ 0.85 | 강한 근거 (원문 뒷받침 확실) |
| 0.70~0.85 | 약한 근거 (추가 확인 권장) |
| < 0.70 | 환각 의심 (원문 미확인) |

### 사용 시점
- Investment Memo 작성 후 주요 주장(5~20개) 검증
- 특히 수치·통계·순위 관련 주장은 반드시 검증
- cos < 0.70 주장은 Investment Memo §6 Evidence Trail에 "환각 의심" 표시

### scripts/rag_evidence_tracker.py 연결

```bash
# 영어 (주장 파일 + 복수 코퍼스)
python3 scripts/rag_evidence_tracker.py \
  --claims nvda_claims.txt \
  --corpus 10k_item1.txt conference_call.txt \
  --lang en --company NVIDIA --out nvda_evidence

# 한국어
python3 scripts/rag_evidence_tracker.py \
  --claims samsung_claims.txt \
  --corpus dart_business_report.txt earnings_transcript.txt \
  --lang ko --company 삼성전자 --out samsung_evidence
```

**claims.txt 형식** (한 줄 = 한 주장, # 시작줄 = 주석):
```
# NVIDIA FY2024 주요 주장
CUDA 개발자 생태계는 450만명 이상이다.
FY2024 Data Center 매출은 47.5B달러를 기록했다.
AMD ROCm의 시장 점유율은 5% 미만이다.
```

**출력**: `{out}.json` + `{out}.md` (주장별 cos 점수, 상위 3개 근거 문장, Evidence Trail 표)

**Investment Memo §6 연동**: 출력된 Evidence Trail 표를 그대로 붙여넣기 가능

---

## 4가지 기법 통합 워크플로우

```
Step 1 → financial-analysis (정량)
Step 2 → A1 Semantic Diff (D2/D3 공시 분석)
Step 3 → A2 Tone Analysis + A3 Moving Targets (D1 경영진)
Step 4 → alphaear-sentiment (D4/D5)
Step 5 → A4 RAG Evidence Tracker (환각 검증) → Investment Memo
```

**의존성 한 줄 설치**:
```bash
pip3 install sentence-transformers scikit-learn numpy transformers torch plotly pandas --break-system-packages
```

**모델 자동 선택 규칙**:
- `--lang en` → `all-MiniLM-L6-v2` (경량, 빠름)
- `--lang ko` → `jhgan/ko-sroberta-multitask` (한국어 특화)
- 커스텀 모델: `--model <모델명>` 인자로 오버라이드 가능

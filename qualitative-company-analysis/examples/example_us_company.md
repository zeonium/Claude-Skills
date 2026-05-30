# 적용 예시: NVIDIA Corporation (NVDA) — 5단계 정성적 분석

**분석 기준일**: FY2024 (2024년 1월 결산)
**QualScore**: 84/100 (A등급)
**최종 판정**: Buy (강한 정성적 근거)

---

## Step 1: 정량 스크리닝 → 정성 진입 결정

**financial-analysis 스킬 위임 결과:**

| 지표 | FY2024 | FY2023 | 변화 |
|------|--------|--------|------|
| 매출 YoY | +122% | +0.2% | 급등 |
| 영업이익률 | 54.1% | 16.0% | 급등 |
| FCF | $26.9B | $3.8B | +608% |
| ROE | 91.4% | 20.0% | 급등 |
| Beneish M-Score | -2.71 | -2.43 | 이상무 |

**정량 Gate 통과**: 매출 급등, 마진 확대, FCF 폭발적 성장 → 정성 분석으로 진입.

**핵심 정성 질문 도출:**
1. Data Center 매출 급등이 일시적 사이클인가, 구조적 전환인가?
2. CUDA 생태계 해자가 경쟁사 GPU/AI 가속기 진입을 장기 차단할 수 있는가?
3. 경영진(Jensen Huang)의 자본배분 판단력과 실행 신뢰도는?
4. HBM 공급망 병목이 매출 상한선을 제약하는가?

---

## Step 2: 해자 · 내러티브 분석 (D2)

**eco-moat-ai 스킬 위임 결과 (Stage 3 정밀 평가):**

| 해자 유형 | 점수(0~2) | 근거 |
|-----------|-----------|------|
| 네트워크 효과 | 2 | CUDA 개발자 450만명 → 전환비용 극대화 |
| 전환비용 | 2 | HPC 코드베이스 전면 재작성 없이 이탈 불가 |
| 비용우위 | 1 | TSMC 선단 공정 우선 배정 확보, 복제 어려움 |
| 무형자산 | 2 | 특허 4,000건+, cuDNN·TensorRT 등 소프트웨어 스택 |
| 규모의 경제 | 1 | AI 추론 칩 시장 성숙 시 AMD·Intel 추격 가능성 |

**eco-moat-ai 종합**: 4단계 해자 (Score 8/10)

**내러티브 검증 (SEC 10-K Item 1A Semantic Diff, scripts/semantic_diff_kit.py):**

```bash
python3 scripts/semantic_diff_kit.py \
  --prev nvda_2023_item1a.txt --curr nvda_2024_item1a.txt \
  --lang en --company NVIDIA --out nvda_diff
```

| 항목 | 값 |
|------|---|
| 평균 코사인 유사도 | 0.74 (유의미한 변화) |
| 신규 추가 문장 | 47개 |
| 삭제된 문장 | 12개 |
| Boilerplate 비율 | 31% (낮음 — 실질 업데이트) |

**신규 추가 위험요인 (상위 3개):**
1. "Export control regulations ... China revenue impact" (cos=0.21, 심각도: 상)
2. "Sovereign AI initiatives creating fragmented demand" (cos=0.31, 심각도: 중)
3. "HBM supply concentration with limited suppliers" (cos=0.38, 심각도: 중)

**해자 지속성 가설** (templates/moat_durability_hypothesis.md 참조):
- 가설: "CUDA 생태계 전환비용은 2027년까지 유효하다"
- 반증 조건: AMD ROCm 채택률 > 15% 또는 Google TPU 외부 판매 확대
- 모니터링 주기: 분기별 개발자 설문 + 클라우드 GPU 점유율 추적

**D2 점수: 88/100**

---

## Step 3: 경영진 신뢰도 평가 (D1)

**management_credibility_scorecard.md 작성:**

| 항목 | 점수 | 근거 |
|------|------|------|
| 가이던스 정확도 | 2/2 | 4분기 연속 EPS Beat +15%~+30%; 과소 가이던스 전략 |
| 자본배분 일관성 | 2/2 | FY2024 R&D $8.7B(+51%), CapEx 절제, 자사주 소각 $9.5B |
| 위기관리 이력 | 1/2 | 2022 암호화폐 급락 재고 충격 0.5분기 만에 조정 (소폭 감점) |
| Q&A 투명성 | 2/2 | 수출통제 영향 구체적 수치 공개, 좋은 질문 회피 없음 |
| 임원진 안정성 | 2/2 | Jensen Huang 31년 재임, CFO·COO 5년 이상 유지 |

**합계: 9/10 → D1 점수: 90/100**

**Moving Targets 분석** (scripts/moving_targets_detector.py):

```bash
python3 scripts/moving_targets_detector.py \
  --transcripts nvda_q1.txt nvda_q2.txt nvda_q3.txt nvda_q4.txt \
  --quarters FY24Q1 FY24Q2 FY24Q3 FY24Q4 \
  --lang en --company NVIDIA --out nvda_kpi
```

| KPI | FY24Q1 | FY24Q2 | FY24Q3 | FY24Q4 | 변화% | 판정 |
|-----|--------|--------|--------|--------|-------|------|
| Data Center | 8 | 14 | 19 | 22 | +57% | 강조 전환 |
| Gaming | 12 | 9 | 6 | 4 | -67% | 급락(자연적) |
| Guidance | 6 | 8 | 9 | 10 | +25% | 정상 |

**Moving Target 적신호**: 없음 — Gaming 언급 감소는 사업 믹스 변화로 자연스러움.

**Q&A 적신호 체크리스트**: 10개 항목 중 0개 해당 → 청신호.

**어조 분석** (scripts/tone_analysis.py):

```bash
python3 scripts/tone_analysis.py \
  --input nvda_q4_transcript.txt --lang en --out nvda_tone
```

| 패턴 | 건수 |
|------|------|
| 모호한 형용사 | 8건 (robust, solid 등) |
| 책임귀속(외부 탓) | 2건 (수출통제 관련 — 합리적) |
| 과도한 낙관 | 1건 |
| 방어적 표현 | 3건 |

**어조 판정**: 중립/사실 위주 (방어적 표현 임계값 미달)

---

## Step 4: Scuttlebutt & 대안 데이터 수집 (D4, D5)

**alphaear-sentiment 스킬 위임 결과:**
- Glassdoor 평점: 4.4/5.0 (엔지니어 문화 우수)
- 최근 12개월 이직률 추정: 낮음 (주요 경쟁사 대비 -15%)
- 특허 출원 FY2024: 1,247건 (+34% YoY)

**기업문화 & 혁신 체크포인트** (templates/culture_innovation_check.md 참조):
- Glassdoor 긍정 키워드: "brilliant people", "fast-paced", "world-changing work"
- 부정 키워드: "work-life balance", "bureaucracy increasing"
- D4 신호: 긍정적. 단, 조직 규모 확대에 따른 관료화 리스크 모니터링 필요

**공급망 채널 체크:**
- TSMC N4P 웨이퍼 투입 우선순위 확보 (업계 관계자 인터뷰 기사 3건 교차확인)
- CoWoS 패키징 TSMC 독점 공급 → HBM 포함 AI 칩 생산 병목 = 공급 제약 리스크

**D4 점수: 75/100** (기업문화 우수, 공급망 집중 리스크 감점)
**D5 점수: 80/100** (Glassdoor + 특허 + 채용 데이터 3중 교차)

---

## Step 5: Red Teaming · Pre-mortem · 통합 의사결정

### Pre-mortem 강제 10문

1. **지금으로부터 2년 후 이 투자가 실패했다면, 가장 그럴듯한 이유는?**
   → AMD MI300X + ROCm 성숙 → HPC 고객 일부 전환, 수출통제 심화 → 중국 매출 0

2. **이 회사의 숫자 중 내가 가장 믿기 어려운 것은?**
   → Data Center 매출의 '최종 수요' vs '재고 축적' 구분 불가 (고객: CSP 중간 집계)

3. **내가 이 회사를 좋아하는 이유가 분석을 오염시키고 있는가?**
   → 후광 편향 경고: Jensen Huang의 카리스마 → CUDA 해자의 지속성을 과대평가할 위험

4. **시장이 이미 이 정보를 아는데 내가 Edge가 있는가?**
   → 단기 Edge 없음. 장기 Edge: CUDA 생태계 복제 가능성 낮음을 신뢰한다는 판단

5. **가장 큰 경쟁위협이 내부에서 온다면?**
   → 주요 CSP(AWS Trainium, Google TPU, Microsoft Maia)의 내재화 가속

6. **이 회사의 규제 위험이 내 시나리오에서 과소평가되었는가?**
   → 수출통제 단계적 강화 시 FY2025 매출 5~8% 하향 리스크 존재

7. **경영진이 지금 주주를 속이고 있다면 어떤 방식으로?**
   → 비현금 보상 비율: FY2024 SBC $2.1B (매출의 2.5%) — 합리적 수준

8. **내 분석에서 가장 약한 고리는?**
   → Step 4 Scuttlebutt: 공급망 채널 체크가 2차 뉴스 기반 (직접 채널 제한)

9. **5년 후 이 해자가 사라진다면?**
   → AI 모델 경량화 → GPU당 연산 효율 10x 향상 시 수요 감소 가능

10. **포지션 크기를 절반으로 줄여야 한다면 그 이유는?**
    → P/E 60x에서의 밸류에이션 리스크 + 중국 수출통제 불확실성

### QualScore 최종 산출

| 차원 | 점수 | 가중치 | 기여 |
|------|------|--------|------|
| D1 경영진 신뢰도 | 90 | 30% | 27.0 |
| D2 해자 내러티브 | 88 | 30% | 26.4 |
| D3 공시 투명성 | 80 | 15% | 12.0 |
| D4 기업문화 | 75 | 15% | 11.25 |
| D5 대안 데이터 | 80 | 10% | 8.0 |
| **QualScore** | **84** | **100%** | **84.65** |

**등급: A (80~89) → Buy**

### 정량×정성 2D 매트릭스

- 정량 점수 (financial-analysis): 88/100 (강함)
- 정성 점수 (QualScore): 84/100 (강함)
- **케이스: Strong Buy Zone** → 포지션 크기 기준 비중의 1.5x까지 가능

단, 아래 조건 충족 시 재평가:
- 중국 매출 비중 > 20% 유지 상태에서 추가 수출통제 확대
- AMD ROCm 개발자 채택률 > 10% 돌파
- CSP 자체 칩 비중 AI 인프라 투자의 30% 초과

---

## Investment Memo 요약

**회사**: NVIDIA Corporation (NASDAQ: NVDA)
**기준일**: FY2024 (2024-01-28 결산)
**판정**: **Buy** | QualScore 84/100 (A등급)
**투자 포인트**: CUDA 생태계 해자(네트워크 효과+전환비용) 복합 방어선, Jensen Huang의 자본배분 신뢰도 최상위급, AI 인프라 수요의 구조적 전환 (사이클이 아닌 secular trend)

**핵심 리스크**: 수출통제 강화 → 중국 매출 소멸, CSP 자체 칩 내재화 가속, HBM 공급 병목

**RAG Evidence Trail 요약** (scripts/rag_evidence_tracker.py):

| # | 주장 | cos | 판정 |
|---|------|-----|------|
| 1 | CUDA 개발자 450만명 생태계 | 0.91 | 강한 근거 |
| 2 | FY2024 Data Center 매출 $47.5B | 0.96 | 강한 근거 |
| 3 | AMD ROCm 시장 점유율 5% 미만 | 0.73 | 약한 근거 |
| 4 | 중국 수출통제 미래 확대 가능성 | 0.68 | 약한 근거 |

**환각 의심**: 0건 / 4건 검증

[Source: SEC 10-K FY2024, FY2024Q4 컨퍼런스콜 트랜스크립트, Glassdoor 리뷰 2024]

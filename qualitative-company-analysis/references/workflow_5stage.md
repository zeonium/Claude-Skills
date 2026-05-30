# 5단계 워크플로우 상세

## Step 1: 정량 스크리닝 → 정성 진입 결정

**목적**: 정성 분석이 의미 있는 기업을 선별한다.

**처리**:
1. financial-analysis 스킬에 위임: "재무 스크리닝 및 Red Flag 점검"
2. 핵심 확인 지표:
   - Gross Margin 5년 추세 (방어 여부)
   - Beneish M-Score (< -1.78 → 이익조작 낮음)
   - FCF Margin (양수 지속 여부)
   - ROE vs. WACC 비교

**Gate 1 (Step 2 진입 조건)**:
- [ ] Gross Margin 방어 또는 상승 추세
- [ ] Beneish M-Score < -1.78 (이익조작 가능성 낮음)
- [ ] FCF 양수 지속 (최근 2년 이상)

**편향 경보**: 사후확신 편향 — 최근 주가 상승 기업을 우선 분석하려는 경향 경계.

---

## Step 2: 해자 & 경쟁 우위 분석

**목적**: 현재 수익성이 5~10년 유지될 구조적 근거를 찾는다.

**처리**:
1. eco-moat-ai 스킬 Stage 3 위임: 5대 해자 정밀 평가
2. Semantic Diff 실행:
   ```bash
   python3 scripts/semantic_diff_kit.py \
     --prev [이전연도]_risk.txt \
     --curr [현재연도]_risk.txt \
     --lang [en|ko] --company [회사명]
   ```
3. 공시 위험요인 신규 문장 분석 → `templates/disclosure_diff_report.md` 작성
4. 해자 지속성 가설 수립 → `templates/moat_durability_hypothesis.md` 작성

**Gate 2 (Step 3 진입 조건)**:
- [ ] 해자 원천 2개 이상 확인
- [ ] Semantic Diff 평균 cos < 0.85 (변화 없음) 또는 변화의 성격 파악 완료

**편향 경보**: 후광 효과 — 유명 CEO/브랜드에 의해 해자 강도를 과대평가하지 않도록 정량 지표로 재검증.

---

## Step 3: 경영진 신뢰도 & 자본배분 (CANDOR-7 + 5단계 포렌식)

**목적**: 경영진이 주주 대리인 역할을 충실히 하는지 평가한다.
**원칙**: 컨퍼런스콜만 보던 한계를 극복하고, CEO 연례 주주 서한이라는 가장 응축된 텍스트를 포렌식 분석한다.

---

### Step 3A: CEO 주주 서한 포렌식 (Rittenhouse 5단계, 신규)

**입력 데이터**:
- KR: DART 사업보고서 'CEO/사장의 인사말' 섹션 또는 별도 주주서한 PDF
- US: 10-K Annual Report 첫 페이지 또는 별도 Letter to Shareholders PDF (Berkshire 등)
- 최소 분석 단위: 최근 1년 (이상적: 최근 3년 시계열 비교)

**5단계 포렌식 절차**:

**[STEP 3A-1] 레드펜 테스트 — FOG 정량 채점**
```bash
python3 scripts/fog_lexicon_scorer.py \
  --input letter_FY2024.txt \
  --lang [en|ko] \
  --company [회사명] \
  --out [회사명]_fog
```
→ Net Candor Score, Candor Index, Weasel/Cliché/Orwellian 카운트 산출.
→ 결과를 `templates/ceo_letter_candor7_report.md` §3에 기록.

**[STEP 3A-2] 수치 교차검증 — 서한 vs 감사보고서**
- 서한에서 인용된 매출·순이익·EPS·FCF 수치를 10-K/사업보고서 실제 수치와 대조.
- 불일치 시: 각주의 일회성 비용·구조조정·손상차손 추적.
- **엔론 패턴**: 13억 달러 *선언* vs 실제 9.79억 — 이 단계에서만 잡힘.
→ `templates/ceo_letter_candor7_report.md` §4 기록.

**[STEP 3A-3] FCF 맥락 평가 — 자본 수탁 의식**
```bash
python3 scripts/ceo_letter_forensics.py \
  --input letter_FY2024.txt \
  --check fcf \
  --lang [en|ko]
```
→ 자동 검사 항목:
- FCF 단어 언급 횟수
- FCF 정의 제시 여부 (Y/N)
- 5년 전 FCF 대조 여부 (Y/N)
- FCF 사용처 명시 여부 (Y/N)

→ J&J Larsen 2001 패턴 충족 시 ① Capital Stewardship +2점.

**[STEP 3A-4] 전략적 일관성 — 최근 3년 서한 비교**
```bash
python3 scripts/semantic_diff_kit.py \
  --prev letter_FY2022.txt \
  --curr letter_FY2024.txt \
  --lang [en|ko] --company [회사명]
```
- 평균 cos ≥ 0.85: 전략 일관 (Ford 'One Plan' 패턴) → ② Strategy +2
- 평균 cos < 0.65: 전략 유행어 교체 (GM 패턴) → ② Strategy 감점

**[STEP 3A-5] 실수 대처법 — 귀인 분석**
```bash
python3 scripts/ceo_letter_forensics.py \
  --input letter_FY2024.txt \
  --check mistake \
  --lang [en|ko]
```
→ 자동 검사:
- 실수 인정 키워드 빈도 ("we failed", "we missed", "우리가 잘못")
- 외부 탓 키워드 빈도 (매크로·환율·규제)
- 비율 = (인정) / (인정 + 외부탓)
- 비율 ≥ 50%: Expeditors 패턴 → ⑤ Leadership +2
- 비율 < 20%: GM 외부탓 패턴 → ⑤ Leadership -1

**[Step 3A 출력]**:
- `templates/ceo_letter_candor7_report.md` 작성
- 7-시스템 레이더 (0~5 × 7축)
- Net Candor Score + Candor Index
- Candor 등급: 모범/경계/위험

---

### Step 3B: 컨퍼런스콜 Q&A (기존 강화)

1. 컨퍼런스콜 Q&A 어조 분석:
   ```bash
   python3 scripts/tone_analysis.py --input transcript.txt --lang [en|ko]
   ```
2. Moving Targets 감지:
   ```bash
   python3 scripts/moving_targets_detector.py \
     --transcripts q1.txt q2.txt q3.txt q4.txt \
     --quarters FY24Q1 FY24Q2 FY24Q3 FY24Q4 --lang [en|ko]
   ```
3. **신규**: Q&A 응답에도 `fog_lexicon_scorer.py` 적용 — 즉흥 발언에서 FOG 농도가 더 높음.
4. 내부자 거래 분석 (SEC Form 4 / DART 임원공시)
5. 자본배분 이력 검토 (자사주·배당·M&A 타이밍)
6. `templates/management_credibility_scorecard.md` 작성 (Net Candor 병기)
7. `templates/earnings_qna_redflag_checklist.md` 작성 (FOG 카운팅 포함)

---

**Gate 3 (Step 4 진입 조건)**:
- [ ] 경영진 신뢰도 점수 ≥ 5/10 (또는 근거 기반 패스)
- [ ] Moving Target 적신호 3개 이하
- [ ] **Candor Index ≥ 50 (또는 Net Candor Score 양수)**
- [ ] **수치 교차검증 통과 (서한 vs 감사보고서 불일치 없음)**

**Gate 3 위반 시 처리**:
- Candor Index < 50: 자동 C등급 후보. Step 4·5 진행하되 가중치 보정.
- Net Score (+) → (-) 전환: 알림 트리거 발동, 직전 4분기 이내 펀더멘털 변화 재검토.
- 수치 불일치: 즉시 STOP — 회계 품질 검증 우선 (financial-analysis 재호출).

**편향 경보**: 확증 편향 — "경영진이 좋은 것 같다"는 가설 검증보다 반증 탐색에 집중.
**편향 경보 (CANDOR-7 한정)**: 후광 효과 — 카리스마 있는 CEO의 서한은 위즐워드도 진솔하게 보임. 정규식 카운팅으로 객관화.

---

## Step 4: Scuttlebutt & 대안 데이터

**목적**: 공식 서사와 현장 신호의 일치 여부를 확인한다.

**처리**:
1. alphaear-sentiment에 ISQ 점수 요청
2. 직원 리뷰 수집 (Glassdoor/잡플래닛 검색)
3. 독성 키워드 빈도 계산
4. 특허 분석 (KIPRIS/USPTO)
5. `templates/culture_innovation_check.md` 작성
6. Divergence 탐지: 공식 서사 vs. Scuttlebutt 신호 불일치 여부

**Gate 4 (Step 5 진입 조건)**:
- [ ] 심각한 Divergence 없음 (있으면 원인 파악 필수)
- [ ] D4, D5 점수 산출 완료

**편향 경보**: 표본 편향 — Glassdoor 리뷰는 이직자 과대 대표, 만족 직원은 리뷰 적게 작성.

---

## Step 5: Red Teaming & Investment Memo

**목적**: 편향을 제거하고 투자 판단의 오류를 사전에 찾아낸다.

**처리**:
1. 5대 편향 가드레일 점검 (`references/bias_guardrails.md`)
2. **Pre-mortem 강제 질문 10개** (아래 참조 — 생략 불가)
3. RAG Evidence Tracker 실행:
   ```bash
   python3 scripts/rag_evidence_tracker.py \
     --claims claims.txt --corpus 10k.txt transcript.txt
   ```
4. `templates/green_red_flag_summary.md` 작성
5. `templates/investment_memo.md` 작성 (최종 산출물)

### Pre-mortem 강제 질문 10개 (생략 불가)

1. 이 분석이 틀리려면 어떤 가정이 틀려야 하는가?
2. 이 기업의 핵심 해자가 3년 내 잠식된다면 어떤 시나리오인가?
3. 경영진이 투자자를 오도하고 있다면 어떤 신호를 숨기고 있을까?
4. 현재 P/E(또는 P/B)가 30% 하락해도 여전히 매력적인가?
5. 주요 고객 3개사가 동시에 이탈하면 매출 영향은 얼마인가?
6. 규제 리스크가 현실화되면 가장 먼저 무너지는 사업은?
7. 이 분석에서 내가 의도적으로 외면한 정보는 무엇인가? (확증 편향 점검)
8. 경쟁사의 최선의 시나리오는 무엇이며, 이 기업을 어떻게 위협하는가?
9. 5년 후 이 산업의 구조가 어떻게 바뀌어 있을 가능성이 가장 높은가?
10. AI 환각 검증: 이 메모에서 원문 확인이 안 된 주장이 있는가?

**편향 경보**: AI 환각 — RAG Evidence Tracker 없이 생성된 수치나 주장을 그대로 사용하지 말 것.

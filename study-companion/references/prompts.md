# 프롬프트 라이브러리

Study Companion 스킬에서 사용하는 9개 프롬프트 템플릿.  
모두 한국어, 격식체. NotebookLM MCP의 `notebook_query` 또는 전용 도구에 전달한다.

---

## 6.1 SUMMARY_3LAYER_TPL

```
[ROLE]
당신은 교육 콘텐츠 디자이너입니다. 학습자가 특정 섹션을 처음 접한 직후, 
빠르게 요점을 파악하고 깊이를 더할 수 있도록 3계층 요약을 작성합니다.

[CONTEXT]
교재명: {book_title}
섹션: {section_title}

[TASK]
다음 3개 계층의 요약을 JSON으로 출력하세요.

- L1 (한 줄, 25자 이내): 이 섹션의 핵심 메시지를 한 문장으로
- L2 (1단락, 100~150자): 핵심 개념 3~5개를 자연스러운 문장으로 연결
- L3 (심화, 400~500자): 정의·예시·주의점·연결되는 다른 개념까지 포함

[CONSTRAINTS]
- 노트북 내 원문 기반으로만 작성하세요.
- 추측하지 말고, 모르는 것은 명시하세요.
- 모든 출력은 한국어, 격식 있는 문체.

[OUTPUT FORMAT]
{"L1": "...", "L2": "...", "L3": "..."}
```

---

## 6.2 SOCRATIC_TPL

```
[ROLE]
당신은 소크라테스식 튜터입니다. 학습자가 단순 암기에서 비판적 사고로 
나아가도록 5단계 발문 시퀀스를 설계합니다.

[CONTEXT]
주제: {section_title}
학습자 수준: {learner_level}

[TASK]
5단계 발문 시퀀스를 JSON 배열로 출력하세요.
각 단계는 이전 단계보다 깊은 사고를 요구해야 합니다.

단계 구조:
1. 기억 (핵심 개념 정의 요청)
2. 이해 (자신의 말로 설명 요청)
3. 적용 (구체적 상황에 적용)
4. 분석 (원인·결과·관계 분석)
5. 평가 (비판적 판단 요청)

[CONSTRAINTS]
- 정답을 문항 안에 노출하지 마세요.
- 각 질문은 30자 이내로 명확하게.

[OUTPUT FORMAT]
[
  {"step": 1, "question": "...", "hint": "...", "model_answer": "..."},
  ...
]
```

---

## 6.3 REFLECTION_TPL

```
[ROLE]
당신은 메타인지 코치입니다. 학습자가 오늘의 학습을 돌아보고 
자신의 이해 상태를 정확히 파악하도록 돕는 질문을 설계합니다.

[CONTEXT]
오늘 학습한 섹션: {section_title}
완료된 형성평가 점수: {score_pct}%

[TASK]
다음 3가지 유형의 메타인지 질문을 각 1개씩 생성하세요.

1. 이해 확인: "오늘 가장 잘 이해한 개념은 무엇이었나요?"
2. 불확실 인식: "아직 완전히 이해되지 않은 부분이 있다면?"
3. 연결 짓기: "오늘 배운 내용이 실생활/이전 지식과 어떻게 연결되나요?"

[OUTPUT FORMAT]
["질문1", "질문2", "질문3"]
```

---

## 6.4 EXAMPLES_TPL

```
[ROLE]
당신은 학습 콘텐츠 제작자입니다. 추상적 개념을 쉬움/중간/어려움 3단계의 
워크드 예제로 구체화합니다.

[CONTEXT]
섹션: {section_title}
학습자 수준: {learner_level}

[TASK]
3개의 워크드 예제를 생성하세요.
각 예제는 문제 → 풀이 과정 → 정답 구조를 갖춰야 합니다.

[OUTPUT FORMAT]
[
  {"difficulty": "easy", "problem": "...", "steps": ["단계1", ...], "answer": "..."},
  {"difficulty": "medium", "problem": "...", "steps": [...], "answer": "..."},
  {"difficulty": "hard", "problem": "...", "steps": [...], "answer": "..."}
]
```

---

## 6.5 APPLICATION_TPL

```
[ROLE]
당신은 실무 교육 전문가입니다. 학습한 개념을 실제 상황에 적용하는 
시나리오를 설계합니다.

[CONTEXT]
섹션: {section_title}

[TASK]
이 개념을 실생활 또는 실무에 적용한 시나리오 3개를 생성하세요.
각 시나리오는 상황 설명 + 개념 적용 방법 + 예상 효과를 포함합니다.

[OUTPUT FORMAT]
[
  {"scenario": "...", "application": "...", "outcome": "..."},
  ...
]
```

---

## 6.6 DIAGNOSTIC_TPL

진단 평가 (온보딩 시 1회 사용):

```
교재 '{book_title}'의 다음 핵심 주제들을 바탕으로 진단 평가 문항 5개를 생성해 주세요.

주제 목록:
{topics_list}

요구사항:
- 각 주제당 1문항, 4지선다 형식
- 난이도: 1.0(매우 쉬움) ~ 5.0(어려움) 균등 분포
- 정답과 100자 이내 해설 포함
- 한국어, 격식 있는 문체

JSON 형식:
{"items": [{"id":"d1","prompt":"...","options":["①","②","③","④"],"answer":"①","difficulty":1.0,"concept":"...","explanation":"..."}]}
```

---

## 6.7 WEAKNESS_CLINIC_TPL

약점 클리닉 (SRS 재학습 시 사용):

```
학습자가 '{concept_title}' 개념에서 반복적으로 오답을 보이고 있습니다.

오답 증거: {evidence}

다음을 수행해 주세요:
1. 이 개념을 더 단순한 언어로 재설명 (비유 포함)
2. 흔히 헷갈리는 오해 2가지 지적
3. 이 개념을 확실히 이해하기 위한 핵심 질문 1개 제시

한국어, 격식체로 작성하세요.
```

---

## 6.8 CHAPTER_EXTRACT_TPL

챕터 구조 추출 (커리큘럼 생성 시 사용):

```
이 노트북의 내용을 분석하여 학습 챕터 구조를 제안해 주세요.

요구사항:
- 챕터 수: 5~15개 (내용 분량에 따라 조정)
- 각 챕터: 제목 + 핵심 개념 3~5개 + 예상 학습 시간(분)
- 챕터 간 선수 관계 명시

JSON 형식:
{"chapters": [{"title":"...","key_concepts":["개념1"],"estimated_minutes":60,"prerequisites":[]}]}
```

---

## 6.9 MILESTONE_REPORT_TPL

주차별 마일스톤 보고서 (자동 생성):

```
Week {week_number} 학습 마일스톤 보고서를 작성해 주세요.

이번 주 학습 내용: {week_theme}
완료된 섹션: {completed_sections}
평균 점수: {avg_score}%
약점 개념: {weak_concepts}

다음을 포함한 마크다운 보고서:
1. 이번 주 학습 요약 (200자)
2. 달성한 Bloom 목표 체크리스트
3. 약점 개념별 보완 계획
4. 다음 주 예습 권고사항

한국어, 격식체.
```

---

## 6.10 CHAPTER_QUIZ_TPL

챕터 종료 후 확인 퀴즈 (10문항, 4지선다 객관식):

```
[ROLE]
당신은 교육 평가 전문가입니다. 학습자가 한 챕터를 완료한 직후, 
핵심 개념의 이해 여부를 점검하는 확인 퀴즈를 설계합니다.

[CONTEXT]
교재명: {book_title}
챕터: {chapter_title}
핵심 개념 목록: {key_concepts_list}

[TASK]
아래 조건을 만족하는 4지선다 객관식 10문항을 생성하세요.

난이도 배분:
- 초(기억·이해, Bloom: Remember/Understand): 4문항
- 중(적용·분석, Bloom: Apply/Analyze): 4문항
- 상(평가·통합, Bloom: Evaluate/Create): 2문항

각 문항 구조:
- 문항 번호 및 난이도 태그
- 문제 (명확한 4지선다)
- 정답 (①②③④ 중 하나)
- 해설 (100자 이내, 오답 이유 포함)
- 관련 개념 태그

[CONSTRAINTS]
- 정답이 선택지에 노출되지 않도록 paraphrase 처리
- 선택지 길이 균형 유지
- 모든 문항은 노트북 내 원문 기반

[OUTPUT FORMAT]
{
  "quiz_id": "chapter-quiz-{chapter_id}",
  "chapter": "{chapter_title}",
  "items": [
    {
      "id": "q1",
      "difficulty": "초",
      "bloom_level": "Remember",
      "prompt": "...",
      "options": ["①...", "②...", "③...", "④..."],
      "answer": "②",
      "explanation": "...",
      "concept": "..."
    }
  ]
}
```

---

## 6.11 EXAM_PREP_TPL

중간고사·기말고사 대비 문제 생성 (범주별·난이도별 각 5문항):

```
[ROLE]
당신은 대학 시험 출제 전문가입니다. 학습자가 중간고사 또는 기말고사를 
준비할 수 있도록 범주별·난이도별 균형 잡힌 문제집을 설계합니다.

[CONTEXT]
교재명: {book_title}
시험 유형: {exam_type}  ← "중간고사" 또는 "기말고사"
범위 챕터: {chapter_range}
전체 핵심 개념: {all_key_concepts}

[TASK]
다음 6개 세트(범주 2 × 난이도 3)로 각 5문항씩 총 30문항을 생성하세요.

세트 구성:
1. 기본개념 × 난이도 초 (Bloom: Remember/Understand)
2. 기본개념 × 난이도 중 (Bloom: Apply/Analyze)
3. 기본개념 × 난이도 상 (Bloom: Evaluate/Create)
4. 응용분야 × 난이도 초 (실제 사례 인식)
5. 응용분야 × 난이도 중 (사례 분석·비교)
6. 응용분야 × 난이도 상 (복합 상황 판단)

각 문항 구조:
- 4지선다 객관식
- 정답 + 상세 해설 (150자 이내)
- 관련 챕터 및 개념 태그

[CONSTRAINTS]
- 같은 개념이 중복 출제되지 않도록 분산
- 응용분야 문항은 실제 투자·경제·과학 등 현실 맥락 활용
- 상위 난이도 문항은 2개 이상의 개념을 통합

[OUTPUT FORMAT]
{
  "exam_type": "{exam_type}",
  "scope": "{chapter_range}",
  "sets": [
    {
      "category": "기본개념",
      "difficulty": "초",
      "items": [
        {
          "id": "bc-e1",
          "prompt": "...",
          "options": ["①...", "②...", "③...", "④..."],
          "answer": "①",
          "explanation": "...",
          "chapter": "Ch01",
          "concept": "..."
        }
      ]
    }
  ]
}
```

---

## 6.12 INFOGRAPHIC_THINKING_TPL

Sequential Thinking을 활용한 전문 인포그래픽 설계 프롬프트:

```
[SEQUENTIAL THINKING TASK]
당신은 교육 시각화 전문가입니다. 아래 챕터의 핵심 개념들을 
전문 출판물 수준의 인포그래픽으로 설계합니다.

입력 정보:
- 교재명: {book_title}
- 챕터: {chapter_title}
- 핵심 개념 목록: {key_concepts_list}
- 개념 간 관계: {concept_relationships}

다음 단계를 순서대로 수행하세요:

STEP 1 — 정보 계층 분석
  - 가장 중심적인 "앵커 개념" 1개를 선정하라
  - 1차 연결 개념(직접 파생) / 2차 연결 개념(간접 관련) 분류
  - 선수 관계(화살표 방향)와 상호 의존 관계 구분

STEP 2 — 시각적 레이아웃 설계
  다음 중 내용에 최적인 레이아웃을 선택하고 그 이유를 명시하라:
  A) 방사형 마인드맵 — 앵커 개념 중심, 방사형 확장
  B) 계층형 트리 — 선수 관계가 명확한 경우
  C) 순환 플로우 — 프로세스·사이클 개념
  D) 비교 매트릭스 — 대조·비교가 핵심인 경우
  E) 타임라인 — 발전 과정·역사적 흐름

STEP 3 — 색상 및 타이포그래피 체계
  - 주색상 1개 + 보조색상 2개 (16진수 코드 포함)
  - 폰트 위계 (제목/소제목/본문/캡션)
  - 아이콘 스타일 (라인/솔리드/두오톤 중 선택)

STEP 4 — Mermaid 코드 생성
  Step 1~3을 바탕으로 Mermaid flowchart 또는 mindmap 코드를 작성하라.
  - 노드 레이블은 간결하게 (10자 이내)
  - 관계 유형별 화살표 스타일 구분 (-->, -.->. ==>, ---|)
  - 중요도에 따른 노드 스타일 구분 (:::important, :::secondary)

STEP 5 — 자연어 레이아웃 설계서
  실제 그래픽 디자이너 또는 Canva/Figma 사용자가 재현할 수 있도록
  다음을 포함한 설계서를 작성하라:
  - 전체 캔버스 크기 및 여백
  - 각 요소의 배치 좌표 (%)
  - 화살표 연결 목록
  - 범례 및 주석 위치

STEP 6 — 검토 및 개선
  설계된 인포그래픽이 다음 기준을 충족하는지 자기 검토:
  □ 5초 내에 핵심 메시지 전달 가능한가?
  □ 색맹 사용자도 구분 가능한 색상인가?
  □ 개념 간 관계가 방향성 있게 표현되었는가?
  □ 불필요한 장식 요소가 제거되었는가?
  미충족 항목이 있으면 해당 단계를 수정하라.

[OUTPUT]
- Mermaid 코드 블록 (즉시 렌더링 가능)
- 자연어 레이아웃 설계서 (전문 디자이너 전달용)
```

---

## 6.13 ANALOGY_METAPHOR_TPL — 비유·은유 생성 (v2.3)

추상 개념을 학습자가 이미 잘 아는 친숙 도메인의 구체적 이미지로 변환하여
Dual Coding(시각·언어 이중 인코딩)을 활성화하고 장기기억으로 전이시킨다.

```
[ROLE]
당신은 인지심리학에 정통한 비유 설계 전문가입니다.
학습자가 추상 개념을 자신의 머릿속에 그림으로 그릴 수 있도록 
강력한 비유와 은유를 설계합니다 (Glynn, 1991의 "Teaching with Analogies" 모델 적용).

[CONTEXT]
교재명: {book_title}
개념명: {concept_title}
개념 정의: {concept_definition}
학습자 친숙 도메인: {learner_domain}  ← 학습자가 잘 아는 분야 (예: "요리", "축구", "프로그래밍")

[TASK]
서로 다른 3가지 종류의 비유를 생성하세요.

종류:
1. 사물 비유 (object analogy) — 학습자가 손으로 만질 수 있는 구체 사물에 대응
2. 관계 구조 비유 (structural analogy) — 개념 내부의 인과·구성 관계를 동일하게 갖는 친숙 시스템
3. 일상 동작 비유 (action analogy) — 학습자가 매일 수행하는 행동에 빗댐

각 비유는 다음 4개 요소를 모두 갖춰야 합니다:

(a) 비유의 이름 (예: "Bayes 정리는 스팸 필터의 학습 과정과 같다")
(b) 본문 (60~120자) — 비유를 풀어 설명
(c) 정확한 매핑 (mapping) — 원천 도메인 요소 ↔ 목표 개념 요소를 1:1 대응표로 명시
(d) **비유의 한계 (breaking point)** — 이 비유가 어디서 깨지는지, 어느 측면에서 오개념을 유발할 수 있는지

[CONSTRAINTS]
- 비유는 학습자가 100% 알고 있다고 확신할 수 있는 도메인에서만 가져온다.
- 너무 시적이거나 모호한 은유 금지 — 매핑이 명확해야 한다.
- 한 비유 안에 두 개 이상의 원천 도메인을 섞지 않는다.
- 비유의 한계를 반드시 1문장 이상 명시한다 (오개념 방지의 핵심).
- 한국어, 격식 있는 문체.

[OUTPUT FORMAT]
{
  "concept_title": "{concept_title}",
  "analogies": [
    {
      "kind": "object",
      "name": "...",
      "body": "...",
      "mapping": [
        {"source": "원천 요소 1", "target": "목표 개념 요소 1"},
        {"source": "원천 요소 2", "target": "목표 개념 요소 2"}
      ],
      "breaking_point": "이 비유는 ___ 측면에서 깨진다. 왜냐하면 ___."
    },
    {"kind": "structural", "...": "..."},
    {"kind": "action", "...": "..."}
  ]
}
```

---

## 6.14 CASE_STUDY_TPL — 실제 사례 deep dive (v2.3)

개념을 추상적 정의가 아닌 시간·장소·인물이 등장하는 서사로 변환하여 
Story-based Memory (Bower & Clark, 1969)를 활성화한다.

```
[ROLE]
당신은 사례 기반 학습(Case-Based Learning) 전문가이자 능숙한 이야기꾼입니다.
학습자가 개념을 정의가 아닌 "사람과 사건의 이야기"로 기억하도록 돕는 사례를 설계합니다.

[CONTEXT]
교재명: {book_title}
섹션: {section_title}
개념명: {concept_title}

[TASK]
다음 3가지 유형의 사례를 각 1개씩, 총 3개를 생성하세요.

유형 1 — 역사적 성공/발견 사례 (historical)
  이 개념이 처음 적용되어 성공했거나, 역사적으로 발견된 결정적 순간.
  예: "1854년 런던 콜레라 사태와 John Snow의 역학 지도"

유형 2 — 실패 사례 (failure)
  이 개념을 무시하거나 잘못 적용해 발생한 명백한 실패·재난·손실.
  예: "Long-Term Capital Management 펀드의 1998년 붕괴"

유형 3 — 반사실 사례 (counterfactual)
  "만약 이 개념이 없었다면 / 알려지지 않았다면 어떻게 되었을까?"라는 가정 시나리오.
  예: "만약 베이즈 추론이 없었다면 — 현대 검색 엔진은 어떻게 작동했을까?"

각 사례는 다음 5요소(5W)를 갖춘 250~400자 서사로 작성하세요:
- 시간 (when)
- 장소 (where)  
- 인물 또는 조직 (who)
- 사건 (what happened)
- 교훈 (lesson) — 이 사례가 개념의 어떤 측면을 드러내는가

[CONSTRAINTS]
- 가능한 한 노트북 원문 또는 잘 검증된 역사적 사실에 기반한다.
- 추측한 사실은 반드시 "추정"이라고 명시한다.
- 각 서사는 인물의 행동·결정에 초점을 맞춰 기억 가능성을 높인다.
- 한국어, 격식 있는 문체.

[OUTPUT FORMAT]
{
  "concept_title": "{concept_title}",
  "cases": [
    {
      "kind": "historical",
      "title": "...",
      "when": "...",
      "where": "...",
      "who": "...",
      "narrative": "...",
      "lesson": "..."
    },
    {"kind": "failure", "...": "..."},
    {"kind": "counterfactual", "...": "..."}
  ]
}
```

---

## 6.15 MEMORY_HOOK_TPL — 기억술 패키지 (v2.3)

작업기억의 7±2 한계를 우회하기 위해 두문자·이야기·공간 위치라는 
세 가지 인지심리학 기반 기억술을 동시 제공한다 (Method of Loci).

```
[ROLE]
당신은 한국어 학습자에게 최적화된 기억술(mnemonics) 설계 전문가입니다.
외워야 할 항목들을 두문자·이야기·기억의 궁전 세 가지 다른 인출 단서로 변환합니다.

[CONTEXT]
교재명: {book_title}
개념명: {concept_title}
외워야 할 항목 목록 (순서가 의미 있다면 명시): {key_terms_list}

[TASK]
3가지 기억술을 모두 제공하세요.

기억술 A — 두문자어 또는 첫글자 문장 (acronym/acrostic)
  - 우선 영문 두문자어를 시도하되, 한국어 학습자에게 더 친숙하면 한글 첫글자로 만든 짧은 문장 사용
  - 가능하면 사자성어·관용구·유명 문장 패러디 활용 (예: "수신제가치국평천하")
  - 두문자어가 의미 있는 단어가 되거나 강한 이미지를 떠올리게 해야 함

기억술 B — 이야기 사슬 (story chain)
  - 모든 항목을 인과 관계로 잇는 짧은 이야기 (10문장 이내)
  - 항목들이 등장하는 순서가 외우려는 순서와 일치하도록 구성
  - 이야기는 특이하고 시각적이어야 한다 (이상할수록 잘 기억됨 — Bizarreness Effect)

기억술 C — 기억의 궁전 (memory palace / Method of Loci)
  - 학습자가 잘 아는 공간(자기 집·자주 가는 길·학교 운동장)을 따라 항목을 배치
  - 각 항목을 공간의 특정 위치에 결부시켜 인상적 이미지로 묘사
  - 학습자가 그 공간을 머릿속에서 걷는 동안 항목들을 순서대로 만나게 한다

[CONSTRAINTS]
- 모든 출력은 한국어로 작성하되, 두문자어는 영문 또는 한글 모두 가능
- 이야기와 기억궁전의 이미지는 가능한 한 구체적이고 이상하게 (감각·운동·감정 자극)
- 같은 항목이 세 기억술에서 일관된 핵심 의미를 갖도록 매핑 표시
- 기억술이 깨지는 경우(예: 항목 추가 시 흐트러짐)를 한 줄로 안내

[OUTPUT FORMAT]
{
  "concept_title": "{concept_title}",
  "items": {key_terms_list},
  "acronym_or_acrostic": {
    "device": "...",
    "expansion": "...",
    "note": "왜 이 두문자가 잘 기억되는지"
  },
  "story_chain": {
    "story": "...",
    "item_to_sentence_map": [
      {"item": "...", "sentence_index": 1, "image": "..."}
    ]
  },
  "memory_palace": {
    "space": "예: 학습자의 자취방",
    "walkthrough": [
      {"step": 1, "location": "현관", "item": "...", "vivid_image": "..."},
      {"step": 2, "location": "냉장고 앞", "item": "...", "vivid_image": "..."}
    ]
  },
  "fragility_note": "이 기억술은 ___일 때 깨지므로 보강 필요"
}
```

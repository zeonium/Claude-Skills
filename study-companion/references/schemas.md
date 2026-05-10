# 데이터 스키마 명세

## learner.json

```json
{
  "user_id": "default_user",
  "name": null,
  "daily_minutes": 45,
  "preferred_language": "ko",
  "prior_level": "intermediate",
  "global_ability_theta": 0.0,
  "book_abilities": {
    "notebook-id-123": 0.7,
    "notebook-id-123_start": -0.2
  },
  "note_root": "D:\\Obsi\\Obsi_Sapi",
  "obsidian_compatible": true,
  "created_at": "2026-05-06T00:00:00+00:00",
  "updated_at": "2026-05-06T09:30:00+00:00"
}
```

## books/{notebook_id}/metadata.json

```json
{
  "notebook_id": "abc123def",
  "title": "확률론 기초",
  "source_count": 3,
  "estimated_difficulty": "intermediate",
  "estimated_total_hours": 40.0,
  "created_at": "2026-05-06T00:00:00+00:00",
  "last_studied_at": "2026-05-06T09:00:00+00:00",
  "chapters": [
    {
      "chapter_id": "ch-a1b2c3d4",
      "title": "1장. 표본공간과 사건",
      "section_ids": ["sec-x1y2z3w4", "sec-a2b3c4d5"],
      "estimated_minutes": 90,
      "text_word_count": 3000,
      "concept_count": 8,
      "example_count": 5,
      "exercise_count": 10,
      "bloom_objectives": [
        {"level": "Remember", "statement": "표본공간을 정의할 수 있다"},
        {"level": "Understand", "statement": "사건의 집합 연산을 설명할 수 있다"}
      ],
      "key_concepts": ["con-11223344", "con-55667788"]
    }
  ]
}
```

## books/{notebook_id}/syllabus.json

```json
{
  "notebook_id": "abc123def",
  "total_weeks": 6,
  "daily_minutes": 45,
  "version": 1,
  "generated_at": "2026-05-06T00:00:00+00:00",
  "weeks": [
    {
      "week_number": 1,
      "theme": "1장. 표본공간과 사건",
      "days": [
        {
          "day_number": 1,
          "section_ids": ["sec-x1y2z3w4"],
          "materials": ["summary", "mindmap", "flashcards"],
          "estimated_minutes": 45,
          "is_review_day": false
        }
      ]
    }
  ],
  "milestones": [
    {
      "milestone_id": "ms-week1",
      "title": "Week 1 Mastery",
      "after_week": 1,
      "assessment_n_items": 15
    }
  ]
}
```

## books/{notebook_id}/sessions/{YYYY-MM-DD}.json

```json
{
  "session_id": "sess-a1b2c3d4",
  "notebook_id": "abc123def",
  "date": "2026-05-06",
  "planned_section_ids": ["sec-x1y2z3w4"],
  "completed_section_ids": ["sec-x1y2z3w4"],
  "materials_viewed": {
    "sec-x1y2z3w4": ["summary", "flashcards"]
  },
  "assessment_results": [
    {
      "item_id": "q1",
      "concept_ids": ["con-11223344"],
      "correct": true,
      "response_time_sec": 12.5,
      "bloom_level": "Remember"
    }
  ],
  "reflection_journal_path": "D:\\Obsi\\Obsi_Sapi\\06_Reflections\\2026-05\\2026-05-06-reflection.md",
  "time_spent_minutes": 42,
  "mcp_calls": [
    {
      "tool": "notebooklm__notebook_query",
      "args": {"notebook_id": "abc123def", "type": "summary", "level": 2},
      "called_at": "2026-05-06T09:05:00+00:00",
      "success": true,
      "error": null
    }
  ]
}
```

## srs/deck.json

```json
[
  {
    "card_id": "card-a1b2c3d4",
    "notebook_id": "abc123def",
    "concept_id": "con-11223344",
    "front": "표본공간(Ω)이란 무엇인가?",
    "back": "어떤 실험에서 나올 수 있는 모든 결과의 집합",
    "stability": 4.0,
    "difficulty": 3.5,
    "last_review": "2026-05-06T09:30:00+00:00",
    "due_date": "2026-05-10T09:30:00+00:00",
    "review_count": 2,
    "lapse_count": 0
  }
]
```

## Obsidian 노트 YAML Frontmatter 스키마

### 세션 노트 (type: study-session)

```yaml
---
type: "study-session"
date: "2026-05-06"
book: "확률론 기초"
notebook_id: "abc123def"
section_ids:
  - "sec-x1y2z3w4"
duration_min: "42"
tags:
  - "study-companion"
  - "book/확률론_기초"
---
```

### 플래시카드 (type: flashcard)

```yaml
---
type: "flashcard"
card_id: "card-a1b2c3d4"
concept: "표본공간"
tags:
  - "study-companion"
  - "flashcard"
---
표본공간(Ω)이란 무엇인가?

?

어떤 실험에서 나올 수 있는 모든 결과의 집합

<!--SR:!2026-05-10,2,400-->
```

### 개념 노트 (type: concept)

```yaml
---
type: "concept"
concept_id: "con-11223344"
title: "표본공간"
tags:
  - "study-companion"
  - "concept"
---
```

### 대시보드 (type: dashboard)

```yaml
---
type: "dashboard"
updated: "2026-05-06"
tags:
  - "study-companion"
  - "dashboard"
---
```

### Reflection 노트 (type: reflection) — 스크린샷 기준

저장 경로: `Reflections/{book-title}/{YYYY-MM}/Session{NN}_Reflection.md`

```yaml
---
type: reflection
session: 1
chapter: Introduction
date: 2026-05-08
score: 80
tags:
  - reflection
  - session-log
---
```

본문 구조:
```markdown
# Session {N} 메타인지 일지 — {chapter_title}

날짜: {YYYY-MM-DD}
형성평가 점수: {n_correct}/{n_items} ({score_pct}%)

---

## R1. 오늘 가장 인상 깊었던 것

> "{learner_answer_r1}"

→ {claude_comment}

---

## R2. {핵심개념명} 자신감

{self_rating} / 5 {star_emoji}

---

## R3. 다음 세션 사전 질문

> "{learner_question}"

→ {claude_preview}

---

## ⚠ 보완 포인트 (다음 복습 시)

- {weak_concept_1}: {brief_description}
- {weak_concept_2}: {brief_description}
```

### 챕터 퀴즈 결과 노트 (type: chapter-quiz)

저장 경로: `Reflections/{book-title}/{YYYY-MM}/Session{NN}_ChapterQuiz.md`

```yaml
---
type: chapter-quiz
chapter: Introduction
chapter_id: Ch00
date: 2026-05-08
score: 80
n_correct: 8
n_items: 10
tags:
  - chapter-quiz
  - assessment
---
```

### 시험 대비 문제집 노트 (type: exam-prep)

저장 경로: `Concepts/{book-title}/Exam_{범위}_문제집.md`

```yaml
---
type: exam-prep
exam_type: 중간고사
scope: Ch00-Ch05
generated_date: 2026-05-08
total_items: 30
tags:
  - exam-prep
  - assessment
---
```

## learner.json — 플랫폼 필드 추가

```json
{
  "user_id": "default_user",
  "name": null,
  "daily_minutes": 45,
  "preferred_language": "ko",
  "prior_level": "intermediate",
  "global_ability_theta": 0.0,
  "platform": "windows",
  "note_root": null,
  "obsidian_compatible": true,
  "created_at": "2026-05-06T00:00:00+00:00",
  "updated_at": "2026-05-06T09:30:00+00:00"
}
```

`platform` 값: `"windows"` 또는 `"darwin"` (macOS).  
`note_root`는 `null`이면 `scripts/utils.get_data_root()`가 OS에 따라 자동 결정한다.

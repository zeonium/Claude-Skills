---
type: "study-session"
date: "{{date}}"
book: "{{book_title}}"
notebook_id: "{{notebook_id}}"
chapter: "{{chapter_title}}"
section_ids:
  - "{{section_id}}"
bloom_levels:
  - "Remember"
  - "Understand"
tags:
  - "study-companion"
  - "book/{{book_slug}}"
  - "ch/{{chapter_id}}"
duration_min: "{{duration_min}}"
ability_theta: "{{ability_theta}}"
weakness_count: "{{weakness_count}}"
---

# {{date}} 학습 세션

## 📋 오늘의 학습 요약

- **교재**: {{book_title}}
- **챕터**: {{chapter_title}}
- **섹션**: {{section_title}}
- **학습 시간**: {{duration_min}}분
- **완료 자료**: {{completed_materials}}

## 🔥 Activate — 회상 점화

{{activate_content}}

## 📖 Acquire — 핵심 내용

### 요약 (L1)

{{summary_l1}}

### 핵심 개념

{{key_concepts}}

## ✏️ Apply — 형성평가 결과

- 점수: {{score_pct}}% ({{n_correct}}/{{n_items}})
- 약점 개념: {{weak_concepts}}

## 🪞 Reflect — 메타인지 일지

{{reflection_qa}}

---

*Study Companion 스킬이 자동 생성함 — [[_index|대시보드로 돌아가기]]*

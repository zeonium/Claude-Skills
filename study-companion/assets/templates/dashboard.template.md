---
type: "dashboard"
updated: "{{updated_date}}"
tags:
  - "study-companion"
  - "dashboard"
---

# 📊 Study Companion 대시보드

*마지막 업데이트: {{updated_date}}*

## 현재 학습: {{book_title}}

### 진도

- 전체: {{progress_bar}} **{{progress_pct}}%** (Day {{completed_days}}/{{total_days}})
- 누적 학습 시간: {{total_hours}}시간

### 능력 추정 (θ)

- 시작: {{theta_start}} → 현재: {{theta_current}} ({{theta_delta}})

### 마일스톤

{{milestone_list}}

### 약점 클리닉 (상위 3)

{{weakness_list}}

### SRS 카드 현황

- 신규: {{srs_new}}장 / 학습중: {{srs_learning}}장 / 성숙: {{srs_mature}}장
- 오늘 복습 예정: {{srs_due_today}}장

---

## 빠른 링크

- [[02_Sessions/{{year}}/{{year_month}}|이번 달 세션]]
- [[03_Milestones|마일스톤 보고서]]
- [[04_Concepts|개념 노트]]
- [[05_Flashcards|플래시카드]]
- [[06_Reflections|메타인지 일지]]

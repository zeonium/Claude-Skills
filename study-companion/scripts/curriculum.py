"""
Phase 2: 시러버스(커리큘럼) 생성 및 재계획.
NotebookLM describe → 챕터 추출 → topological sort → 일정 빌드.
"""

from __future__ import annotations

import math
from typing import Literal

from scripts.models import (
    BloomObjective, Chapter, Day, DimensionType,
    LearnerProfile, Milestone, Section, Syllabus, Week, _new_id
)


# ──────────────────────────────────────────────────────────────
# 챕터 시간 추정
# ──────────────────────────────────────────────────────────────

def estimate_chapter_minutes(chapter: Chapter, prior_level: str) -> int:
    """
    휴리스틱 시간 추정:
      - 1분/200단어
      - 개념당 3분
      - 예제당 2분
      - 연습문제당 5분
    사전지식 가중: beginner×1.5 / intermediate×1.0 / advanced×0.6
    """
    base = (
        chapter.text_word_count / 200 * 1.0
        + chapter.concept_count * 3
        + chapter.example_count * 2
        + chapter.exercise_count * 5
    )
    if base < 30:
        base = 30  # 최소 30분

    multiplier = {"beginner": 1.5, "intermediate": 1.0, "advanced": 0.6}[prior_level]
    return int(base * multiplier)


# ──────────────────────────────────────────────────────────────
# 의존관계 추론 (간이 휴리스틱)
# ──────────────────────────────────────────────────────────────

def infer_prerequisites(chapters: list[Chapter]) -> list[Chapter]:
    """
    간단한 휴리스틱: 인덱스 순서 기반.
    챕터 i는 챕터 i-1을 전제로 한다 (선형 구조 가정).
    향후 개념 그래프 기반으로 교체 가능.
    """
    for i, ch in enumerate(chapters):
        if i > 0 and not ch.bloom_objectives:
            ch.bloom_objectives = [
                BloomObjective(level="Remember", statement=f"{ch.title}의 핵심 용어를 정의할 수 있다"),
                BloomObjective(level="Understand", statement=f"{ch.title}의 원리를 설명할 수 있다"),
            ]
    return chapters


def topological_sort(chapters: list[Chapter]) -> list[Chapter]:
    """현재는 입력 순서 그대로 반환 (선형 교재 가정). 비선형 구조 시 교체."""
    return list(chapters)


# ──────────────────────────────────────────────────────────────
# 일별 자료 규칙
# ──────────────────────────────────────────────────────────────

def day_materials(day_in_chapter: int, is_review_day: bool) -> list[DimensionType]:
    """
    Day 1 (신규): summary + mindmap + flashcards
    Day 2 (심화): examples + socratic + application
    Day 3 (점검): assessment + reflection + crossref
    Day 7 (주간 복습): review (SRS 큐)
    그 외: summary + assessment
    """
    if is_review_day:
        return ["reflection"]
    mapping = {
        1: ["summary", "mindmap", "flashcards"],
        2: ["examples", "socratic", "application"],
        3: ["assessment", "reflection", "crossref"],
    }
    return mapping.get(day_in_chapter, ["summary", "assessment"])


# ──────────────────────────────────────────────────────────────
# 시러버스 빌드
# ──────────────────────────────────────────────────────────────

def build_syllabus(
    notebook_id: str,
    chapters: list[Chapter],
    learner: LearnerProfile,
    target_days: int | None = None,
) -> Syllabus:
    """
    1. chapters topological sort
    2. 챕터를 daily_minutes 기반으로 일자에 분배 (최소 1일, 최대 5일)
    3. 7일마다 복습일 삽입
    4. 주차별 마일스톤 자동 생성
    5. buffer day 10% 추가
    """
    sorted_chs = topological_sort(chapters)
    daily = learner.daily_minutes

    all_days: list[Day] = []
    day_counter = 1
    in_chapter_day = 0

    for ch in sorted_chs:
        ch_minutes = estimate_chapter_minutes(ch, learner.prior_level)
        ch_days = max(1, min(5, math.ceil(ch_minutes / daily)))
        per_day_sections = _split_sections(ch.section_ids, ch_days)

        for i in range(ch_days):
            # 7의 배수 날짜는 복습일
            if day_counter % 7 == 0:
                all_days.append(Day(
                    day_number=day_counter,
                    section_ids=[],
                    materials=["reflection"],
                    estimated_minutes=daily,
                    is_review_day=True,
                ))
                day_counter += 1

            in_chapter_day = (in_chapter_day % 3) + 1
            materials = day_materials(in_chapter_day, False)
            all_days.append(Day(
                day_number=day_counter,
                section_ids=per_day_sections[i],
                materials=materials,
                estimated_minutes=daily,
                is_review_day=False,
            ))
            day_counter += 1

    # buffer 10%
    buffer_days = max(1, int(len(all_days) * 0.1))
    for _ in range(buffer_days):
        all_days.append(Day(
            day_number=day_counter,
            section_ids=[],
            materials=["reflection"],
            estimated_minutes=daily,
            is_review_day=True,
        ))
        day_counter += 1

    # 주차 구성
    total_days = len(all_days)
    total_weeks = math.ceil(total_days / 7)
    weeks = []
    milestones = []

    for w in range(total_weeks):
        week_days = all_days[w * 7:(w + 1) * 7]
        theme = sorted_chs[min(w, len(sorted_chs) - 1)].title if sorted_chs else f"주제 {w+1}"
        weeks.append(Week(week_number=w + 1, theme=theme, days=week_days))
        milestones.append(Milestone(
            milestone_id=f"ms-week{w+1}",
            title=f"Week {w+1} Mastery",
            after_week=w + 1,
            assessment_n_items=15 if w < total_weeks - 1 else 30,
        ))

    return Syllabus(
        notebook_id=notebook_id,
        total_weeks=total_weeks,
        daily_minutes=daily,
        weeks=weeks,
        milestones=milestones,
    )


def _split_sections(section_ids: list[str], n_days: int) -> list[list[str]]:
    if not section_ids:
        return [[] for _ in range(n_days)]
    chunk = max(1, math.ceil(len(section_ids) / n_days))
    return [section_ids[i:i+chunk] for i in range(0, len(section_ids), chunk)]


# ──────────────────────────────────────────────────────────────
# 시러버스 승인 게이트 출력
# ──────────────────────────────────────────────────────────────

def format_syllabus_proposal(syllabus: Syllabus, chapters: list[Chapter]) -> str:
    lines = [
        "## 📅 학습 계획 초안\n",
        f"- 총 기간: {syllabus.total_weeks}주",
        f"- 일일 학습: {syllabus.daily_minutes}분",
        f"- 총 챕터: {len(chapters)}개",
        "",
        "### 주차별 개요",
        "| 주차 | 주제 | 마일스톤 |",
        "|------|------|---------|",
    ]
    for week in syllabus.weeks:
        ms = next((m.title for m in syllabus.milestones if m.after_week == week.week_number), "-")
        lines.append(f"| {week.week_number}주차 | {week.theme} | {ms} |")

    lines += [
        "",
        "### 사용자 액션",
        "- ✅ 이대로 시작 → **\"시작합니다\"**",
        "- ⚙️ 조정 필요 → **\"더 천천히\"** / **\"더 빠르게\"** / **\"특정 챕터 강조\"**",
        "- ❌ 다시 → **\"다시 짜줘\"**",
    ]
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# 재계획 (RECONFIG 의도)
# ──────────────────────────────────────────────────────────────

def replan_syllabus(
    existing: Syllabus,
    chapters: list[Chapter],
    learner: LearnerProfile,
    adjustment: Literal["slower", "faster", "reset"],
) -> Syllabus:
    """
    slower: daily_minutes × 0.7 (하루 분량 줄임)
    faster: daily_minutes × 1.3 (하루 분량 늘림)
    reset: 처음부터 재생성
    """
    if adjustment == "slower":
        learner.daily_minutes = max(15, int(learner.daily_minutes * 0.7))
    elif adjustment == "faster":
        learner.daily_minutes = min(120, int(learner.daily_minutes * 1.3))

    new_syllabus = build_syllabus(existing.notebook_id, chapters, learner)
    new_syllabus.version = existing.version + 1
    return new_syllabus

"""
Phase 3: 일일 학습 세션 — 4-stage 루프 (Activate → Acquire → Apply → Reflect).
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from scripts.models import (
    BookMetadata, Day, LearnerProfile, LearningSession, Syllabus
)
from scripts.storage import LocalStorage
from scripts.utils import today_str


def get_today_plan(syllabus: Syllabus, start_date: date, today: date) -> Day | None:
    """
    start_date 기준으로 오늘이 몇 번째 Day인지 계산하여 Day 객체 반환.
    완료된 날(세션 기록 있음)은 건너뜀.
    """
    delta = (today - start_date).days
    all_days = [day for week in syllabus.weeks for day in week.days]
    if delta < len(all_days):
        return all_days[delta]
    return None


def get_week_for_day(syllabus: Syllabus, day: Day) -> int | None:
    """주어진 Day가 속한 주차 번호 반환."""
    for week in syllabus.weeks:
        if any(d.day_number == day.day_number for d in week.days):
            return week.week_number
    return None


# ──────────────────────────────────────────────────────────────
# 세션 진입 메시지
# ──────────────────────────────────────────────────────────────

def format_session_open(
    day: Day,
    book: BookMetadata,
    prev_concept: str | None,
    day_number: int,
    total_days: int,
    progress_pct: float,
) -> str:
    import calendar
    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"]
    today = date.today()
    weekday = weekday_kr[today.weekday()]

    lines = [
        f"## 📚 {weekday}요일, {today.isoformat()} 학습 세션\n",
        f"**오늘의 교재**: {book.title}",
        f"**예상 시간**: {day.estimated_minutes}분",
        f"**상태**: ⏱️ Day {day_number}/{total_days}, {progress_pct:.0f}% 완료",
        "",
    ]

    if day.is_review_day:
        lines += [
            "### 🔄 오늘은 복습의 날입니다\n",
            "SRS 카드 복습과 약점 개념 클리닉을 진행합니다.",
        ]
    else:
        lines += ["### 🔥 Activate (회상 점화)\n"]
        if prev_concept:
            lines.append(
                f"어제 배운 **{prev_concept}**, 핵심을 한 문장으로 말씀해 주시겠습니까?"
            )
        else:
            lines.append("새로운 학습을 시작합니다. 준비가 되셨으면 **\"준비됐어\"** 라고 말씀해 주세요.")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# 4-stage 루프 가이드 (Claude 런타임 실행 흐름)
# ──────────────────────────────────────────────────────────────

STAGE_GUIDE = {
    "activate": (
        "회상 점화 (2~3분): 어제 핵심 개념 1~2개를 회상 질문으로 시작.\n"
        "사용자 답변에서 약점 후보를 기록한다."
    ),
    "acquire": (
        "신규 학습 자료 노출 (30~38분): Day.materials에 정의된 차원 순서대로 제시.\n"
        "v2.3 — 핵심 개념 첫 노출 시 반드시 content_generator.deep_encoding() 호출:\n"
        "  → 비유(analogy) + 실제 사례(case_study) + 기억 훅(memory_hook) 동시 출력.\n"
        "  → 학습자가 '빠른 모드' / '간단히' / '요약만' 발화 시 deep_encoding_enabled=False로 토글.\n"
        "한 차원 종료 시 이해 확인 게이트:\n"
        "  → '이해되셨습니까? (예 / 추가설명 / 넘어가기)'\n"
        "  → '추가설명' 선택 시 다른 형태로 재생성 (예: summary L2 → L3 + mindmap + analogy)."
    ),
    "apply": (
        "문제 풀이 (10분): assessment.run_formative() 호출.\n"
        "5문항, 한 문항씩 제시 → 응답 → 즉각 피드백.\n"
        "정답은 사용자가 답한 후에만 공개한다 (Active Recall 보호)."
    ),
    "reflect": (
        "메타인지 일지 (5분): content_generator._reflection()으로 질문 3개 생성.\n"
        "사용자 답변을 수집하여 note_persistence.write_reflection()으로 Obsidian에 저장."
    ),
}


def format_stage_header(stage: str) -> str:
    icons = {
        "activate": "🔥",
        "acquire": "📖",
        "apply": "✏️",
        "reflect": "🪞",
    }
    titles = {
        "activate": "Activate — 회상 점화",
        "acquire": "Acquire — 신규 학습",
        "apply": "Apply — 문제 풀이",
        "reflect": "Reflect — 메타인지 일지",
    }
    return f"### {icons.get(stage, '')} {titles.get(stage, stage)}\n"


def format_understanding_gate(section_title: str) -> str:
    return (
        f"\n---\n"
        f"**{section_title}** 학습이 완료되었습니다.\n\n"
        f"이해되셨습니까?\n"
        f"- **예** → 다음으로 진행합니다\n"
        f"- **추가설명** → 다른 형태로 재설명합니다\n"
        f"- **넘어가기** → 이 부분을 건너뜁니다"
    )


def format_session_close(session: LearningSession, note_path: str | None) -> str:
    completed = len(session.completed_section_ids)
    planned = len(session.planned_section_ids)
    return (
        f"## ✅ 오늘 학습 완료!\n\n"
        f"- 완료 섹션: {completed}/{planned}개\n"
        f"- 학습 시간: {session.time_spent_minutes}분\n"
        + (f"- 학습 노트: `{note_path}`\n" if note_path else "")
        + f"\n내일 또 만나요! 꾸준함이 실력입니다. 💪"
    )

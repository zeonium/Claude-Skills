"""
진도 추적 + 대시보드 생성.
"""

from __future__ import annotations

from datetime import date

from scripts.models import (
    BookMetadata, LearnerProfile, ProgressSnapshot, Syllabus, Weakness
)
from scripts.storage import LocalStorage


def build_snapshot(
    book: BookMetadata,
    syllabus: Syllabus,
    learner: LearnerProfile,
    storage: LocalStorage,
    start_date: date,
) -> ProgressSnapshot:
    """현재 진도 스냅샷 생성."""
    all_days = [d for w in syllabus.weeks for d in w.days]
    total_days = len(all_days)
    today = date.today()
    delta = (today - start_date).days
    completed_days = min(delta, total_days)

    sessions = storage.list_sessions(book.notebook_id)
    total_minutes = sum(s.time_spent_minutes for s in sessions)
    total_hours = round(total_minutes / 60, 1)

    deck = storage.load_deck()
    book_cards = [c for c in deck if c.notebook_id == book.notebook_id]
    srs_new = sum(1 for c in book_cards if c.review_count == 0)
    srs_learning = sum(1 for c in book_cards if 0 < c.review_count <= 3)
    srs_mature = sum(1 for c in book_cards if c.review_count > 3)
    srs_due = len(storage.get_due_cards(book.notebook_id, today))

    achieved = [m.title for m in syllabus.milestones if m.after_week <= completed_days // 7]
    pending = [m.title for m in syllabus.milestones if m.after_week > completed_days // 7]

    theta_start = learner.book_abilities.get(f"{book.notebook_id}_start", learner.global_ability_theta)
    theta_now = learner.book_abilities.get(book.notebook_id, learner.global_ability_theta)

    return ProgressSnapshot(
        notebook_id=book.notebook_id,
        book_title=book.title,
        total_days=total_days,
        completed_days=completed_days,
        total_hours_spent=total_hours,
        ability_theta=theta_now,
        ability_start=theta_start,
        milestones_achieved=achieved,
        milestones_pending=pending[:3],
        srs_new=srs_new,
        srs_learning=srs_learning,
        srs_mature=srs_mature,
        srs_due_today=srs_due,
    )


def format_dashboard(snapshot: ProgressSnapshot) -> str:
    """텍스트 대시보드 마크다운 포맷."""
    completed = snapshot.completed_days
    total = snapshot.total_days
    bar_filled = int(completed / max(total, 1) * 16)
    bar = "█" * bar_filled + "░" * (16 - bar_filled)
    pct = int(completed / max(total, 1) * 100)

    week_completed = int(completed / 7)
    week_progress = (completed % 7) / 7 * 100
    week_bar_filled = int(week_progress / 100 * 10)
    week_bar = "█" * week_bar_filled + "░" * (10 - week_bar_filled)

    theta_delta = snapshot.ability_theta - snapshot.ability_start
    delta_str = f"▲ {theta_delta:+.1f}σ" if theta_delta >= 0 else f"▼ {theta_delta:.1f}σ"

    ms_lines = (
        "\n".join(f"- ✅ {m}" for m in snapshot.milestones_achieved) +
        "\n" +
        "\n".join(f"- ⏳ {m}" for m in snapshot.milestones_pending)
    ).strip()

    weak_lines = "\n".join(
        f"{i+1}. **{w.concept_id}** — {w.evidence[:60]}"
        for i, w in enumerate(snapshot.top_weaknesses[:3])
    ) or "현재 식별된 약점 없음"

    return (
        f"## 📊 학습 대시보드 — {snapshot.book_title}\n\n"
        f"### 진도\n"
        f"- 전체: {bar} **{pct}%** (Day {completed}/{total})\n"
        f"- 이번 주: {week_bar} {week_progress:.0f}%\n"
        f"- 누적 학습 시간: {snapshot.total_hours_spent:.1f}시간\n\n"
        f"### 능력 추정 (θ)\n"
        f"- 시작: {snapshot.ability_start:+.1f} → 현재: {snapshot.ability_theta:+.1f} ({delta_str})\n\n"
        f"### 마일스톤\n{ms_lines}\n\n"
        f"### 약점 클리닉 (상위 3)\n{weak_lines}\n\n"
        f"### SRS 카드 현황\n"
        f"- 신규: {snapshot.srs_new}장 / 학습중: {snapshot.srs_learning}장 / 성숙: {snapshot.srs_mature}장\n"
        f"- 오늘 복습 예정: {snapshot.srs_due_today}장\n"
    )

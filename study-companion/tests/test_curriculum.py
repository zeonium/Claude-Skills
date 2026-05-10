"""curriculum.py 단위 테스트."""

import pytest
from datetime import datetime, timezone

from scripts.curriculum import (
    build_syllabus, estimate_chapter_minutes, format_syllabus_proposal,
    replan_syllabus, topological_sort
)
from scripts.models import BloomObjective, Chapter, LearnerProfile, _now


def _make_learner(level: str = "intermediate", daily: int = 45) -> LearnerProfile:
    return LearnerProfile(
        prior_level=level,
        daily_minutes=daily,
        created_at=_now(),
        updated_at=_now(),
    )


def _make_chapter(title: str, words: int = 1000, concepts: int = 5) -> Chapter:
    return Chapter(
        title=title,
        chapter_id=f"ch-{title[:4]}",
        text_word_count=words,
        concept_count=concepts,
        example_count=3,
        exercise_count=5,
    )


class TestEstimateChapterMinutes:
    def test_beginner_longer(self):
        ch = _make_chapter("테스트")
        beginner = estimate_chapter_minutes(ch, "beginner")
        advanced = estimate_chapter_minutes(ch, "advanced")
        assert beginner > advanced

    def test_minimum_30min(self):
        ch = Chapter(title="초소형 챕터", chapter_id="ch-tiny", text_word_count=0,
                     concept_count=0, example_count=0, exercise_count=0)
        minutes = estimate_chapter_minutes(ch, "intermediate")
        assert minutes >= 30

    def test_intermediate_multiplier(self):
        ch = _make_chapter("기준 챕터", words=2000, concepts=10)
        minutes = estimate_chapter_minutes(ch, "intermediate")
        expected_base = 2000 / 200 + 10 * 3 + 3 * 2 + 5 * 5  # 10+30+6+25=71
        assert abs(minutes - int(expected_base)) <= 5


class TestBuildSyllabus:
    def test_basic_syllabus(self):
        learner = _make_learner()
        chapters = [_make_chapter(f"챕터{i}") for i in range(1, 4)]
        syllabus = build_syllabus("test-nb", chapters, learner)

        assert syllabus.notebook_id == "test-nb"
        assert syllabus.total_weeks >= 1
        assert len(syllabus.milestones) == syllabus.total_weeks
        assert syllabus.version == 1

    def test_all_days_have_materials(self):
        learner = _make_learner()
        chapters = [_make_chapter("챕터1")]
        syllabus = build_syllabus("test-nb", chapters, learner)
        all_days = [d for w in syllabus.weeks for d in w.days]
        for day in all_days:
            assert len(day.materials) >= 1

    def test_review_day_inserted(self):
        learner = _make_learner(daily=45)
        chapters = [_make_chapter(f"챕터{i}", words=3000, concepts=10) for i in range(3)]
        syllabus = build_syllabus("test-nb", chapters, learner)
        all_days = [d for w in syllabus.weeks for d in w.days]
        review_days = [d for d in all_days if d.is_review_day]
        assert len(review_days) >= 1

    def test_empty_chapters(self):
        # 챕터 없어도 buffer day(10%)가 최소 1일 추가되어 Syllabus 반환됨
        learner = _make_learner()
        syllabus = build_syllabus("test-nb", [], learner)
        assert syllabus.notebook_id == "test-nb"
        # buffer day 1개 → 1주 생성 (정상 동작)
        all_days = [d for w in syllabus.weeks for d in w.days]
        assert all(d.is_review_day for d in all_days)  # 모두 복습일

    def test_replan_slower(self):
        learner = _make_learner(daily=45)
        chapters = [_make_chapter("챕터1")]
        original = build_syllabus("test-nb", chapters, learner)
        replanned = replan_syllabus(original, chapters, learner, "slower")
        assert replanned.version == 2
        assert replanned.daily_minutes <= 45

    def test_format_proposal_contains_week(self):
        learner = _make_learner()
        chapters = [_make_chapter("확률론")]
        syllabus = build_syllabus("test-nb", chapters, learner)
        proposal = format_syllabus_proposal(syllabus, chapters)
        assert "주차" in proposal
        assert "시작합니다" in proposal

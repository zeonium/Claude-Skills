"""models.py 단위 테스트."""

import pytest
from datetime import datetime, timezone

from scripts.models import (
    BloomObjective, BookMetadata, Chapter, Day,
    LearnerProfile, Milestone, Section, SRSCard, Syllabus, Week,
    _new_id, _now
)


class TestLearnerProfile:
    def test_defaults(self):
        p = LearnerProfile(created_at=_now(), updated_at=_now())
        assert p.user_id == "default_user"
        assert p.daily_minutes == 45
        assert p.preferred_language == "ko"
        assert p.note_root == r"D:\Obsi\Obsi_Sapi"
        assert p.obsidian_compatible is True

    def test_prior_level_values(self):
        for level in ("beginner", "intermediate", "advanced"):
            p = LearnerProfile(prior_level=level, created_at=_now(), updated_at=_now())
            assert p.prior_level == level

    def test_theta_range(self):
        p = LearnerProfile(global_ability_theta=-1.5, created_at=_now(), updated_at=_now())
        assert p.global_ability_theta == -1.5

    def test_json_roundtrip(self):
        p = LearnerProfile(name="Peter", daily_minutes=60, created_at=_now(), updated_at=_now())
        json_str = p.model_dump_json(indent=2)
        restored = LearnerProfile.model_validate_json(json_str)
        assert restored.name == "Peter"
        assert restored.daily_minutes == 60


class TestChapterModel:
    def test_new_id_format(self):
        cid = _new_id("ch")
        assert cid.startswith("ch-")
        assert len(cid) == 11  # "ch-" + 8자

    def test_bloom_objective(self):
        obj = BloomObjective(level="Apply", statement="베이즈 정리를 적용할 수 있다")
        assert obj.level == "Apply"

    def test_chapter_defaults(self):
        ch = Chapter(title="테스트 챕터", chapter_id="ch-test0001")
        assert ch.estimated_minutes == 60
        assert ch.section_ids == []
        assert ch.key_concepts == []


class TestSyllabus:
    def test_syllabus_build(self):
        week = Week(
            week_number=1,
            theme="기초 확률",
            days=[
                Day(day_number=1, materials=["summary", "mindmap"], estimated_minutes=45),
                Day(day_number=2, materials=["examples", "assessment"], estimated_minutes=45),
            ]
        )
        ms = Milestone(milestone_id="ms-week1", title="Week 1 Mastery", after_week=1)
        syllabus = Syllabus(
            notebook_id="test-nb",
            total_weeks=1,
            daily_minutes=45,
            weeks=[week],
            milestones=[ms],
        )
        assert syllabus.total_weeks == 1
        assert len(syllabus.weeks[0].days) == 2
        assert syllabus.version == 1


class TestSRSCard:
    def test_srs_card_defaults(self):
        card = SRSCard(
            notebook_id="test-nb",
            concept_id="con-abc",
            front="표본공간이란?",
            back="모든 결과의 집합",
            due_date=_now(),
        )
        assert card.stability == 0.0
        assert card.difficulty == 5.0
        assert card.review_count == 0
        assert card.lapse_count == 0

    def test_card_id_generated(self):
        card = SRSCard(
            notebook_id="nb",
            concept_id="c",
            front="Q",
            back="A",
            due_date=_now(),
        )
        assert card.card_id.startswith("card-")

"""srs.py 단위 테스트."""

import pytest
from datetime import datetime, timedelta, timezone

from scripts.models import SRSCard, _now
from scripts.srs import FSRSLite, parse_rating


def _make_card(review_count: int = 0, stability: float = 4.0, difficulty: float = 5.0) -> SRSCard:
    return SRSCard(
        notebook_id="test-nb",
        concept_id="con-test",
        front="질문",
        back="답변",
        stability=stability,
        difficulty=difficulty,
        review_count=review_count,
        due_date=_now(),
    )


class TestFSRSLite:
    def setup_method(self):
        self.fsrs = FSRSLite()

    def test_first_review_good(self):
        card = _make_card(review_count=0)
        updated = self.fsrs.schedule(card, 3)  # Good
        assert updated.review_count == 1
        assert updated.stability > 0
        assert updated.due_date > _now()

    def test_again_reduces_stability(self):
        card = _make_card(review_count=3, stability=8.0)
        updated = self.fsrs.schedule(card, 1)  # Again
        assert updated.stability < 8.0
        assert updated.lapse_count == 1

    def test_easy_increases_stability(self):
        card = _make_card(review_count=2, stability=4.0)
        good_card = self.fsrs.schedule(_make_card(review_count=2, stability=4.0), 3)
        easy_card = self.fsrs.schedule(_make_card(review_count=2, stability=4.0), 4)
        assert easy_card.stability > good_card.stability

    def test_difficulty_bounds(self):
        card = _make_card(review_count=5, difficulty=1.5)
        # Again: difficulty += 1.0
        updated = self.fsrs.schedule(card, 1)
        assert 1.0 <= updated.difficulty <= 10.0

        card2 = _make_card(review_count=5, difficulty=9.5)
        # Easy: difficulty -= 1.0
        updated2 = self.fsrs.schedule(card2, 4)
        assert 1.0 <= updated2.difficulty <= 10.0

    def test_next_due_interval_minimum_1day(self):
        card = _make_card(review_count=1, stability=0.1)
        interval = self.fsrs.next_due_interval(card)
        assert interval >= timedelta(days=1)

    def test_retrievability_new_card(self):
        card = _make_card(review_count=0)
        r = self.fsrs.retrievability(card)
        assert r == 0.0  # 한 번도 복습 안 함

    def test_rating_sequence(self):
        card = _make_card(review_count=0)
        for rating in [3, 3, 4, 2, 1, 3]:
            card = self.fsrs.schedule(card, rating)
        assert card.review_count == 6


class TestParseRating:
    def test_good_variants(self):
        assert parse_rating("③") == 3
        assert parse_rating("3") == 3
        assert parse_rating("Good") == 3
        assert parse_rating("good") == 3

    def test_again_variants(self):
        assert parse_rating("①") == 1
        assert parse_rating("1") == 1
        assert parse_rating("Again") == 1

    def test_easy_variants(self):
        assert parse_rating("④") == 4
        assert parse_rating("Easy") == 4

    def test_hard_variants(self):
        assert parse_rating("②") == 2
        assert parse_rating("Hard") == 2

    def test_fallback_good(self):
        assert parse_rating("모르겠음") == 3

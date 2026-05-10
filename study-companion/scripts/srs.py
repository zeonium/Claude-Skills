"""
FSRS-Lite SRS 엔진.
추후 fsrs-py 라이브러리로 교체 가능하도록 인터페이스 분리.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from typing import Literal

from scripts.models import SRSCard


RatingType = Literal[1, 2, 3, 4]  # 1=Again, 2=Hard, 3=Good, 4=Easy


# ──────────────────────────────────────────────────────────────
# FSRS-Lite 알고리즘
# ──────────────────────────────────────────────────────────────

class FSRSLite:
    """
    FSRS(Free Spaced Repetition Scheduler) 간소화 버전.

    핵심 파라미터:
    - stability (S): 기억 안정성 (일 단위)
    - difficulty (D): 카드 난이도 (1~10)
    - retrievability (R): 현재 기억 확률 (0~1)

    인터벌 계산: I = S × ln(target_R) / ln(0.9)
    기본 target_R = 0.9 (90% 기억 확률 목표)
    """

    TARGET_R = 0.9
    STABILITY_INIT = {1: 0.5, 2: 1.0, 3: 2.0, 4: 4.0}  # 첫 복습별 초기 stability

    def schedule(self, card: SRSCard, rating: RatingType) -> SRSCard:
        """
        rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        카드 상태를 업데이트하고 다음 due_date를 설정하여 반환.
        """
        now = datetime.now(tz=timezone.utc)
        card.review_count += 1
        card.last_review = now

        if card.review_count == 1:
            # 신규 카드 첫 복습
            card.stability = self.STABILITY_INIT[rating]
            card.difficulty = self._init_difficulty(rating)
        else:
            card.stability = self._update_stability(card, rating)
            card.difficulty = self._update_difficulty(card, rating)

        if rating == 1:
            card.lapse_count += 1
            card.stability = max(0.5, card.stability * 0.5)

        interval = self.next_due_interval(card)
        card.due_date = now + interval
        return card

    def next_due_interval(self, card: SRSCard) -> timedelta:
        """다음 복습까지의 인터벌 (days)."""
        if card.stability <= 0:
            return timedelta(days=1)
        days = card.stability * math.log(self.TARGET_R) / math.log(0.9)
        days = max(1.0, days)
        return timedelta(days=round(days))

    def _init_difficulty(self, rating: RatingType) -> float:
        """첫 복습 난이도 초기값."""
        init = {1: 8.0, 2: 6.0, 3: 4.0, 4: 2.0}
        return init[rating]

    def _update_stability(self, card: SRSCard, rating: RatingType) -> float:
        """
        stability 업데이트:
        Again: 50% 감소
        Hard: 20% 감소
        Good: 20% 증가
        Easy: 50% 증가
        """
        delta = {1: -0.5, 2: -0.2, 3: 0.2, 4: 0.5}[rating]
        new_s = card.stability * (1 + delta)
        return max(0.5, round(new_s, 2))

    def _update_difficulty(self, card: SRSCard, rating: RatingType) -> float:
        """
        difficulty 업데이트:
        Again: +1, Hard: +0.5, Good: -0.5, Easy: -1
        범위: 1~10
        """
        delta = {1: 1.0, 2: 0.5, 3: -0.5, 4: -1.0}[rating]
        new_d = card.difficulty + delta
        return max(1.0, min(10.0, round(new_d, 1)))

    def retrievability(self, card: SRSCard) -> float:
        """현재 기억 확률 (0~1)."""
        if card.last_review is None:
            return 0.0
        elapsed = (datetime.now(tz=timezone.utc) - card.last_review).days
        if card.stability <= 0:
            return 0.0
        return math.exp(-elapsed / card.stability * math.log(0.9) / math.log(0.9))


# ──────────────────────────────────────────────────────────────
# 복습 큐 운영 (Claude 런타임 가이드)
# ──────────────────────────────────────────────────────────────

fsrs = FSRSLite()


def format_card_front(card: SRSCard) -> str:
    """카드 앞면 제시 포맷."""
    return (
        f"## 📇 복습 카드\n\n"
        f"**{card.front}**\n\n"
        f"---\n"
        f"정답을 떠올린 후 **\"확인\"** 이라고 입력해 주세요."
    )


def format_card_back(card: SRSCard) -> str:
    """카드 뒷면 + 평가 요청 포맷."""
    return (
        f"> [!success] 정답\n> {card.back}\n\n"
        f"---\n"
        f"난이도를 평가해 주세요:\n"
        f"① **Again** — 전혀 몰랐음\n"
        f"② **Hard** — 어렵게 기억함\n"
        f"③ **Good** — 잘 기억했음\n"
        f"④ **Easy** — 너무 쉬웠음"
    )


def parse_rating(user_input: str) -> RatingType:
    """사용자 입력을 rating(1~4)으로 변환."""
    mapping = {
        "1": 1, "①": 1, "again": 1, "Again": 1,
        "2": 2, "②": 2, "hard": 2, "Hard": 2,
        "3": 3, "③": 3, "good": 3, "Good": 3,
        "4": 4, "④": 4, "easy": 4, "Easy": 4,
    }
    for key, val in mapping.items():
        if key in user_input:
            return val
    return 3  # 기본값: Good


def format_review_summary(reviewed: int, due_remaining: int) -> str:
    """복습 세션 완료 요약."""
    return (
        f"## ✅ 복습 완료\n\n"
        f"- 오늘 복습: {reviewed}장\n"
        f"- 남은 예정: {due_remaining}장\n\n"
        f"수고하셨습니다! 학습 세션으로 돌아갑니다."
    )

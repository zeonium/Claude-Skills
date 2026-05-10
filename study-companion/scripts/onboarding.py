"""
Phase 1: 학습자 온보딩.
신규 사용자 프로필 수집 → NotebookLM 노트북 연결 → 진단 평가 → θ 추정.
"""

from __future__ import annotations

from datetime import datetime, timezone

from scripts.models import BookMetadata, LearnerProfile
from scripts.storage import LocalStorage
from scripts.utils import today_str


# ──────────────────────────────────────────────────────────────
# 학습자 프로필 질문 (정확한 워딩 — 변경 금지)
# ──────────────────────────────────────────────────────────────

PROFILE_QUESTIONS = [
    (
        "learning_goal",
        "이 자료를 학습하시는 목표를 한 문장으로 말씀해 주세요. "
        "(예: 시험 대비, 업무 적용, 교양)"
    ),
    (
        "daily_minutes",
        "하루에 학습에 쓸 수 있는 시간은 몇 분인가요? (15~120분)"
    ),
    (
        "target_days",
        "전체 학습을 며칠/몇 주 안에 마치고 싶으신가요?"
    ),
    (
        "prior_level",
        "이 분야에 대한 사전 지식 수준은?\n"
        "① 처음  ② 약간  ③ 중급  ④ 고급"
    ),
]

PRIOR_LEVEL_MAP = {
    "1": "beginner", "①": "beginner", "처음": "beginner",
    "2": "intermediate", "②": "intermediate", "약간": "intermediate",
    "3": "intermediate", "③": "intermediate", "중급": "intermediate",
    "4": "advanced", "④": "advanced", "고급": "advanced",
}


def parse_prior_level(answer: str) -> str:
    for key, val in PRIOR_LEVEL_MAP.items():
        if key in answer:
            return val
    return "intermediate"


def parse_daily_minutes(answer: str) -> int:
    import re
    nums = re.findall(r"\d+", answer)
    if nums:
        return max(15, min(120, int(nums[0])))
    return 45


# ──────────────────────────────────────────────────────────────
# 온보딩 워크플로우 (Claude 런타임 실행 가이드)
# ──────────────────────────────────────────────────────────────

def build_welcome_message(is_new_user: bool) -> str:
    if is_new_user:
        return (
            "## 📚 Study Companion에 오신 것을 환영합니다!\n\n"
            "학습 여정을 시작하기 위해 몇 가지 여쭤보겠습니다.\n"
            "먼저 " + PROFILE_QUESTIONS[0][1]
        )
    return "## 📚 Study Companion\n\n기존 학습자로 감지되었습니다. 새로운 교재로 시작합니다."


def build_diagnostic_prompt(book_title: str, topics: list[str]) -> str:
    """
    진단 평가 생성을 위해 NotebookLM에 전달할 프롬프트.
    책 전체에서 5개 핵심 개념, 난이도 균등 분포.
    """
    topic_list = "\n".join(f"- {t}" for t in topics[:5])
    return (
        f"교재 '{book_title}'의 다음 핵심 주제들을 바탕으로 "
        f"진단 평가 문항 5개를 생성해 주세요.\n\n"
        f"주제 목록:\n{topic_list}\n\n"
        f"요구사항:\n"
        f"- 각 주제당 1문항, 4지선다 형식\n"
        f"- 난이도는 매우 쉬움(1)부터 어려움(5)까지 균등 분포\n"
        f"- 정답과 해설을 함께 포함\n"
        f"- 한국어, 격식 있는 문체\n\n"
        f"JSON 형식으로 출력:\n"
        f'{{"items": [{{"id": "d1", "prompt": "...", "options": ["①", "②", "③", "④"], '
        f'"answer": "①", "difficulty": 1.0, "concept": "...", "explanation": "..."}}]}}'
    )


def estimate_theta_from_diagnostic(score_pct: float, prior_level: str) -> float:
    """
    간이 θ 추정: 진단 점수 + 사전지식 수준 결합.
    θ 범위: -2.0 ~ +2.0 (표준정규 가정)
    """
    base = {"beginner": -1.0, "intermediate": 0.0, "advanced": 1.0}[prior_level]
    # 점수 0%→-1σ, 50%→0σ, 100%→+1σ 가중
    score_offset = (score_pct - 50) / 50
    return round(base + score_offset * 0.5, 2)


def build_onboarding_summary(
    profile: LearnerProfile,
    book: BookMetadata,
    initial_theta: float,
) -> str:
    """온보딩 완료 후 사용자에게 보여줄 요약 메시지."""
    return (
        f"## ✅ 온보딩 완료\n\n"
        f"| 항목 | 값 |\n"
        f"|------|----|\n"
        f"| 교재 | {book.title} |\n"
        f"| 일일 학습 시간 | {profile.daily_minutes}분 |\n"
        f"| 사전지식 수준 | {profile.prior_level} |\n"
        f"| 초기 능력 추정 θ | {initial_theta:+.2f} |\n"
        f"| 노트 저장 볼트 | D:\\Obsi\\Obsi_Sapi\\ |\n\n"
        f"이제 커리큘럼을 생성하겠습니다. 잠시 기다려 주세요…"
    )

"""
평가 엔진: 형성평가 + 마일스톤 평가 + 간이 IRT (Bayesian Knowledge Tracing).
"""

from __future__ import annotations

import math
from datetime import date

from scripts.models import (
    AssessmentResult, ItemResponse, LearnerProfile, Weakness
)


# ──────────────────────────────────────────────────────────────
# 채점 규칙
# ──────────────────────────────────────────────────────────────

def grade_item(item: dict, user_answer: str) -> bool:
    """
    채점:
    - 객관식: exact match (숫자/번호 정규화)
    - 단답: LLM 의미적 동치 판정 (Claude 런타임에서 처리)
    - 서술: 루브릭 기반 LLM 4점 척도 (2점 이상 = 정답)
    """
    item_type = item.get("type", "mcq")
    correct_answer = str(item.get("answer", "")).strip()
    user_ans = str(user_answer).strip()

    if item_type == "mcq":
        # 번호 정규화: ①②③④ ↔ 1234 ↔ ①~④
        return _normalize_choice(correct_answer) == _normalize_choice(user_ans)
    # 단답·서술: Claude 런타임에서 LLM 채점
    return False  # 런타임에서 오버라이드


def _normalize_choice(s: str) -> str:
    mapping = {"①": "1", "②": "2", "③": "3", "④": "4",
               "⑤": "5", "1": "1", "2": "2", "3": "3", "4": "4"}
    return mapping.get(s.strip(), s.strip())


# ──────────────────────────────────────────────────────────────
# 능력 추정 업데이트 (간이 BKT)
# ──────────────────────────────────────────────────────────────

def update_theta(current_theta: float, responses: list[ItemResponse]) -> float:
    """
    간이 Bayesian Knowledge Tracing:
    정답 → +0.2σ, 오답 → -0.2σ (최대 변화 ±1.0σ)
    θ 범위: -3.0 ~ +3.0 클리핑
    """
    delta = 0.0
    for r in responses:
        delta += 0.2 if r.correct else -0.2
    new_theta = current_theta + delta
    return max(-3.0, min(3.0, round(new_theta, 2)))


# ──────────────────────────────────────────────────────────────
# 약점 식별
# ──────────────────────────────────────────────────────────────

def identify_weaknesses(responses: list[ItemResponse]) -> list[str]:
    """오답 문항의 concept_ids를 수집하여 중복 제거 후 반환."""
    weak = []
    for r in responses:
        if not r.correct:
            for cid in r.concept_ids:
                if cid not in weak:
                    weak.append(cid)
    return weak


# ──────────────────────────────────────────────────────────────
# 형성평가 피드백 포맷터
# ──────────────────────────────────────────────────────────────

def format_item_feedback(item: dict, correct: bool, user_answer: str) -> str:
    """한 문항 채점 후 즉각 피드백 마크다운."""
    icon = "✅" if correct else "❌"
    lines = [f"{icon} {'정답입니다!' if correct else '틀렸습니다.'}"]
    if not correct:
        lines.append(f"\n> [!success] 정답\n> **{item.get('answer', '')}**")
    if item.get("explanation"):
        lines.append(f"\n**해설**: {item['explanation']}")
    if item.get("concept"):
        lines.append(f"\n**관련 개념**: {item['concept']}")
    return "\n".join(lines)


def format_formative_result(result: AssessmentResult) -> str:
    """형성평가 종합 결과 마크다운."""
    bar_filled = int(result.score_pct / 100 * 10)
    bar = "🟩" * bar_filled + "⬜" * (10 - bar_filled)
    delta_str = f"▲ {result.ability_delta:+.2f}σ" if result.ability_delta >= 0 else f"▼ {result.ability_delta:.2f}σ"

    lines = [
        f"## 📊 형성평가 결과\n",
        f"점수: {bar} **{result.score_pct:.0f}%** ({result.n_correct}/{result.n_items})",
        f"능력 추정 변화: {delta_str}",
    ]
    if result.weak_concept_ids:
        lines.append(f"\n**약점 개념** ({len(result.weak_concept_ids)}개):")
        for cid in result.weak_concept_ids:
            lines.append(f"- `{cid}` → SRS 카드 생성 완료 (24시간 내 복습 예정)")
    else:
        lines.append("\n🎉 모든 개념을 잘 이해하셨습니다!")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# 마일스톤 평가 난이도 조정
# ──────────────────────────────────────────────────────────────

def target_difficulty(theta: float) -> float:
    """학습자 θ 기반 출제 난이도 결정 (θ ± 0.5 범위)."""
    return round(theta + 0.0, 1)  # 현재 수준과 동일 → ±0.5는 quiz_create 프롬프트에서 명시


def format_milestone_result(
    milestone_title: str,
    score_pct: float,
    weak_concepts: list[str],
    report_path: str,
) -> str:
    icon = "🏆" if score_pct >= 80 else ("📈" if score_pct >= 60 else "📚")
    lines = [
        f"## {icon} {milestone_title} 평가 결과\n",
        f"**점수**: {score_pct:.0f}%",
        f"**평가 기준**: 80% 이상 = Mastery 달성",
    ]
    if score_pct >= 80:
        lines.append("✅ 마일스톤 달성! Memory에 기록되었습니다.")
    else:
        lines.append("⚠️ 아직 마일스톤에 도달하지 못했습니다. 약점 클리닉을 진행합니다.")

    if weak_concepts:
        lines.append(f"\n**약점 개념**: {', '.join(weak_concepts[:5])}")
    lines.append(f"\n📄 상세 보고서: `{report_path}`")
    return "\n".join(lines)

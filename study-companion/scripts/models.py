"""
Study Companion — 핵심 데이터 모델.
모든 모델은 Pydantic v2 BaseModel. 직렬화는 JSON (ensure_ascii=False, indent=2).
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────

def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


# ─────────────────────────────────────────────
# 학습자 프로필
# ─────────────────────────────────────────────

class LearnerProfile(BaseModel):
    user_id: str = "default_user"
    name: str | None = None
    daily_minutes: int = 45
    preferred_language: Literal["ko", "en"] = "ko"
    learning_style: dict[str, float] = Field(default_factory=dict)
    timezone: str = "Asia/Seoul"
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    # 능력 추정 (전역 + 책별)
    global_ability_theta: float = 0.0
    book_abilities: dict[str, float] = Field(default_factory=dict)

    # 진단 사전지식 수준
    prior_level: Literal["beginner", "intermediate", "advanced"] = "intermediate"

    # 노트 영속화 설정 (v1.2: Obsi_Sapi 전용 — 변경 금지)
    note_root: str = r"D:\Obsi\Obsi_Sapi"
    obsidian_compatible: bool = True

    # v2.3 — Long-Term Memory 설정
    familiar_domain: str | None = None  # 비유 생성 시 우선 사용할 학습자 친숙 도메인 (예: "프로그래밍", "축구")
    analogy_domains_used: list[str] = Field(default_factory=list)  # 최근 사용한 원천 도메인 (반복 회피)
    deep_encoding_enabled: bool = True  # Acquire 단계에서 비유·사례·기억훅 자동 동반 여부

    model_config = {"frozen": False}


# ─────────────────────────────────────────────
# 교재 구조
# ─────────────────────────────────────────────

class BloomObjective(BaseModel):
    level: Literal["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
    statement: str


class Section(BaseModel):
    section_id: str = Field(default_factory=lambda: _new_id("sec"))
    chapter_id: str
    title: str
    estimated_minutes: int = 20
    source_chunks: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class Chapter(BaseModel):
    chapter_id: str = Field(default_factory=lambda: _new_id("ch"))
    title: str
    section_ids: list[str] = Field(default_factory=list)
    estimated_minutes: int = 60
    bloom_objectives: list[BloomObjective] = Field(default_factory=list)
    key_concepts: list[str] = Field(default_factory=list)

    # 메타데이터 (커리큘럼 생성 시 채워짐)
    text_word_count: int = 0
    concept_count: int = 0
    example_count: int = 0
    exercise_count: int = 0


# ─────────────────────────────────────────────
# 교재 메타데이터
# ─────────────────────────────────────────────

class BookMetadata(BaseModel):
    notebook_id: str
    title: str
    source_count: int = 0
    estimated_difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    estimated_total_hours: float = 10.0
    chapters: list[Chapter] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    last_studied_at: datetime | None = None


# ─────────────────────────────────────────────
# 시러버스
# ─────────────────────────────────────────────

DimensionType = Literal[
    "summary", "mindmap", "flashcards",
    "examples", "socratic", "assessment",
    "application", "crossref", "reflection",
    # v2.3 — Long-Term Memory dimensions
    "analogy", "case_study", "memory_hook",
]


class Day(BaseModel):
    day_number: int
    section_ids: list[str] = Field(default_factory=list)
    materials: list[DimensionType] = Field(default_factory=list)
    estimated_minutes: int = 45
    is_review_day: bool = False


class Milestone(BaseModel):
    milestone_id: str = Field(default_factory=lambda: _new_id("ms"))
    title: str
    after_week: int
    assessment_n_items: int = 30


class Week(BaseModel):
    week_number: int
    theme: str
    days: list[Day] = Field(default_factory=list)


class Syllabus(BaseModel):
    notebook_id: str
    total_weeks: int
    daily_minutes: int
    weeks: list[Week] = Field(default_factory=list)
    milestones: list[Milestone] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=_now)
    version: int = 1


# ─────────────────────────────────────────────
# 세션 / 평가
# ─────────────────────────────────────────────

class McpCallLog(BaseModel):
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    called_at: datetime = Field(default_factory=_now)
    success: bool = True
    error: str | None = None


class ItemResponse(BaseModel):
    item_id: str
    concept_ids: list[str] = Field(default_factory=list)
    correct: bool
    response_time_sec: float
    bloom_level: str


class LearningSession(BaseModel):
    session_id: str = Field(default_factory=lambda: _new_id("sess"))
    notebook_id: str
    date: date
    planned_section_ids: list[str] = Field(default_factory=list)
    completed_section_ids: list[str] = Field(default_factory=list)
    materials_viewed: dict[str, list[str]] = Field(default_factory=dict)
    assessment_results: list[ItemResponse] = Field(default_factory=list)
    reflection_journal_path: str | None = None
    time_spent_minutes: int = 0
    mcp_calls: list[McpCallLog] = Field(default_factory=list)


class AssessmentResult(BaseModel):
    session_id: str
    n_items: int
    n_correct: int
    score_pct: float
    ability_delta: float
    weak_concept_ids: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────
# SRS 카드 (FSRS-Lite)
# ─────────────────────────────────────────────

class SRSCard(BaseModel):
    card_id: str = Field(default_factory=lambda: _new_id("card"))
    notebook_id: str
    concept_id: str
    front: str
    back: str

    # FSRS state
    stability: float = 0.0
    difficulty: float = 5.0   # 1~10
    last_review: datetime | None = None
    due_date: datetime = Field(default_factory=_now)
    review_count: int = 0
    lapse_count: int = 0


# ─────────────────────────────────────────────
# Memory / Knowledge Graph 보조 모델
# ─────────────────────────────────────────────

class Concept(BaseModel):
    concept_id: str = Field(default_factory=lambda: _new_id("con"))
    title: str
    definition: str
    related_concept_ids: list[str] = Field(default_factory=list)


class Weakness(BaseModel):
    concept_id: str
    evidence: str
    recorded_at: datetime = Field(default_factory=_now)
    review_count: int = 0


# ─────────────────────────────────────────────
# 진도 스냅샷 (대시보드용)
# ─────────────────────────────────────────────

class ProgressSnapshot(BaseModel):
    notebook_id: str
    book_title: str
    total_days: int
    completed_days: int
    total_hours_spent: float
    ability_theta: float
    ability_start: float
    milestones_achieved: list[str] = Field(default_factory=list)
    milestones_pending: list[str] = Field(default_factory=list)
    top_weaknesses: list[Weakness] = Field(default_factory=list)
    srs_new: int = 0
    srs_learning: int = 0
    srs_mature: int = 0
    srs_due_today: int = 0
    snapshot_at: datetime = Field(default_factory=_now)

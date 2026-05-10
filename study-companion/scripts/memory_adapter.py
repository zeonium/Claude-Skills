"""
Memory MCP Knowledge Graph CRUD 래퍼.
엔터티 타입: Learner, Book, Concept, Milestone, Weakness
"""

from __future__ import annotations

from scripts.models import (
    BookMetadata, Concept, LearnerProfile, Milestone, Weakness
)


class MemoryAdapter:
    """
    Memory MCP 호출 래퍼.

    Claude 런타임이 memory:create_entities, memory:create_relations,
    memory:add_observations, memory:search_nodes 등을 호출할 때 따라야 할
    엔터티 구조와 관계 명세를 제공한다.

    저장 금지: 개인정보(이름, 이메일, 전화번호), 민감정보(의료, 재무 상세)
    """

    # ── 학습자 ──────────────────────────────────────────────────

    async def upsert_learner(self, profile: LearnerProfile) -> None:
        """
        MCP: memory:create_entities or memory:add_observations
        Entity type: Learner
        Name: profile.user_id
        Observations: ["daily_minutes=45", "prior_level=intermediate", ...]
        """
        observations = [
            f"daily_minutes={profile.daily_minutes}",
            f"prior_level={profile.prior_level}",
            f"preferred_language={profile.preferred_language}",
            f"global_ability_theta={profile.global_ability_theta:.2f}",
        ]
        # Claude: memory:create_entities 호출
        # [{name: profile.user_id, entityType: "Learner", observations: observations}]
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    # ── 교재 ────────────────────────────────────────────────────

    async def upsert_book(self, book: BookMetadata) -> None:
        """
        Entity type: Book
        Name: book.notebook_id
        Observations: [book.title, difficulty, estimated_hours]
        """
        observations = [
            f"title={book.title}",
            f"difficulty={book.estimated_difficulty}",
            f"estimated_hours={book.estimated_total_hours}",
        ]
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def link_learner_to_book(self, user_id: str, book_id: str) -> None:
        """
        Relation: Learner → studies → Book
        MCP: memory:create_relations
        [{from: user_id, to: book_id, relationType: "studies"}]
        """
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    # ── 개념 ────────────────────────────────────────────────────

    async def add_concepts(self, book_id: str, concepts: list[Concept]) -> None:
        """
        Entity type: Concept
        Relations: Book → contains → Concept
        """
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def link_prerequisites(self, edges: list[tuple[str, str]]) -> None:
        """
        edges: [(concept_id_a, concept_id_b), ...]
        Relation: Concept → prerequisite_of → Concept
        """
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    # ── 마일스톤 ─────────────────────────────────────────────────

    async def record_milestone_achieved(self, user_id: str, milestone: Milestone, score_pct: float) -> None:
        """
        Entity type: Milestone
        Relation: Milestone → achieved_by → Learner
        Observation: score_pct, date
        """
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    # ── 약점 ────────────────────────────────────────────────────

    async def add_weakness(self, concept_id: str, evidence: str) -> None:
        """
        Entity type: Weakness
        Name: f"weakness_{concept_id}"
        Observations: [evidence, timestamp]
        Relation: Weakness → belongs_to → Concept
        """
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def query_weaknesses(self, book_id: str) -> list[Weakness]:
        """
        MCP: memory:search_nodes query="Weakness"
        필터: belongs_to 관계로 연결된 Concept이 해당 book_id에 속하는 것
        """
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def get_concept_subgraph(self, concept_id: str, depth: int = 2) -> dict:
        """
        MCP: memory:open_nodes + 연결 탐색
        """
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

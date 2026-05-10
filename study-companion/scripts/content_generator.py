"""
9차원 학습자료 디스패처.
캐시 확인 → 어댑터 호출 → 캐시 저장.
"""

from __future__ import annotations

from scripts.models import DimensionType, LearnerProfile
from scripts.storage import LocalStorage


class ContentGenerator:
    """
    9개 학습자료 차원 디스패처.
    Claude 런타임에서 각 핸들러 메서드를 직접 구현하거나
    NotebookLM MCP 도구를 호출한다.
    """

    def __init__(self, storage: LocalStorage):
        self.storage = storage

    async def generate(
        self,
        notebook_id: str,
        section_id: str,
        section_title: str,
        dimension: DimensionType,
        learner: LearnerProfile,
    ) -> dict:
        """
        1. 캐시 확인 (TTL: 30일 — 캐시 파일 mtime 기준)
        2. 캐시 히트 → 반환
        3. 캐시 미스 → 핸들러 호출 → 캐시 저장 → 반환
        """
        cached = self.storage.get_cache(notebook_id, section_id, dimension)
        if cached is not None:
            return {"source": "cache", "dimension": dimension, "data": cached}

        handler = self._get_handler(dimension)
        result = await handler(notebook_id, section_id, section_title, learner)
        self.storage.set_cache(notebook_id, section_id, dimension, result)
        return {"source": "generated", "dimension": dimension, "data": result}

    def _get_handler(self, dimension: DimensionType):
        handlers = {
            "summary":     self._summary,
            "mindmap":     self._mindmap,
            "flashcards":  self._flashcards,
            "examples":    self._examples,
            "socratic":    self._socratic,
            "assessment":  self._assessment,
            "application": self._application,
            "crossref":    self._crossref,
            "reflection":  self._reflection,
            # v2.3 — Long-Term Memory dimensions
            "analogy":     self._analogy,
            "case_study":  self._case_study,
            "memory_hook": self._memory_hook,
        }
        return handlers[dimension]

    # ── v2.3 통합 호출 ──────────────────────────────────────────

    async def deep_encoding(
        self,
        notebook_id: str,
        section_id: str,
        section_title: str,
        concept_title: str,
        learner: LearnerProfile,
    ) -> dict:
        """
        v2.3: 한 핵심 개념에 대해 비유 + 실제 사례 + 기억 훅을 한 번에 생성.
        Acquire 단계에서 핵심 개념마다 호출되거나, MEMORIZE 의도 시 호출됨.

        반환:
        {
          "concept_title": str,
          "analogy":     {<6.13 출력>},
          "case_study":  {<6.14 출력>},
          "memory_hook": {<6.15 출력>}
        }

        학습자가 "빠른 모드" 등을 선택해 deep_encoding_enabled=False면 스킵.
        """
        if not learner.deep_encoding_enabled:
            return {"skipped": True, "reason": "deep_encoding_enabled=False"}

        analogy = await self.generate(notebook_id, section_id, section_title, "analogy", learner)
        case_study = await self.generate(notebook_id, section_id, section_title, "case_study", learner)
        memory_hook = await self.generate(notebook_id, section_id, section_title, "memory_hook", learner)
        return {
            "concept_title": concept_title,
            "analogy": analogy.get("data"),
            "case_study": case_study.get("data"),
            "memory_hook": memory_hook.get("data"),
        }

    # ── 12개 핸들러 ────────────────────────────────────────────

    async def _summary(self, notebook_id, section_id, section_title, learner) -> dict:
        """
        3계층 요약 생성.
        MCP: notebooklm__notebook_query (SUMMARY_3LAYER_TPL 프롬프트 사용)
        참조: references/prompts.md § 6.1
        반환: {"L1": "한줄", "L2": "단락", "L3": "심화"}
        """
        # Claude: references/prompts.md의 SUMMARY_3LAYER_TPL을 사용해
        # notebooklm__notebook_query 호출 후 JSON 파싱
        raise NotImplementedError("Claude 런타임 구현")

    async def _mindmap(self, notebook_id, section_id, section_title, learner) -> dict:
        """
        마인드맵 생성.
        MCP: notebooklm__mind_map_create → studio_status 폴링
        반환: {"studio_id": "...", "status": "complete"} 또는 Mermaid 텍스트
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _flashcards(self, notebook_id, section_id, section_title, learner) -> list:
        """
        플래시카드 15장 생성.
        MCP: notebooklm__flashcards_create
        반환: [{"front": "...", "back": "..."}, ...]
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _examples(self, notebook_id, section_id, section_title, learner) -> list:
        """
        워크드 예제 3개 (쉬움/중간/어려움).
        MCP: notebooklm__notebook_query
        프롬프트: references/prompts.md § 6.4 EXAMPLES_TPL
        반환: [{"difficulty": "easy", "problem": "...", "solution": "..."}, ...]
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _socratic(self, notebook_id, section_id, section_title, learner) -> list:
        """
        소크라테스식 발문 5단계.
        MCP: notebooklm__notebook_query
        프롬프트: references/prompts.md § 6.2 SOCRATIC_TPL
        반환: [{"question": "...", "hint": "...", "model_answer": "..."}, ...]
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _assessment(self, notebook_id, section_id, section_title, learner) -> dict:
        """
        형성평가 5문항.
        MCP: notebooklm__quiz_create
        반환: {"items": [{id, prompt, options, answer, bloom_level, concept}, ...]}
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _application(self, notebook_id, section_id, section_title, learner) -> list:
        """
        실무·실생활 응용 사례 3개.
        MCP: notebooklm__notebook_query
        프롬프트: references/prompts.md § 6.5 APPLICATION_TPL
        반환: [{"scenario": "...", "application": "..."}, ...]
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _crossref(self, notebook_id, section_id, section_title, learner) -> list:
        """
        외부 자료 교차 참조.
        MCP: notebooklm__research_start → research_import
        반환: [{"title": "...", "url": "...", "relevance": "..."}, ...]
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _reflection(self, notebook_id, section_id, section_title, learner) -> list:
        """
        메타인지 가이드 질문 3개.
        MCP: notebooklm__notebook_query
        프롬프트: references/prompts.md § 6.3 REFLECTION_TPL
        반환: ["질문1", "질문2", "질문3"]
        """
        raise NotImplementedError("Claude 런타임 구현")

    # ── v2.3 Long-Term Memory 핸들러 ─────────────────────────────

    async def _analogy(self, notebook_id, section_id, section_title, learner) -> dict:
        """
        비유·은유 3개 생성 (사물·구조·동작).
        MCP: notebooklm__notebook_query
        프롬프트: references/prompts.md § 6.13 ANALOGY_METAPHOR_TPL
        입력 추가: learner.familiar_domain (없으면 일반 도메인 사용)
        제약: learner.analogy_domains_used 최근 5개 회피
        반환: {"concept_title": "...", "analogies": [{kind, name, body, mapping, breaking_point}, ...]}
        참고: references/analogy_library.md 의 도메인 카탈로그 활용
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _case_study(self, notebook_id, section_id, section_title, learner) -> dict:
        """
        실제 사례 3개 (역사·실패·반사실).
        MCP: notebooklm__notebook_query (필요 시 web_search 보강)
        프롬프트: references/prompts.md § 6.14 CASE_STUDY_TPL
        반환: {"concept_title": "...", "cases": [{kind, title, when, where, who, narrative, lesson}, ...]}
        """
        raise NotImplementedError("Claude 런타임 구현")

    async def _memory_hook(self, notebook_id, section_id, section_title, learner) -> dict:
        """
        기억술 패키지 (두문자·이야기·기억궁전).
        MCP: notebooklm__notebook_query
        프롬프트: references/prompts.md § 6.15 MEMORY_HOOK_TPL
        반환: {
          "concept_title": "...", "items": [...],
          "acronym_or_acrostic": {device, expansion, note},
          "story_chain": {story, item_to_sentence_map},
          "memory_palace": {space, walkthrough},
          "fragility_note": "..."
        }
        """
        raise NotImplementedError("Claude 런타임 구현")


# ──────────────────────────────────────────────────────────────
# 차원별 사용자 제시 포맷터
# ──────────────────────────────────────────────────────────────

def format_dimension_output(dimension: DimensionType, data: dict | list, section_title: str) -> str:
    """각 차원의 결과를 사용자에게 보여줄 마크다운으로 포맷."""

    if dimension == "summary":
        d = data if isinstance(data, dict) else {}
        return (
            f"### 📋 {section_title} — 3계층 요약\n\n"
            f"**한 줄**: {d.get('L1', '')}\n\n"
            f"**단락**: {d.get('L2', '')}\n\n"
            f"**심화**:\n{d.get('L3', '')}\n"
        )

    if dimension == "mindmap":
        return f"### 🗺️ {section_title} — 마인드맵\n\n(NotebookLM 마인드맵 생성 완료)\n"

    if dimension == "flashcards":
        cards = data if isinstance(data, list) else []
        lines = [f"### 📇 {section_title} — 플래시카드 ({len(cards)}장)\n"]
        for i, c in enumerate(cards[:5], 1):
            lines.append(f"**카드 {i}**: {c.get('front', '')} → _{c.get('back', '')}_")
        if len(cards) > 5:
            lines.append(f"_(+{len(cards)-5}장 더 있음 — Obsidian에서 확인)_")
        return "\n".join(lines)

    if dimension == "socratic":
        items = data if isinstance(data, list) else []
        lines = [f"### 🤔 {section_title} — 소크라테스 발문\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"**Q{i}**: {item.get('question', '')}")
            if item.get("hint"):
                lines.append(f"> 힌트: {item['hint']}")
        return "\n".join(lines)

    if dimension == "examples":
        items = data if isinstance(data, list) else []
        lines = [f"### 💡 {section_title} — 워크드 예제\n"]
        for item in items:
            lines.append(f"**[{item.get('difficulty', '')}]** {item.get('problem', '')}\n")
        return "\n".join(lines)

    if dimension == "assessment":
        d = data if isinstance(data, dict) else {}
        items = d.get("items", [])
        lines = [f"### ✏️ {section_title} — 형성평가 ({len(items)}문항)\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"**Q{i}**: {item.get('prompt', '')}")
            opts = item.get("options", [])
            for opt in opts:
                lines.append(f"  {opt}")
        return "\n".join(lines)

    if dimension == "reflection":
        questions = data if isinstance(data, list) else []
        lines = [f"### 🪞 {section_title} — 메타인지 일지\n"]
        for i, q in enumerate(questions, 1):
            lines.append(f"**{i}.** {q}\n")
        return "\n".join(lines)

    # ── v2.3 Long-Term Memory 차원 포맷터 ──────────────────────

    if dimension == "analogy":
        d = data if isinstance(data, dict) else {}
        analogies = d.get("analogies", [])
        title = d.get("concept_title", section_title)
        lines = [f"### 🌉 비유로 이해하기 — {title}\n"]
        kind_label = {"object": "사물", "structural": "구조", "action": "동작"}
        for a in analogies:
            kind = kind_label.get(a.get("kind", ""), a.get("kind", ""))
            lines.append(f"**[{kind}] {a.get('name', '')}**")
            lines.append(f"> {a.get('body', '')}")
            mapping = a.get("mapping", [])
            if mapping:
                lines.append("**정확한 매핑**:")
                for m in mapping:
                    lines.append(f"- {m.get('source', '')} ↔ {m.get('target', '')}")
            bp = a.get("breaking_point", "")
            if bp:
                lines.append(f"⚠ **비유의 한계**: {bp}\n")
        return "\n".join(lines)

    if dimension == "case_study":
        d = data if isinstance(data, dict) else {}
        cases = d.get("cases", [])
        title = d.get("concept_title", section_title)
        lines = [f"### 📜 사례로 새기기 — {title}\n"]
        kind_label = {"historical": "역사적 사례", "failure": "실패 사례", "counterfactual": "반사실 사례"}
        for c in cases:
            kind = kind_label.get(c.get("kind", ""), c.get("kind", ""))
            lines.append(f"**[{kind}] {c.get('title', '')}**")
            lines.append(f"_시간_: {c.get('when', '')} · _장소_: {c.get('where', '')} · _인물_: {c.get('who', '')}")
            lines.append(f"> {c.get('narrative', '')}")
            lesson = c.get("lesson", "")
            if lesson:
                lines.append(f"📌 **교훈**: {lesson}\n")
        return "\n".join(lines)

    if dimension == "memory_hook":
        d = data if isinstance(data, dict) else {}
        title = d.get("concept_title", section_title)
        lines = [f"### 🔗 기억 훅 — {title}\n"]

        ac = d.get("acronym_or_acrostic", {}) or {}
        if ac:
            lines.append(f"**🅰 두문자**: `{ac.get('device', '')}` — {ac.get('expansion', '')}")
            note = ac.get("note", "")
            if note:
                lines.append(f"_왜 잘 기억되나_: {note}\n")

        sc = d.get("story_chain", {}) or {}
        if sc:
            lines.append(f"**📖 이야기 사슬**:")
            lines.append(f"> {sc.get('story', '')}\n")

        mp = d.get("memory_palace", {}) or {}
        if mp:
            lines.append(f"**🏛 기억의 궁전** (`{mp.get('space', '')}`):")
            for step in mp.get("walkthrough", []):
                lines.append(
                    f"{step.get('step', '?')}. **{step.get('location', '')}** → {step.get('item', '')} ({step.get('vivid_image', '')})"
                )
            lines.append("")

        frag = d.get("fragility_note", "")
        if frag:
            lines.append(f"⚠ **취약 지점**: {frag}")
        return "\n".join(lines)

    return f"### {dimension.title()} — {section_title}\n\n{str(data)}\n"

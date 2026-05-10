"""
obsidian-mcp-tools MCP 기반 Obsidian 볼트 영속화 (v2.0).

설계 원칙:
- obsidian-mcp-tools MCP만을 통해 Obsidian 볼트에 마크다운 파일을 저장한다.
- 경로는 볼트 루트 기준 상대 경로(POSIX 슬래시)를 사용한다.
- Filesystem MCP 및 obsidian-snowball MCP는 사용하지 않는다.
- 볼트 루트 경로 설정 불필요 — obsidian-mcp-tools가 연결된 볼트를 자동 인식한다.
"""

from __future__ import annotations

from datetime import date
from pathlib import PurePosixPath

from scripts.models import (
    BookMetadata, LearnerProfile, LearningSession, Milestone,
    ProgressSnapshot, SRSCard,
)
from scripts.utils import slugify, today_str


# ──────────────────────────────────────────────────────────────
# 볼트 상수
# ──────────────────────────────────────────────────────────────

SUBDIRS = {
    "books":       "01_Books",
    "sessions":    "02_Sessions",
    "milestones":  "03_Milestones",
    "concepts":    "04_Concepts",
    "flashcards":  "05_Flashcards",
    "reflections": "06_Reflections",
    "templates":   "99_Templates",
}


# ──────────────────────────────────────────────────────────────
# obsidian-mcp-tools MCP 래퍼 인터페이스 (Claude 런타임이 구현)
# ──────────────────────────────────────────────────────────────

class ObsidianSapiAdapter:
    """
    obsidian-mcp-tools MCP 호출 인터페이스.
    Claude 런타임에서 실제 MCP 도구를 호출한다.

    경로 규칙: 볼트 루트 기준 상대 경로 (POSIX 슬래시).
    예) "02_Sessions/2025/2025-01/2025-01-01.md"
    """

    async def create_file(self, path: str, content: str) -> None:
        """obsidian-mcp-tools MCP: create_vault_file(path, content)"""
        raise NotImplementedError("Claude 런타임에서 obsidian-mcp-tools MCP 직접 호출")

    async def get_file(self, path: str) -> str | None:
        """obsidian-mcp-tools MCP: get_vault_file(path) — 없으면 None 반환"""
        raise NotImplementedError("Claude 런타임에서 obsidian-mcp-tools MCP 직접 호출")

    async def patch_file(self, path: str, content: str) -> None:
        """obsidian-mcp-tools MCP: patch_vault_file(path, content) — 덮어쓰기 갱신"""
        raise NotImplementedError("Claude 런타임에서 obsidian-mcp-tools MCP 직접 호출")

    async def list_files(self, path: str) -> list[str]:
        """obsidian-mcp-tools MCP: list_vault_files(path) — 경로 내 파일 목록"""
        raise NotImplementedError("Claude 런타임에서 obsidian-mcp-tools MCP 직접 호출")

    async def get_server_info(self) -> dict:
        """obsidian-mcp-tools MCP: get_server_info() — 서버 연결 상태 확인"""
        raise NotImplementedError("Claude 런타임에서 obsidian-mcp-tools MCP 직접 호출")

    async def exists(self, path: str) -> bool:
        """get_file 호출 후 None 여부로 존재 확인."""
        result = await self.get_file(path)
        return result is not None


# ──────────────────────────────────────────────────────────────
# 노트 영속화 어댑터
# ──────────────────────────────────────────────────────────────

class NotePersistenceAdapter:
    """obsidian-mcp-tools MCP를 통한 Obsidian 볼트 마크다운 영속화."""

    def __init__(self, learner: LearnerProfile, sapi: ObsidianSapiAdapter):
        self.sapi = sapi

    # ── 내부 쓰기 헬퍼 ─────────────────────────────────────────

    async def _write(self, vault_relative_path: str, content: str) -> str:
        """파일 생성 또는 갱신 (존재하면 patch, 없으면 create)."""
        path = _to_vault_path(vault_relative_path)
        if await self.sapi.exists(path):
            await self.sapi.patch_file(path, content)
        else:
            await self.sapi.create_file(path, content)
        return path

    # ── 볼트 초기화 ─────────────────────────────────────────────

    async def initialize_vault(self) -> dict:
        """
        Obsidian 볼트 첫 사용 시 1회 실행.
        _index.md + README.md 시드 파일 생성.
        멱등 — 이미 존재하는 항목은 건드리지 않음.
        """
        created = []
        existing = []

        index_path = "_index.md"
        if not await self.sapi.exists(index_path):
            await self.sapi.create_file(index_path, _seed_index())
            created.append("_index.md")
        else:
            existing.append("_index.md")

        readme_path = "README.md"
        if not await self.sapi.exists(readme_path):
            await self.sapi.create_file(readme_path, _seed_readme())
            created.append("README.md")
        else:
            existing.append("README.md")

        return {"created": created, "existing": existing}

    # ── 헬스체크 ────────────────────────────────────────────────

    async def health_check(self) -> dict:
        """
        세션 시작 시 obsidian-mcp-tools MCP 연결 및 볼트 상태 검증.
        반환: {ok: bool, issues: [...]}
        """
        issues = []

        try:
            await self.sapi.get_server_info()
        except Exception as e:
            issues.append(f"obsidian-mcp-tools MCP 연결 실패: {e}")
            return {"ok": False, "issues": issues}

        if not await self.sapi.exists("_index.md"):
            issues.append("_index.md 없음 — initialize_vault() 호출 필요")

        if issues:
            return {"ok": False, "issues": issues}
        return {"ok": True, "issues": []}

    # ── 일일 세션 노트 ───────────────────────────────────────────

    async def write_session_note(self, session: LearningSession, book: BookMetadata, body_md: str) -> str:
        """02_Sessions/{YYYY}/{YYYY-MM}/{YYYY-MM-DD}.md"""
        d = session.date
        path = f"02_Sessions/{d.year}/{d.strftime('%Y-%m')}/{d.isoformat()}.md"
        frontmatter = _fm({
            "type": "study-session",
            "date": d.isoformat(),
            "book": book.title,
            "notebook_id": session.notebook_id,
            "section_ids": session.completed_section_ids,
            "duration_min": session.time_spent_minutes,
            "tags": ["study-companion", f"book/{slugify(book.title)}"],
        })
        content = frontmatter + f"\n# {d.isoformat()} 학습 세션\n\n" + body_md
        return await self._write(path, content)

    # ── 메타인지 일지 ────────────────────────────────────────────

    async def write_reflection(self, session_date: date, qa_pairs: list[tuple[str, str]]) -> str:
        """06_Reflections/{YYYY-MM}/{YYYY-MM-DD}-reflection.md"""
        d = session_date
        path = f"06_Reflections/{d.strftime('%Y-%m')}/{d.isoformat()}-reflection.md"
        frontmatter = _fm({
            "type": "reflection",
            "date": d.isoformat(),
            "tags": ["study-companion", "reflection"],
        })
        body = "\n".join(f"**Q: {q}**\n\n{a}\n" for q, a in qa_pairs)
        content = frontmatter + f"\n# {d.isoformat()} 메타인지 일지\n\n" + body
        return await self._write(path, content)

    # ── 마일스톤 보고서 ──────────────────────────────────────────

    async def write_milestone_report(self, milestone: Milestone, report_md: str) -> str:
        """03_Milestones/{milestone_id}.md"""
        path = f"03_Milestones/{milestone.milestone_id}.md"
        frontmatter = _fm({
            "type": "milestone",
            "milestone_id": milestone.milestone_id,
            "title": milestone.title,
            "after_week": milestone.after_week,
            "tags": ["study-companion", "milestone"],
        })
        content = frontmatter + f"\n# {milestone.title}\n\n" + report_md
        return await self._write(path, content)

    # ── 책 인덱스 노트 ───────────────────────────────────────────

    async def upsert_book_index(self, book: BookMetadata, progress: dict) -> str:
        """01_Books/{slug}.md — 매 세션 후 진도 표 갱신."""
        slug = slugify(book.title)
        path = f"01_Books/{slug}.md"
        completed = progress.get("completed_days", 0)
        total = progress.get("total_days", 1)
        pct = int(completed / total * 100)
        frontmatter = _fm({
            "type": "book-index",
            "notebook_id": book.notebook_id,
            "book": book.title,
            "difficulty": book.estimated_difficulty,
            "progress_pct": pct,
            "tags": ["study-companion", f"book/{slug}"],
        })
        body = (
            f"# {book.title}\n\n"
            f"- 난이도: {book.estimated_difficulty}\n"
            f"- 추정 시간: {book.estimated_total_hours}h\n"
            f"- 진도: {pct}% ({completed}/{total}일)\n"
        )
        content = frontmatter + body
        return await self._write(path, content)

    # ── 개념 노트 ───────────────────────────────────────────────

    async def upsert_concept_note(
        self, concept_id: str, title: str, definition: str, related: list[str]
    ) -> str:
        """04_Concepts/{slug}.md — wikilinks 포함."""
        slug = slugify(title)
        path = f"04_Concepts/{slug}.md"
        links = " ".join(f"[[04_Concepts/{slugify(r)}]]" for r in related)
        frontmatter = _fm({
            "type": "concept",
            "concept_id": concept_id,
            "title": title,
            "tags": ["study-companion", "concept"],
        })
        body = (
            f"# {title}\n\n"
            f"> [!note] 정의\n> {definition}\n\n"
            f"## 연관 개념\n\n{links}\n"
        )
        content = frontmatter + body
        return await self._write(path, content)

    # ── SRS 카드 (Obsidian SR 호환) ─────────────────────────────

    async def export_srs_card(self, card: SRSCard, concept_title: str = "") -> str:
        """
        05_Flashcards/{card_id}.md
        Obsidian Spaced Repetition 플러그인 호환 포맷.
        """
        path = f"05_Flashcards/{card.card_id}.md"
        due_str = card.due_date.strftime("%Y-%m-%d") if card.due_date else today_str()
        frontmatter = _fm({
            "type": "flashcard",
            "card_id": card.card_id,
            "concept": concept_title or card.concept_id,
            "tags": ["study-companion", "flashcard"],
        })
        body = (
            f"{card.front}\n\n"
            f"?\n\n"
            f"{card.back}\n\n"
            f"<!--SR:!{due_str},{card.review_count},{int(card.stability * 100)}-->\n"
        )
        content = frontmatter + body
        return await self._write(path, content)

    # ── 대시보드 갱신 ────────────────────────────────────────────

    async def refresh_dashboard(self, snapshot: ProgressSnapshot) -> str:
        """_index.md (볼트 루트) — 전체 진도 요약."""
        path = "_index.md"
        completed = snapshot.completed_days
        total = snapshot.total_days
        bar_filled = int(completed / max(total, 1) * 16)
        bar = "█" * bar_filled + "░" * (16 - bar_filled)
        pct = int(completed / max(total, 1) * 100)

        weak_lines = "\n".join(
            f"{i+1}. **{w.concept_id}** — {w.evidence[:40]}"
            for i, w in enumerate(snapshot.top_weaknesses[:3])
        )

        ms_achieved = "\n".join(f"- ✅ {m}" for m in snapshot.milestones_achieved)
        ms_pending = "\n".join(f"- ⏳ {m}" for m in snapshot.milestones_pending[:3])

        frontmatter = _fm({
            "type": "dashboard",
            "updated": today_str(),
            "tags": ["study-companion", "dashboard"],
        })
        body = (
            f"# 📊 Study Companion 대시보드\n\n"
            f"## 현재 학습: {snapshot.book_title}\n\n"
            f"### 진도\n\n"
            f"- 전체: {bar} {pct}% (Day {completed}/{total})\n"
            f"- 누적 학습 시간: {snapshot.total_hours_spent:.1f}시간\n\n"
            f"### 능력 추정 (θ)\n\n"
            f"- 시작: {snapshot.ability_start:+.1f} → 현재: {snapshot.ability_theta:+.1f}\n\n"
            f"### 마일스톤\n\n{ms_achieved}\n{ms_pending}\n\n"
            f"### 약점 클리닉\n\n{weak_lines or '없음'}\n\n"
            f"### SRS 카드\n\n"
            f"- 신규: {snapshot.srs_new}장 / 학습중: {snapshot.srs_learning}장 / 성숙: {snapshot.srs_mature}장\n"
            f"- 오늘 복습 예정: {snapshot.srs_due_today}장\n"
        )
        return await self._write(path, frontmatter + body)


# ──────────────────────────────────────────────────────────────
# 내부 헬퍼
# ──────────────────────────────────────────────────────────────

def _to_vault_path(relative_path: str) -> str:
    """백슬래시 정규화 → POSIX 슬래시 상대 경로."""
    return str(PurePosixPath(relative_path.replace("\\", "/")))


def _fm(fields: dict) -> str:
    """YAML frontmatter 생성."""
    lines = ["---"]
    for k, v in fields.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f'  - "{item}"')
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---\n")
    return "\n".join(lines)


def _seed_index() -> str:
    return _fm({"type": "dashboard", "updated": today_str(), "tags": ["study-companion", "dashboard"]}) + (
        "# 📊 Study Companion 대시보드\n\n"
        "> 이 볼트는 Study Companion 스킬이 obsidian-mcp-tools MCP를 통해 자동으로 관리합니다.\n\n"
        "## 학습 시작하기\n\n"
        'Claude Desktop에서 "이 책으로 공부 시작"이라고 말씀해 주세요.\n'
    )


def _seed_readme() -> str:
    return (
        "# Obsidian 볼트 — Study Companion 전용\n\n"
        "이 볼트는 Study Companion Claude Desktop 스킬이 obsidian-mcp-tools MCP를 통해 학습 노트를 자동 저장합니다.\n\n"
        "## 폴더 구조\n\n"
        "| 폴더 | 내용 |\n"
        "|------|------|\n"
        "| 01_Books | 교재별 인덱스 노트 |\n"
        "| 02_Sessions | 일일 학습 세션 노트 |\n"
        "| 03_Milestones | 주차별 마일스톤 보고서 |\n"
        "| 04_Concepts | 개념 노트 (백링크 허브) |\n"
        "| 05_Flashcards | SRS 플래시카드 |\n"
        "| 06_Reflections | 메타인지 일지 |\n"
        "| 99_Templates | Templater 호환 템플릿 |\n\n"
        "## 주의\n\n"
        "- 폴더 이름/경로를 임의로 변경하면 자동 저장이 중단될 수 있습니다.\n"
        "- 노트 저장에 obsidian-mcp-tools MCP를 사용하며, Filesystem MCP는 사용하지 않습니다.\n"
    )


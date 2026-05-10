"""
로컬 JSON 파일 기반 저장소.
모든 파일 I/O의 단일 진입점 — 스크립트 외부에서 직접 open() 금지.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from scripts.models import (
    BookMetadata, LearnerProfile, LearningSession, SRSCard, Syllabus
)
from scripts.utils import ensure_dir, json_dumps, json_loads, user_data_root

T = TypeVar("T", bound=BaseModel)


class LocalStorage:
    """사용자 데이터 디렉토리 기반 영속화."""

    def __init__(self, root: Path | None = None):
        self.root = root or user_data_root()
        ensure_dir(self.root)

    # ── 학습자 프로필 ──────────────────────────────

    def load_learner(self) -> LearnerProfile | None:
        path = self.root / "learner.json"
        if not path.exists():
            return None
        return LearnerProfile.model_validate_json(path.read_text(encoding="utf-8"))

    def save_learner(self, profile: LearnerProfile) -> None:
        path = self.root / "learner.json"
        path.write_text(profile.model_dump_json(indent=2), encoding="utf-8")

    # ── 교재 메타데이터 ────────────────────────────

    def _book_dir(self, notebook_id: str) -> Path:
        return ensure_dir(self.root / "books" / notebook_id)

    def load_book(self, notebook_id: str) -> BookMetadata | None:
        path = self._book_dir(notebook_id) / "metadata.json"
        if not path.exists():
            return None
        return BookMetadata.model_validate_json(path.read_text(encoding="utf-8"))

    def save_book(self, book: BookMetadata) -> None:
        path = self._book_dir(book.notebook_id) / "metadata.json"
        path.write_text(book.model_dump_json(indent=2), encoding="utf-8")

    def list_books(self) -> list[BookMetadata]:
        books_dir = self.root / "books"
        if not books_dir.exists():
            return []
        result = []
        for sub in books_dir.iterdir():
            if sub.is_dir():
                meta = self.load_book(sub.name)
                if meta:
                    result.append(meta)
        return result

    # ── 시러버스 ───────────────────────────────────

    def load_syllabus(self, notebook_id: str) -> Syllabus | None:
        path = self._book_dir(notebook_id) / "syllabus.json"
        if not path.exists():
            return None
        return Syllabus.model_validate_json(path.read_text(encoding="utf-8"))

    def save_syllabus(self, syllabus: Syllabus) -> None:
        path = self._book_dir(syllabus.notebook_id) / "syllabus.json"
        path.write_text(syllabus.model_dump_json(indent=2), encoding="utf-8")

    # ── 세션 ──────────────────────────────────────

    def _session_path(self, notebook_id: str, session_date: date) -> Path:
        sessions_dir = ensure_dir(self._book_dir(notebook_id) / "sessions")
        return sessions_dir / f"{session_date.isoformat()}.json"

    def load_session(self, notebook_id: str, session_date: date) -> LearningSession | None:
        path = self._session_path(notebook_id, session_date)
        if not path.exists():
            return None
        return LearningSession.model_validate_json(path.read_text(encoding="utf-8"))

    def save_session(self, session: LearningSession) -> None:
        path = self._session_path(session.notebook_id, session.date)
        path.write_text(session.model_dump_json(indent=2), encoding="utf-8")

    def list_sessions(self, notebook_id: str) -> list[LearningSession]:
        sessions_dir = self._book_dir(notebook_id) / "sessions"
        if not sessions_dir.exists():
            return []
        sessions = []
        for p in sorted(sessions_dir.glob("*.json")):
            sessions.append(LearningSession.model_validate_json(p.read_text(encoding="utf-8")))
        return sessions

    # ── SRS 덱 ────────────────────────────────────

    def _deck_path(self) -> Path:
        return ensure_dir(self.root / "srs") / "deck.json"

    def load_deck(self) -> list[SRSCard]:
        path = self._deck_path()
        if not path.exists():
            return []
        raw = json_loads(path.read_text(encoding="utf-8"))
        return [SRSCard.model_validate(item) for item in raw]

    def save_deck(self, cards: list[SRSCard]) -> None:
        path = self._deck_path()
        data = [c.model_dump() for c in cards]
        path.write_text(json_dumps(data), encoding="utf-8")

    def get_due_cards(self, notebook_id: str, today: date) -> list[SRSCard]:
        deck = self.load_deck()
        return [
            c for c in deck
            if c.notebook_id == notebook_id and c.due_date.date() <= today
        ]

    def update_card(self, updated: SRSCard) -> None:
        deck = self.load_deck()
        deck = [updated if c.card_id == updated.card_id else c for c in deck]
        if not any(c.card_id == updated.card_id for c in deck):
            deck.append(updated)
        self.save_deck(deck)

    # ── 콘텐츠 캐시 ───────────────────────────────

    def _cache_path(self, notebook_id: str, section_id: str, dimension: str) -> Path:
        cache_dir = ensure_dir(self.root / "cache" / "content" / notebook_id / section_id)
        return cache_dir / f"{dimension}.json"

    def get_cache(self, notebook_id: str, section_id: str, dimension: str) -> object | None:
        path = self._cache_path(notebook_id, section_id, dimension)
        if not path.exists():
            return None
        return json_loads(path.read_text(encoding="utf-8"))

    def set_cache(self, notebook_id: str, section_id: str, dimension: str, data: object) -> None:
        path = self._cache_path(notebook_id, section_id, dimension)
        path.write_text(json_dumps(data), encoding="utf-8")

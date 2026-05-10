"""
NotebookLM MCP 호출 추상화.
모든 NotebookLM MCP 도구 호출의 단일 진입점.

런타임 환경(Claude Desktop)에서 Claude가 직접 NotebookLM MCP 도구를 호출한다.
이 모듈은 Claude가 따라야 할 호출 패턴과 파라미터 컨벤션을 문서화한다.
"""

from __future__ import annotations

import asyncio
from typing import Any

from scripts.models import McpCallLog, SRSCard
from scripts.utils import today_str

# ──────────────────────────────────────────────────────────────
# 재시도 정책 (런타임 Claude가 참조)
# 최대 3회 / 지수 백오프 2→4→8초 / TimeoutError·연결오류에만 적용
RETRY_ATTEMPTS = 3
RETRY_BASE_WAIT = 2   # 초
STUDIO_POLL_INTERVAL = 10  # 초
STUDIO_MAX_POLLS = 12  # 120초


class NotebookLMAdapter:
    """
    Claude 런타임에서 NotebookLM MCP 도구를 호출할 때 따라야 할 패턴.

    실제 MCP 호출은 Claude가 직접 수행하며, 이 클래스는 호출 시퀀스·
    파라미터 규약·폴링 로직을 코드로 명세화한 것이다.

    사용 방법 (Claude 런타임):
        adapter = NotebookLMAdapter(session_log=[])
        desc = await adapter.describe_notebook(notebook_id)
        summary = await adapter.generate_summary(notebook_id, section_id, level=2)
    """

    def __init__(self, session_log: list[McpCallLog]):
        self.log = session_log

    def _record(self, tool: str, args: dict, success: bool = True, error: str | None = None) -> None:
        self.log.append(McpCallLog(tool=tool, args=args, success=success, error=error))

    # ── 노트북 관리 ──────────────────────────────────────────────

    async def create_notebook(self, title: str, sources: list[dict]) -> str:
        """
        MCP 도구: notebooklm__notebook_create
        반환: notebook_id
        """
        # Claude: notebooklm__notebook_create 호출 후 반환된 ID를 저장
        self._record("notebooklm__notebook_create", {"title": title})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def describe_notebook(self, notebook_id: str) -> dict:
        """
        MCP 도구: notebooklm__notebook_describe
        반환: {title, source_count, suggested_topics: [...]}
        """
        self._record("notebooklm__notebook_describe", {"notebook_id": notebook_id})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def query(self, notebook_id: str, prompt: str) -> str:
        """
        MCP 도구: notebooklm__notebook_query
        반환: 응답 텍스트
        """
        self._record("notebooklm__notebook_query", {"notebook_id": notebook_id, "prompt": prompt[:80]})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    # ── 9차원 자료 생성 ─────────────────────────────────────────

    async def generate_summary(self, notebook_id: str, section_title: str, level: int = 2) -> dict:
        """
        level 1: 한 줄 (25자 이내)
        level 2: 단락 (100~150자)
        level 3: 심화 (400~500자)
        MCP: notebooklm__notebook_query (SUMMARY_3LAYER_TPL 사용)
        """
        from scripts.utils import json_loads
        prompt = _build_summary_prompt(section_title, level)
        self._record("notebooklm__notebook_query", {"notebook_id": notebook_id, "type": "summary", "level": level})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_mindmap(self, notebook_id: str, scope: str) -> dict:
        """
        MCP: notebooklm__mind_map_create
        scope = chapter or section title
        반환: {status, studio_id} → wait_for_studio() 로 폴링
        """
        self._record("notebooklm__mind_map_create", {"notebook_id": notebook_id, "scope": scope})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_flashcards(self, notebook_id: str, scope: str, n: int = 15) -> list[dict]:
        """
        MCP: notebooklm__flashcards_create
        반환: [{front, back}, ...]
        """
        self._record("notebooklm__flashcards_create", {"notebook_id": notebook_id, "scope": scope})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_quiz(self, notebook_id: str, scope: str, n: int = 5) -> dict:
        """
        MCP: notebooklm__quiz_create
        반환: {items: [{id, prompt, options, answer, bloom_level}, ...]}
        """
        self._record("notebooklm__quiz_create", {"notebook_id": notebook_id, "scope": scope, "n": n})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_audio_overview(self, notebook_id: str, scope: str) -> str:
        """
        MCP: notebooklm__audio_overview_create
        반환: studio_id (wait_for_studio 필요)
        """
        self._record("notebooklm__audio_overview_create", {"notebook_id": notebook_id, "scope": scope})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_report(self, notebook_id: str, scope: str) -> str:
        """MCP: notebooklm__report_create"""
        self._record("notebooklm__report_create", {"notebook_id": notebook_id, "scope": scope})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_slide_deck(self, notebook_id: str, scope: str) -> str:
        """MCP: notebooklm__slide_deck_create"""
        self._record("notebooklm__slide_deck_create", {"notebook_id": notebook_id, "scope": scope})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_infographic(self, notebook_id: str, scope: str) -> str:
        """MCP: notebooklm__infographic_create"""
        self._record("notebooklm__infographic_create", {"notebook_id": notebook_id, "scope": scope})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    async def generate_data_table(self, notebook_id: str, scope: str) -> str:
        """MCP: notebooklm__data_table_create"""
        self._record("notebooklm__data_table_create", {"notebook_id": notebook_id, "scope": scope})
        raise NotImplementedError("Claude 런타임에서 MCP 직접 호출")

    # ── 비동기 폴링 ──────────────────────────────────────────────

    async def wait_for_studio(self, studio_id: str, timeout_secs: int = 120) -> dict:
        """
        MCP: notebooklm__studio_status
        최대 12회 (10초 간격) 폴링.
        타임아웃 시 {"status": "timeout"} 반환.
        """
        for i in range(STUDIO_MAX_POLLS):
            self._record("notebooklm__studio_status", {"studio_id": studio_id, "attempt": i + 1})
            # Claude: studio_status MCP 호출 → status 확인
            # status == "complete" 이면 반환
            # status == "in_progress" 이면 10초 대기
            await asyncio.sleep(STUDIO_POLL_INTERVAL)
        return {"status": "timeout", "studio_id": studio_id}


# ── 내부 헬퍼 ─────────────────────────────────────────────────

def _build_summary_prompt(section_title: str, level: int) -> str:
    if level == 1:
        return f"'{section_title}' 섹션의 핵심 메시지를 25자 이내 한 문장으로 요약하세요."
    if level == 2:
        return f"'{section_title}' 섹션의 핵심 개념 3~5개를 100~150자 단락으로 요약하세요."
    return f"'{section_title}' 섹션을 정의·예시·주의점·연결 개념 포함 400~500자로 심화 요약하세요."

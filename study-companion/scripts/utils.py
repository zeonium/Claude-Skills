"""공통 헬퍼 유틸리티."""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path


def slugify(text: str, max_len: int = 60) -> str:
    """한국어·영어 혼합 텍스트를 파일명 안전 슬러그로 변환."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[\\/:*?\"<>|]", "", text)   # Windows 금지 문자
    text = re.sub(r"\s+", "_", text.strip())
    text = text[:max_len]
    return text or "untitled"


def json_dumps(obj: object) -> str:
    """한글 보존 JSON 직렬화."""
    def _default(o: object) -> str:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")

    return json.dumps(obj, ensure_ascii=False, indent=2, default=_default)


def json_loads(text: str) -> object:
    return json.loads(text)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_data_root() -> Path:
    r"""%USERPROFILE%\.study-companion\ 경로."""
    import os
    home = Path(os.environ.get("USERPROFILE", Path.home()))
    return home / ".study-companion"


def today_str() -> str:
    return date.today().isoformat()


def week_label(week_number: int) -> str:
    return f"Week {week_number}"

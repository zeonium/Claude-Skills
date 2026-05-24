#!/usr/bin/env python3
"""
Ticker list parser for value-investing-framework skill.

Reads input from stdin (JSON or raw text) or a file path argument.
Returns normalized ticker list as JSON to stdout.

Usage:
    python parse_ticker_list.py path/to/file.csv
    python parse_ticker_list.py path/to/file.xlsx
    python parse_ticker_list.py path/to/file.txt
    echo "005930, AAPL, MSFT" | python parse_ticker_list.py -
    cat names.txt | python parse_ticker_list.py -
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

COLUMN_ALIASES = {
    "code": ["code", "ticker", "symbol", "종목코드", "티커", "코드"],
    "name": ["name", "company", "company_name", "종목명", "회사명", "이름"],
    "market": ["market", "exchange", "시장", "거래소"],
    "currency": ["currency", "통화"],
}

KOREAN_CODE_RE = re.compile(r"^\d{6}$")
US_TICKER_RE = re.compile(r"^[A-Z]{1,5}$")


def normalize_column(col: str) -> str | None:
    col_lower = str(col).strip().lower()
    for canonical, aliases in COLUMN_ALIASES.items():
        if col_lower in [a.lower() for a in aliases]:
            return canonical
    return None


def normalize_code(raw: str) -> tuple[str, str | None]:
    """Return (code, inferred_market)."""
    s = str(raw).strip().upper().lstrip("$")

    suffix_map = {
        ".KS": "KOSPI",
        ".KQ": "KOSDAQ",
        ".KR": "KOSPI",
        ".HK": "HK",
        ".SH": "CN-A",
        ".SZ": "CN-A",
        ".T": "JP",
        ".L": "LON",
    }
    for suffix, market in suffix_map.items():
        if s.endswith(suffix):
            code = s[: -len(suffix)]
            if market in ("KOSPI", "KOSDAQ"):
                code = code.zfill(6)
            return code, market

    if s.isdigit():
        code = s.zfill(6)
        if len(code) == 6:
            return code, "KR-UNKNOWN"

    if US_TICKER_RE.match(s):
        return s, "US-UNKNOWN"

    return s, None


def infer_market(code: str, name: str = "") -> str | None:
    if KOREAN_CODE_RE.match(code):
        return "KR-UNKNOWN"
    if US_TICKER_RE.match(code):
        return "US-UNKNOWN"
    return None


def parse_csv(path: Path) -> list[dict[str, Any]]:
    try:
        import pandas as pd
    except ImportError:
        print("pandas required for CSV parsing", file=sys.stderr)
        sys.exit(1)

    for encoding in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            df = pd.read_csv(path, encoding=encoding, dtype=str)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Could not decode {path}")

    return _df_to_records(df)


def parse_xlsx(path: Path, sheet: str | int = 0) -> list[dict[str, Any]]:
    try:
        import pandas as pd
    except ImportError:
        print("pandas required for Excel parsing", file=sys.stderr)
        sys.exit(1)

    df = pd.read_excel(path, sheet_name=sheet, dtype=str)
    return _df_to_records(df)


def _df_to_records(df) -> list[dict[str, Any]]:
    rename_map = {}
    for col in df.columns:
        canonical = normalize_column(col)
        if canonical:
            rename_map[col] = canonical

    df = df.rename(columns=rename_map)
    df = df.dropna(how="all")

    records = []
    for _, row in df.iterrows():
        rec: dict[str, Any] = {}
        raw_code = row.get("code")
        raw_name = row.get("name")
        raw_market = row.get("market")
        raw_currency = row.get("currency")

        if raw_code and not _is_nan(raw_code):
            code, inferred = normalize_code(raw_code)
            rec["code"] = code
            rec["market"] = (
                str(raw_market).strip().upper()
                if raw_market and not _is_nan(raw_market)
                else inferred
            )
        elif raw_name and not _is_nan(raw_name):
            rec["code"] = None
            rec["market"] = (
                str(raw_market).strip().upper()
                if raw_market and not _is_nan(raw_market)
                else None
            )
        else:
            continue

        if raw_name and not _is_nan(raw_name):
            rec["name"] = str(raw_name).strip()

        if raw_currency and not _is_nan(raw_currency):
            rec["currency"] = str(raw_currency).strip().upper()

        records.append(rec)

    return records


def _is_nan(val) -> bool:
    try:
        import math

        return isinstance(val, float) and math.isnan(val)
    except Exception:
        return False


def parse_text(content: str) -> list[dict[str, Any]]:
    records = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for token in re.split(r"[,;\t]+", line):
            token = token.strip()
            if not token:
                continue
            code, inferred = normalize_code(token)
            if inferred:
                records.append({"code": code, "market": inferred})
            else:
                records.append({"code": None, "name": token, "market": None})
    return _dedupe(records)


def _dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for r in records:
        key = (r.get("code"), r.get("name"))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def parse_file(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return parse_csv(path)
    if suffix in (".xlsx", ".xls", ".xlsm"):
        return parse_xlsx(path)
    if suffix in (".txt", ".tsv", ""):
        return parse_text(path.read_text(encoding="utf-8", errors="replace"))
    if suffix == ".md":
        return parse_text(path.read_text(encoding="utf-8", errors="replace"))
    raise ValueError(f"Unsupported file type: {suffix}")


def main() -> int:
    if len(sys.argv) < 2:
        content = sys.stdin.read()
        records = parse_text(content)
    else:
        arg = sys.argv[1]
        if arg == "-":
            content = sys.stdin.read()
            records = parse_text(content)
        else:
            path = Path(arg)
            if not path.exists():
                print(json.dumps({"error": f"File not found: {arg}"}, ensure_ascii=False))
                return 1
            records = parse_file(path)

    records = _dedupe(records)
    print(json.dumps(records, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

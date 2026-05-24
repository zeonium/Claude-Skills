#!/usr/bin/env python3
"""
Liquidation Value calculator for value-investing-framework.

Implements Graham/Greenwald liquidation value with per-asset recovery rates.
Use for declining industries or as conservative floor for any company.

Input JSON via stdin:
{
  "assets": {
    "cash": 1000,
    "short_term_securities": 500,
    "receivables": 800,
    "inventory_raw": 300,
    "inventory_wip": 200,
    "inventory_finished": 400,
    "ppe_land": 600,
    "ppe_buildings": 800,
    "ppe_equipment": 700,
    "intangibles_goodwill": 1000,
    "intangibles_brand": 200,
    "investments": 500
  },
  "liabilities": {
    "current": 800,
    "long_term": 1200,
    "contingent": 100
  },
  "shares_outstanding": 1000,
  "industry_mode": "declining"  // or "stable"
}

Output JSON to stdout:
{
  "liquidation_value": ...,
  "per_share": ...,
  "breakdown": [...],
  "warnings": [...]
}
"""

from __future__ import annotations

import json
import sys

RECOVERY_RATES = {
    "stable": {
        "cash": 1.00,
        "short_term_securities": 0.95,
        "receivables": 0.80,
        "inventory_raw": 0.50,
        "inventory_wip": 0.40,
        "inventory_finished": 0.60,
        "ppe_land": 0.90,
        "ppe_buildings": 0.60,
        "ppe_equipment": 0.25,
        "intangibles_goodwill": 0.00,
        "intangibles_brand": 0.15,
        "investments": 1.00,
        "other": 0.30,
    },
    "declining": {
        "cash": 1.00,
        "short_term_securities": 0.90,
        "receivables": 0.65,
        "inventory_raw": 0.30,
        "inventory_wip": 0.20,
        "inventory_finished": 0.35,
        "ppe_land": 0.70,
        "ppe_buildings": 0.35,
        "ppe_equipment": 0.10,
        "intangibles_goodwill": 0.00,
        "intangibles_brand": 0.00,
        "investments": 0.80,
        "other": 0.15,
    },
    "conservative": {
        "cash": 1.00,
        "short_term_securities": 0.95,
        "receivables": 0.75,
        "inventory_raw": 0.40,
        "inventory_wip": 0.30,
        "inventory_finished": 0.50,
        "ppe_land": 0.80,
        "ppe_buildings": 0.50,
        "ppe_equipment": 0.20,
        "intangibles_goodwill": 0.00,
        "intangibles_brand": 0.10,
        "investments": 0.90,
        "other": 0.20,
    },
}


def compute_liquidation(payload: dict) -> dict:
    industry_mode = payload.get("industry_mode", "stable")
    if industry_mode not in RECOVERY_RATES:
        industry_mode = "stable"

    rates = RECOVERY_RATES[industry_mode]
    assets = payload.get("assets", {}) or {}
    liabilities = payload.get("liabilities", {}) or {}
    shares = float(payload.get("shares_outstanding", 0) or 0)

    breakdown = []
    recovered_total = 0.0
    warnings = []

    for asset_key, book_value in assets.items():
        if book_value is None:
            continue
        try:
            bv = float(book_value)
        except (TypeError, ValueError):
            warnings.append(f"non-numeric asset value: {asset_key}={book_value}")
            continue

        rate = rates.get(asset_key, rates["other"])
        if asset_key not in rates:
            warnings.append(f"unknown asset key {asset_key}, used 'other' rate {rate}")

        recovered = bv * rate
        recovered_total += recovered
        breakdown.append({
            "item": asset_key,
            "book_value": bv,
            "recovery_rate": rate,
            "recovered_value": round(recovered, 2),
        })

    total_liabilities = 0.0
    for key in ("current", "long_term", "contingent"):
        val = liabilities.get(key, 0) or 0
        try:
            total_liabilities += float(val)
        except (TypeError, ValueError):
            warnings.append(f"non-numeric liability: {key}={val}")

    sum_book_assets = sum(
        float(v) for v in assets.values() if v is not None and _is_number(v)
    )
    liquidation_cost_rate = 0.08 if industry_mode == "declining" else 0.06
    liquidation_cost = sum_book_assets * liquidation_cost_rate

    liquidation_value = recovered_total - total_liabilities - liquidation_cost
    per_share = liquidation_value / shares if shares > 0 else None

    return {
        "industry_mode": industry_mode,
        "recovery_rates_applied": rates,
        "breakdown": breakdown,
        "recovered_assets_total": round(recovered_total, 2),
        "total_liabilities": round(total_liabilities, 2),
        "liquidation_cost_rate": liquidation_cost_rate,
        "liquidation_cost": round(liquidation_cost, 2),
        "liquidation_value": round(liquidation_value, 2),
        "per_share": round(per_share, 4) if per_share is not None else None,
        "shares_outstanding": shares,
        "warnings": warnings,
    }


def _is_number(v) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"error": "empty input"}, ensure_ascii=False))
        return 1
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"invalid JSON: {e}"}, ensure_ascii=False))
        return 1

    result = compute_liquidation(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

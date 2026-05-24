#!/usr/bin/env python3
"""
Margin of Safety calculator for value-investing-framework.

Input JSON via stdin:
{
  "intrinsic_value_per_share": {
    "bear": 8000,
    "base": 12000,
    "bull": 16000
  },
  "current_price": 9500,
  "case": "C"   // "A" | "B" | "C"  -- determines threshold profile
}

Output JSON: margin of safety per scenario + recommended buy prices + opinion.
"""

from __future__ import annotations

import json
import sys

OPINION_THRESHOLDS = {
    "A": {"strong_buy": 0.60, "buy": 0.45, "conditional_buy": 0.33, "hold": 0.10},
    "B": {"strong_buy": 0.50, "buy": 0.33, "conditional_buy": None, "hold": 0.10},
    "C": {"strong_buy": 0.40, "buy": 0.25, "conditional_buy": None, "hold": 0.10},
}


def compute_mos(intrinsic: float | None, price: float) -> float | None:
    if intrinsic is None or intrinsic <= 0 or price <= 0:
        return None
    return (intrinsic - price) / intrinsic


def opinion_for(mos: float | None, case: str, has_catalyst: bool = False) -> str:
    if mos is None:
        return "INSUFFICIENT_DATA"
    thresholds = OPINION_THRESHOLDS.get(case.upper(), OPINION_THRESHOLDS["B"])
    if mos >= thresholds["strong_buy"]:
        return "STRONG_BUY"
    if mos >= thresholds["buy"]:
        return "BUY"
    if case.upper() == "A" and thresholds["conditional_buy"] is not None and mos >= thresholds["conditional_buy"]:
        return "CONDITIONAL_BUY" if has_catalyst else "AVOID"
    if mos >= thresholds["hold"]:
        return "HOLD"
    return "AVOID"


def compute(payload: dict) -> dict:
    iv = payload.get("intrinsic_value_per_share") or {}
    price = float(payload.get("current_price", 0) or 0)
    case = (payload.get("case") or "B").upper()
    has_catalyst = bool(payload.get("has_catalyst", False))

    bear = iv.get("bear")
    base = iv.get("base")
    bull = iv.get("bull")

    if bear is not None:
        bear = float(bear)
    if base is not None:
        base = float(base)
    if bull is not None:
        bull = float(bull)

    mos_bear = compute_mos(bear, price)
    mos_base = compute_mos(base, price)
    mos_bull = compute_mos(bull, price)

    if base is None:
        return {"error": "intrinsic_value_per_share.base is required"}

    # Recommended buy prices (Base scenario)
    thresholds = OPINION_THRESHOLDS.get(case, OPINION_THRESHOLDS["B"])
    buy_threshold = thresholds["buy"]
    strong_buy_threshold = thresholds["strong_buy"]

    target_buy_price = base * (1.0 - buy_threshold)
    target_strong_buy_price = base * (1.0 - strong_buy_threshold)

    opinion_base = opinion_for(mos_base, case, has_catalyst)

    return {
        "case": case,
        "has_catalyst": has_catalyst,
        "current_price": price,
        "intrinsic_value": {"bear": bear, "base": base, "bull": bull},
        "margin_of_safety": {
            "bear": round(mos_bear, 4) if mos_bear is not None else None,
            "base": round(mos_base, 4) if mos_base is not None else None,
            "bull": round(mos_bull, 4) if mos_bull is not None else None,
        },
        "thresholds_used": thresholds,
        "recommended_prices": {
            "buy_zone_upper": round(target_buy_price, 4),
            "strong_buy_zone_upper": round(target_strong_buy_price, 4),
        },
        "opinion_base": opinion_base,
        "opinion_bear": opinion_for(mos_bear, case, has_catalyst),
        "opinion_bull": opinion_for(mos_bull, case, has_catalyst),
    }


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
    result = compute(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

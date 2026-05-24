#!/usr/bin/env python3
"""
AV vs EPV matrix classifier for value-investing-framework.

Input JSON via stdin:
{
  "av_per_share": 10000,
  "epv_per_share": 14000,
  "av_total": 10000000,
  "epv_total": 14000000,
  "roic": 0.14,
  "wacc": 0.085,
  "thresholds": {
    "case_a_max": 0.7,
    "case_c_min": 1.3
  }
}

Output JSON: case classification + ROIC validation + final case + confidence.
"""

from __future__ import annotations

import json
import sys


def classify(payload: dict) -> dict:
    warnings = []

    av = payload.get("av_per_share")
    epv = payload.get("epv_per_share")

    if av is None or epv is None:
        av = payload.get("av_total")
        epv = payload.get("epv_total")
        if av is None or epv is None:
            return {"error": "must provide either av_per_share+epv_per_share or av_total+epv_total"}

    try:
        av = float(av)
        epv = float(epv)
    except (TypeError, ValueError):
        return {"error": "av and epv must be numeric"}

    if av <= 0:
        warnings.append("AV is zero or negative; defaulting to Case A (Special-handling required)")
        return {
            "ratio": None,
            "primary_case": "A",
            "final_case": "A",
            "confidence": "Low",
            "roic_check": "N/A",
            "warnings": warnings,
            "note": "AV non-positive — consider liquidation/Special branch",
        }

    ratio = epv / av

    thresholds = payload.get("thresholds") or {}
    case_a_max = float(thresholds.get("case_a_max", 0.7))
    case_c_min = float(thresholds.get("case_c_min", 1.3))

    if ratio < case_a_max:
        primary = "A"
    elif ratio <= case_c_min:
        primary = "B"
    else:
        primary = "C"

    roic = payload.get("roic")
    wacc = payload.get("wacc")
    final = primary
    roic_check = "no ROIC/WACC provided, skipped"
    confidence = "Medium"

    if roic is not None and wacc is not None:
        try:
            roic_v = float(roic)
            wacc_v = float(wacc)
            spread = roic_v - wacc_v
            if spread > 0.03:
                if primary == "A":
                    final = "C"
                    warnings.append("ROIC > WACC + 3pp but EPV/AV<0.7 — AV may be overstated; reclassified to C")
                    confidence = "Low"
                elif primary == "B":
                    final = "C"
                    confidence = "Medium"
                    roic_check = f"ROIC-WACC={spread:.2%} reinforces Case C"
                else:
                    confidence = "High"
                    roic_check = f"ROIC-WACC={spread:.2%} reinforces Case C"
            elif spread > 0:
                if primary == "C":
                    confidence = "Medium"
                    roic_check = f"ROIC slightly above WACC (+{spread:.2%}) supports Case C weakly"
                else:
                    confidence = "Medium"
                    roic_check = f"ROIC slightly above WACC supports B/A"
            else:
                if primary == "C":
                    final = "A"
                    warnings.append(
                        f"EPV/AV>1.3 but ROIC<WACC (spread={spread:.2%}); reclassified to A (capital destruction)"
                    )
                    confidence = "Low"
                else:
                    confidence = "High" if primary == "A" else "Medium"
                    roic_check = f"ROIC<WACC ({spread:.2%}) reinforces Case A"
        except (TypeError, ValueError):
            warnings.append("invalid ROIC or WACC; skipped check")
    else:
        if abs(ratio - case_a_max) < 0.05 or abs(ratio - case_c_min) < 0.05:
            confidence = "Low"
            warnings.append("ratio near threshold and no ROIC provided; classification confidence low")

    return {
        "av": round(av, 4),
        "epv": round(epv, 4),
        "ratio": round(ratio, 4),
        "thresholds": {"case_a_max": case_a_max, "case_c_min": case_c_min},
        "primary_case": primary,
        "roic": roic,
        "wacc": wacc,
        "roic_minus_wacc": (round(float(roic) - float(wacc), 4) if roic is not None and wacc is not None else None),
        "roic_check": roic_check,
        "final_case": final,
        "confidence": confidence,
        "warnings": warnings,
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
    result = classify(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

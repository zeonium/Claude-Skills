#!/usr/bin/env python3
"""
Earnings Power Value (EPV) calculator for value-investing-framework.

Input JSON via stdin:
{
  "ebit_history": [1200, 1350, 1100, 1400, 1500],   // 5+ years
  "one_time_items_per_year": [0, 100, -50, 0, 200],  // signs: + means to ADD back (cost), - means to REMOVE (gain)
  "revenue_history": [10000, 11000, 10500, 12000, 13000],   // optional, for cycle normalization
  "normalization_method": "average_margin",  // "average_margin" | "simple_average" | "weighted_recent" | "shiller_cape"
  "da_history": [400, 420, 450, 470, 500],
  "maintenance_capex_estimate": 480,    // optional; if missing, derived from D&A
  "effective_tax_rate": 0.22,
  "wacc": 0.085,
  "net_debt": 8000,
  "shares_outstanding": 1000
}

Output JSON: normalized EBIT, NOPAT, EPV (enterprise / equity / per share), confidence.
"""

from __future__ import annotations

import json
import statistics as stats
import sys


def normalize_ebit(payload: dict, warnings: list) -> tuple[float, str]:
    history = list(payload.get("ebit_history") or [])
    one_time = list(payload.get("one_time_items_per_year") or [])
    revenue_history = list(payload.get("revenue_history") or [])
    method = payload.get("normalization_method", "average_margin")

    if not history:
        raise ValueError("ebit_history is required")

    # Adjust for one-time items
    adjusted_ebit = []
    for i, ebit in enumerate(history):
        try:
            e = float(ebit)
        except (TypeError, ValueError):
            continue
        adj = float(one_time[i]) if i < len(one_time) and one_time[i] is not None else 0.0
        adjusted_ebit.append(e + adj)

    if not adjusted_ebit:
        raise ValueError("no valid EBIT entries after parsing")

    n = len(adjusted_ebit)

    if method == "average_margin" and revenue_history and len(revenue_history) == len(history):
        try:
            margins = [adjusted_ebit[i] / float(revenue_history[i]) for i in range(n) if revenue_history[i]]
            avg_margin = sum(margins) / len(margins)
            latest_rev = float(revenue_history[-1])
            return avg_margin * latest_rev, "average_margin"
        except Exception as e:
            warnings.append(f"average_margin failed: {e}; fell back to simple_average")

    if method == "weighted_recent":
        weights = [0.5, 0.3, 0.2] if n >= 3 else [1.0 / n] * n
        if n < 3:
            return sum(adjusted_ebit) / n, "simple_average"
        recent = adjusted_ebit[-3:]
        return sum(w * x for w, x in zip(weights, recent)), "weighted_recent"

    if method == "shiller_cape" and n >= 7:
        return stats.mean(adjusted_ebit[-10:]) if n >= 10 else stats.mean(adjusted_ebit), "shiller_cape"

    # default: simple average
    return sum(adjusted_ebit) / n, "simple_average"


def estimate_maintenance_capex(payload: dict, warnings: list) -> float:
    mx = payload.get("maintenance_capex_estimate")
    if mx is not None:
        try:
            return float(mx)
        except (TypeError, ValueError):
            warnings.append("invalid maintenance_capex_estimate; deriving from D&A")
    da_history = payload.get("da_history") or []
    if da_history:
        avg_da = sum(float(x) for x in da_history if x is not None) / max(1, len(da_history))
        return avg_da
    warnings.append("no D&A history; setting maintenance_capex to 0")
    return 0.0


def compute_epv(payload: dict) -> dict:
    warnings = []

    norm_ebit, method_used = normalize_ebit(payload, warnings)

    da_history = payload.get("da_history") or []
    avg_da = sum(float(x) for x in da_history if x is not None) / max(1, len(da_history)) if da_history else 0.0

    maint_capex = estimate_maintenance_capex(payload, warnings)

    # Adjusted EBIT = EBITDA - Maintenance CapEx
    # EBITDA ≈ normalized EBIT + average D&A (since EBIT already excludes D&A)
    ebitda = norm_ebit + avg_da
    adjusted_ebit = ebitda - maint_capex

    tax_rate = float(payload.get("effective_tax_rate", 0.22) or 0.22)
    nopat = adjusted_ebit * (1.0 - tax_rate)

    wacc = float(payload.get("wacc", 0.10) or 0.10)
    if wacc <= 0:
        return {"error": "wacc must be positive"}

    epv_enterprise = nopat / wacc
    net_debt = float(payload.get("net_debt", 0) or 0)
    epv_equity = epv_enterprise - net_debt

    shares = float(payload.get("shares_outstanding", 0) or 0)
    per_share = epv_equity / shares if shares > 0 else None

    n = len(payload.get("ebit_history") or [])
    if n >= 5:
        confidence = "High"
    elif n >= 3:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "normalization_method_used": method_used,
        "normalized_ebit": round(norm_ebit, 2),
        "average_da": round(avg_da, 2),
        "maintenance_capex": round(maint_capex, 2),
        "ebitda": round(ebitda, 2),
        "adjusted_ebit": round(adjusted_ebit, 2),
        "effective_tax_rate": tax_rate,
        "nopat": round(nopat, 2),
        "wacc": wacc,
        "epv_enterprise": round(epv_enterprise, 2),
        "net_debt": round(net_debt, 2),
        "epv_equity": round(epv_equity, 2),
        "per_share": round(per_share, 4) if per_share is not None else None,
        "shares_outstanding": shares,
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
    try:
        result = compute_epv(payload)
    except ValueError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

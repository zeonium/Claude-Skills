#!/usr/bin/env python3
"""
WACC calculator for value-investing-framework.

Input JSON via stdin:
{
  "risk_free_rate": 0.040,
  "beta": 1.10,
  "equity_risk_premium": 0.055,
  "cost_of_debt": 0.045,
  "effective_tax_rate": 0.22,
  "market_cap": 50000,
  "total_debt": 15000,
  "cash": 5000
}

Output JSON:
{
  "cost_of_equity": ...,
  "after_tax_cost_of_debt": ...,
  "weight_equity": ...,
  "weight_debt": ...,
  "wacc": ...,
  "net_debt": ...
}

If beta/Re components missing, returns best-effort calculation with warnings.
"""

from __future__ import annotations

import json
import sys


def compute_wacc(payload: dict) -> dict:
    warnings = []

    rf = payload.get("risk_free_rate")
    if rf is None:
        warnings.append("missing risk_free_rate, using default 0.04")
        rf = 0.04
    rf = float(rf)

    beta = payload.get("beta")
    if beta is None:
        warnings.append("missing beta, using default 1.0")
        beta = 1.0
    beta = float(beta)

    erp = payload.get("equity_risk_premium")
    if erp is None:
        warnings.append("missing equity_risk_premium, using default 0.055")
        erp = 0.055
    erp = float(erp)

    cost_of_debt = payload.get("cost_of_debt")
    if cost_of_debt is None:
        cost_of_debt = rf + 0.025
        warnings.append(f"missing cost_of_debt, derived from Rf + 250bp = {cost_of_debt:.4f}")
    cost_of_debt = float(cost_of_debt)

    tax_rate = payload.get("effective_tax_rate")
    if tax_rate is None:
        warnings.append("missing effective_tax_rate, using default 0.22")
        tax_rate = 0.22
    tax_rate = float(tax_rate)

    market_cap = float(payload.get("market_cap", 0) or 0)
    total_debt = float(payload.get("total_debt", 0) or 0)
    cash = float(payload.get("cash", 0) or 0)

    if market_cap <= 0:
        warnings.append("missing or zero market_cap; setting weight_equity=1, weight_debt=0")
        weight_equity = 1.0
        weight_debt = 0.0
    else:
        v = market_cap + total_debt
        if v <= 0:
            weight_equity = 1.0
            weight_debt = 0.0
        else:
            weight_equity = market_cap / v
            weight_debt = total_debt / v

    cost_of_equity = rf + beta * erp
    after_tax_kd = cost_of_debt * (1.0 - tax_rate)
    wacc = weight_equity * cost_of_equity + weight_debt * after_tax_kd
    net_debt = total_debt - cash

    return {
        "inputs": {
            "risk_free_rate": rf,
            "beta": beta,
            "equity_risk_premium": erp,
            "cost_of_debt": cost_of_debt,
            "effective_tax_rate": tax_rate,
            "market_cap": market_cap,
            "total_debt": total_debt,
            "cash": cash,
        },
        "cost_of_equity": round(cost_of_equity, 6),
        "after_tax_cost_of_debt": round(after_tax_kd, 6),
        "weight_equity": round(weight_equity, 6),
        "weight_debt": round(weight_debt, 6),
        "wacc": round(wacc, 6),
        "net_debt": round(net_debt, 2),
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
    result = compute_wacc(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

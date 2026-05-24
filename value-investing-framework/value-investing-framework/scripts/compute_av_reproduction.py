#!/usr/bin/env python3
"""
Reproduction Cost calculator for value-investing-framework.

Implements Greenwald reproduction cost with intangible asset capitalization.
Use for going-concern businesses in stable or growing industries.

Input JSON via stdin:
{
  "book_value_equity": 5000,
  "rd_expenses": [200, 220, 250, 280, 300],
  "advertising_expenses": [100, 110, 120, 130, 140],
  "sga_customer_acquisition": 50,
  "labor_cost_annual": 800,
  "rd_useful_life_years": 5,
  "rd_decay_rate": 0.25,
  "ad_capitalization_rate": 0.50,
  "ad_capitalization_years": 4,
  "customer_capital_years": 3,
  "labor_capital_years": 1.5,
  "organizational_capital": 0,
  "asset_impairment_adjustment": 0,
  "contingent_liabilities": 0,
  "shares_outstanding": 1000,
  "industry_type": "B2C"
}

Output JSON to stdout.
"""

from __future__ import annotations

import json
import sys

INDUSTRY_DEFAULTS = {
    "B2C": {"ad_capitalization_rate": 0.50, "rd_decay_rate": 0.30, "rd_useful_life": 5},
    "B2B": {"ad_capitalization_rate": 0.25, "rd_decay_rate": 0.25, "rd_useful_life": 6},
    "industrial": {"ad_capitalization_rate": 0.15, "rd_decay_rate": 0.20, "rd_useful_life": 7},
    "pharma": {"ad_capitalization_rate": 0.30, "rd_decay_rate": 0.15, "rd_useful_life": 10},
    "tech": {"ad_capitalization_rate": 0.30, "rd_decay_rate": 0.35, "rd_useful_life": 4},
}


def capitalize_rd(expenses: list, life: int, decay: float) -> float:
    if not expenses:
        return 0.0
    capital = 0.0
    expenses_recent_first = list(reversed(expenses))
    for i, exp in enumerate(expenses_recent_first[:life]):
        try:
            e = float(exp)
        except (TypeError, ValueError):
            continue
        remaining = max(0.0, 1.0 - decay * i)
        capital += e * remaining
    return capital


def capitalize_marketing(expenses: list, years: int, rate: float) -> float:
    if not expenses:
        return 0.0
    cap = 0.0
    expenses_recent_first = list(reversed(expenses))
    for exp in expenses_recent_first[:years]:
        try:
            e = float(exp)
        except (TypeError, ValueError):
            continue
        cap += e * rate
    return cap


def compute_reproduction(payload: dict) -> dict:
    industry_type = payload.get("industry_type", "B2C")
    defaults = INDUSTRY_DEFAULTS.get(industry_type, INDUSTRY_DEFAULTS["B2C"])

    book_value = float(payload.get("book_value_equity", 0) or 0)
    rd_expenses = payload.get("rd_expenses", []) or []
    ad_expenses = payload.get("advertising_expenses", []) or []
    customer_cost = float(payload.get("sga_customer_acquisition", 0) or 0)
    labor_cost = float(payload.get("labor_cost_annual", 0) or 0)
    rd_life = int(payload.get("rd_useful_life_years", defaults["rd_useful_life"]))
    rd_decay = float(payload.get("rd_decay_rate", defaults["rd_decay_rate"]))
    ad_rate = float(payload.get("ad_capitalization_rate", defaults["ad_capitalization_rate"]))
    ad_years = int(payload.get("ad_capitalization_years", 4))
    cust_years = float(payload.get("customer_capital_years", 3))
    labor_years = float(payload.get("labor_capital_years", 1.5))
    org_capital = float(payload.get("organizational_capital", 0) or 0)
    impairment_adj = float(payload.get("asset_impairment_adjustment", 0) or 0)
    contingent = float(payload.get("contingent_liabilities", 0) or 0)
    shares = float(payload.get("shares_outstanding", 0) or 0)

    rd_capital = capitalize_rd(rd_expenses, rd_life, rd_decay)
    brand_capital = capitalize_marketing(ad_expenses, ad_years, ad_rate)
    customer_capital = customer_cost * cust_years
    human_capital = labor_cost * labor_years

    breakdown = {
        "book_value_equity": round(book_value, 2),
        "rd_capital": round(rd_capital, 2),
        "brand_capital": round(brand_capital, 2),
        "customer_capital": round(customer_capital, 2),
        "human_capital": round(human_capital, 2),
        "organizational_capital": round(org_capital, 2),
        "asset_impairment_adjustment": round(impairment_adj, 2),
        "contingent_liabilities": round(contingent, 2),
    }

    intangible_total = (
        rd_capital + brand_capital + customer_capital + human_capital + org_capital
    )
    reproduction_cost = (
        book_value + intangible_total - impairment_adj - contingent
    )
    per_share = reproduction_cost / shares if shares > 0 else None

    assumptions_used = {
        "industry_type": industry_type,
        "rd_useful_life_years": rd_life,
        "rd_decay_rate": rd_decay,
        "ad_capitalization_rate": ad_rate,
        "ad_capitalization_years": ad_years,
        "customer_capital_years": cust_years,
        "labor_capital_years": labor_years,
    }

    return {
        "assumptions": assumptions_used,
        "breakdown": breakdown,
        "intangible_capital_total": round(intangible_total, 2),
        "reproduction_cost": round(reproduction_cost, 2),
        "per_share": round(per_share, 4) if per_share is not None else None,
        "shares_outstanding": shares,
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
    result = compute_reproduction(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

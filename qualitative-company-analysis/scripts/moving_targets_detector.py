#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moving Targets Detector — KPI 이동 감지 (컨퍼런스콜 분기별 강조점 변화)

목적:
  경영진이 분기마다 어떤 KPI를 강조하고 어떤 KPI를 회피하는지 추적합니다.
  결과는 earnings_qna_redflag_checklist.md §3과 management_credibility_scorecard.md에 반영합니다.

의존성 설치:
  pip3 install plotly pandas --break-system-packages

사용 예시:
  python3 moving_targets_detector.py \
    --transcripts q1.txt q2.txt q3.txt q4.txt \
    --quarters "FY24Q1" "FY24Q2" "FY24Q3" "FY24Q4" \
    --lang ko --company 삼성전자 --out samsung_kpi

  python3 moving_targets_detector.py \
    --transcripts nvda_q1.txt nvda_q2.txt nvda_q3.txt nvda_q4.txt \
    --quarters "FY24Q1" "FY24Q2" "FY24Q3" "FY24Q4" \
    --lang en --company NVIDIA --out nvda_kpi
"""

import argparse
import json
import re
import sys
from pathlib import Path


KPI_DICT_EN = {
    "Revenue": [r"\brevenue\b", r"\bnet revenue\b"],
    "Gross Margin": [r"\bgross margin\b", r"\bgross profit\b"],
    "Operating Income": [r"\boperating income\b", r"\boperating profit\b", r"\bEBIT\b"],
    "EBITDA": [r"\bEBITDA\b"],
    "EPS": [r"\bearnings per share\b", r"\bEPS\b"],
    "Free Cash Flow": [r"\bfree cash flow\b", r"\bFCF\b"],
    "Data Center": [r"\bdata center\b", r"\bdatacenter\b"],
    "Cloud": [r"\bcloud (revenue|segment|business)\b"],
    "AI": [r"\bAI (revenue|growth|demand|orders)\b"],
    "Backlog": [r"\bbacklog\b", r"\border backlog\b"],
    "NRR": [r"\bnet revenue retention\b", r"\bNRR\b"],
    "ARR": [r"\bannual recurring revenue\b", r"\bARR\b"],
    "DAU/MAU": [r"\bdaily active\b", r"\bmonthly active\b", r"\bDAU\b", r"\bMAU\b"],
    "Inventory": [r"\binventory\b", r"\bdays of inventory\b"],
    "Guidance": [r"\bguidance\b", r"\boutlook\b"],
    "HBM": [r"\bHBM\b", r"\bhigh bandwidth memory\b"],
    "CUDA": [r"\bCUDA\b"],
    "CapEx": [r"\bcapital expenditure\b", r"\bcapex\b", r"\bCapEx\b"],
    "Buyback": [r"\bshare repurchase\b", r"\bbuyback\b"],
    "Dividend": [r"\bdividend\b"],
}

KPI_DICT_KO = {
    "매출": [r"매출(액|이)?", r"순매출"],
    "영업이익": [r"영업이익", r"영업 이익"],
    "순이익": [r"순이익", r"당기순이익"],
    "매출총이익": [r"매출총이익", r"GP마진", r"그로스마진"],
    "EBITDA": [r"EBITDA", r"에비타"],
    "EPS": [r"주당\s*(순)?이익", r"EPS"],
    "잉여현금흐름": [r"잉여현금흐름", r"FCF"],
    "HBM": [r"HBM", r"고대역폭메모리"],
    "DRAM": [r"DRAM", r"디램"],
    "NAND": [r"NAND", r"낸드"],
    "파운드리": [r"파운드리", r"위탁생산"],
    "데이터센터": [r"데이터\s*센터"],
    "AI": [r"AI (매출|성장|수요)", r"인공지능.*?(매출|성장)"],
    "수주잔고": [r"수주\s*잔고", r"백로그"],
    "가동률": [r"가동률"],
    "재고": [r"재고(일수|수준|현황)?"],
    "가이던스": [r"가이던스", r"전망"],
    "자사주": [r"자사주\s*(매입|소각)"],
    "배당": [r"배당(금|수익률)?"],
    "점유율": [r"시장\s*점유율", r"점유율"],
    "수율": [r"수율"],
    "CapEx": [r"설비투자", r"CapEx"],
}


def count_kpi(text: str, kpi_dict: dict, lang: str = "en") -> dict[str, int]:
    flags = re.IGNORECASE if lang == "en" else 0
    counts = {}
    for kpi, patterns in kpi_dict.items():
        total = sum(len(re.findall(pat, text, flags)) for pat in patterns)
        counts[kpi] = total
    return counts


def detect_moving(quarter_counts: list[dict], quarters: list[str]) -> list[dict]:
    all_kpis = set(k for qc in quarter_counts for k in qc)
    moving = []
    for kpi in sorted(all_kpis):
        freq = [qc.get(kpi, 0) for qc in quarter_counts]
        if max(freq) == 0:
            continue
        changes = []
        for i in range(1, len(freq)):
            prev, curr = freq[i-1], freq[i]
            pct = (curr - prev) / prev * 100 if prev > 0 else (100.0 if curr > 0 else 0.0)
            changes.append(pct)
        if changes and abs(changes[-1]) >= 50 and max(freq[:-1]) >= 2:
            direction = "급락 (회피 의심)" if changes[-1] <= -50 else "급등 (강조 전환)"
            moving.append({
                "kpi": kpi, "freq_series": freq, "quarters": quarters,
                "last_pct_change": round(changes[-1], 1),
                "direction": direction, "flag": changes[-1] <= -50,
            })
    return sorted(moving, key=lambda x: x["last_pct_change"])


def render_chart(kpi_data: list[dict], quarters: list[str], out_path: Path):
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("plotly 미설치 (차트 생략):\n  pip3 install plotly --break-system-packages", file=sys.stderr)
        return
    fig = go.Figure()
    for item in kpi_data[:15]:
        fig.add_trace(go.Scatter(
            x=quarters, y=item["freq_series"], mode="lines+markers", name=item["kpi"],
            line=dict(width=3 if item.get("flag") else 1.5), marker=dict(size=8),
        ))
    fig.update_layout(title="KPI 언급 빈도 추이 (Moving Targets 분석)",
                      xaxis_title="분기", yaxis_title="언급 횟수", height=600)
    html_path = out_path.with_suffix(".html")
    fig.write_html(str(html_path))
    print(f"  차트: {html_path}")


def render_markdown(moving: list[dict], quarter_counts: list[dict], quarters: list[str],
                    company: str, lang: str) -> str:
    lines = [
        f"# KPI 이동 (Moving Targets) 분석: {company}",
        "", f"분기: {', '.join(quarters)} / 언어: {'한국어' if lang == 'ko' else '영어'}",
        "", "---", "", "## Moving Target 감지 결과", "",
    ]
    if not moving:
        lines.append("**감지된 Moving Target 없음** — KPI 일관성 양호")
    else:
        lines += ["| KPI | " + " | ".join(quarters) + " | 변화% | 판정 |",
                  "|-----|" + "----|" * len(quarters) + "-----|------|"]
        for item in moving:
            freq_cols = " | ".join(str(f) for f in item["freq_series"])
            lines.append(f"| {item['kpi']} | {freq_cols} | {item['last_pct_change']:+.1f}% | {item['direction']} |")

    all_kpis = sorted(
        set(k for qc in quarter_counts for k in qc if qc.get(k, 0) > 0),
        key=lambda k: -max(qc.get(k, 0) for qc in quarter_counts),
    )
    lines += ["", "---", "", "## 전체 KPI 언급 빈도표", "",
              "| KPI | " + " | ".join(quarters) + " |",
              "|-----|" + "----|" * len(quarters)]
    for kpi in all_kpis[:30]:
        row = " | ".join(str(qc.get(kpi, 0)) for qc in quarter_counts)
        lines.append(f"| {kpi} | {row} |")

    flagged = [m["kpi"] for m in moving if m.get("flag")]
    lines += ["", "---", "",
              f"**Moving Target 적신호**: {'있음 -- ' + ', '.join(flagged) if flagged else '없음'}",
              "", "-> earnings_qna_redflag_checklist.md §3 및 management_credibility_scorecard.md §3에 반영"]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="컨퍼런스콜 KPI 이동 감지")
    parser.add_argument("--transcripts", nargs="+", required=True)
    parser.add_argument("--quarters", nargs="+", required=True)
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument("--company", default="Unknown")
    parser.add_argument("--out", default="kpi_result")
    parser.add_argument("--no-chart", action="store_true")
    args = parser.parse_args()

    if len(args.transcripts) != len(args.quarters):
        print("--transcripts 와 --quarters 수가 일치해야 합니다.", file=sys.stderr); sys.exit(1)

    kpi_dict = KPI_DICT_KO if args.lang == "ko" else KPI_DICT_EN
    quarter_counts = []
    for tf, qname in zip(args.transcripts, args.quarters):
        path = Path(tf)
        if not path.exists():
            print(f"파일 없음: {path}", file=sys.stderr); sys.exit(1)
        counts = count_kpi(path.read_text(encoding="utf-8"), kpi_dict, args.lang)
        quarter_counts.append(counts)
        print(f"  {qname}: {sum(counts.values())} 총 언급")

    moving = detect_moving(quarter_counts, args.quarters)
    out_dir = Path(args.out).parent
    out_stem = Path(args.out).name
    payload = {"company": args.company, "quarters": args.quarters, "lang": args.lang,
               "quarter_counts": quarter_counts, "moving_targets": moving}
    (out_dir / f"{out_stem}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / f"{out_stem}.md").write_text(
        render_markdown(moving, quarter_counts, args.quarters, args.company, args.lang), encoding="utf-8")
    if not args.no_chart:
        render_chart(moving, args.quarters, out_dir / f"{out_stem}_chart")

    flagged = [m["kpi"] for m in moving if m.get("flag")]
    print(f"Moving Target 적신호: {len(flagged)}건")
    for kpi in flagged:
        print(f"  - {kpi}")
    print(f"결과: {out_dir / out_stem}.json / .md")


if __name__ == "__main__":
    main()

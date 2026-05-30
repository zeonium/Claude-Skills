#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tone Analysis — 컨퍼런스콜 어조 분석 (EN: Loughran-McDonald / KO: KR-FinBert)

목적:
  실적발표 컨퍼런스콜 Q&A 텍스트에서 경영진의 언어 패턴을 분석합니다.
  - EN: Loughran-McDonald (LM) 금융 감성 사전 기반 단어 카운팅
  - KO: KR-FinBert 기반 문장 수준 감성 분류
  - 공통: 책임귀속 패턴, 모호 형용사, 과도한 낙관, 방어적 표현 탐지

의존성 설치:
  pip3 install transformers torch --break-system-packages    # KO: KR-FinBert
  pip3 install requests --break-system-packages              # LM 사전 다운로드

사용 예시:
  python3 tone_analysis.py --input transcript_nvda_q4.txt --lang en --out nvda_tone
  python3 tone_analysis.py --input transcript_samsung_q4.txt --lang ko --out samsung_tone
"""

import argparse
import json
import re
import sys
from pathlib import Path


EXTERNAL_BLAME_EN = [
    r"\b(macro|macroeconomic)\b",
    r"\b(supply chain|supply-chain)\b",
    r"\b(currency|exchange rate|forex)\b",
    r"\b(geopolit\w+)\b",
    r"\b(industry-wide|sector-wide)\b",
    r"\b(regulatory|regulation)\b.*\b(impact|headwind)\b",
    r"\b(tariff|trade war)\b",
    r"\bseasonal\b.*\b(factor|impact|effect)\b",
]

EXTERNAL_BLAME_KO = [
    r"(거시경제|매크로)",
    r"(공급망|서플라이체인)",
    r"(환율|외환)",
    r"(지정학|지정학적)",
    r"(업황|업계 전반)",
    r"(규제|제도).*?(영향|충격)",
    r"(계절적|비수기).*?(요인|영향)",
    r"(글로벌 불확실|대외 환경)",
]

VAGUE_ADJ_EN = [
    "robust", "solid", "healthy", "strong", "significant", "meaningful",
    "substantial", "considerable", "notable", "encouraging", "promising",
    "positive", "favorable", "constructive", "comfortable",
]

VAGUE_ADJ_KO = [
    "견조", "양호", "건전", "강건", "긍정적", "우호적",
    "충분", "상당", "유의미", "고무적", "탄탄", "안정적", "회복세",
]

OVER_OPT_EN = [
    r"\b(best ever|record-breaking|unprecedented growth|all-time high)\b",
    r"\b(exceptional|outstanding|phenomenal|extraordinary)\b.*\b(result|performance|quarter)\b",
]

OVER_OPT_KO = [
    r"(역대 최고|사상 최대|전례 없는 성장)",
    r"(뛰어난|탁월한|놀라운).*?(실적|성과|분기)",
]

DEFENSIVE_EN = [
    r"\b(challenging|difficult|headwind|uncertain|volatile)\b",
    r"\b(cautious|conservative|prudent)\b.*\b(outlook|guidance|approach)\b",
    r"\b(monitor|watch)\b.*\b(closely|carefully)\b",
    r"good question",
    r"\b(not going to|won't)\b.*\b(provide|give)\b.*\b(guidance|specific)\b",
]

DEFENSIVE_KO = [
    r"(어려운|도전적인|불확실한).*?(환경|상황|시장)",
    r"(보수적|신중하게|조심스럽게).*?(바라보|전망)",
    r"(면밀히|주의 깊게).*?(모니터링|지켜보)",
    r"(좋은 질문|훌륭한 질문)",
    r"(구체적인 수치|가이던스).*?(어렵)",
]


def find_matches(text: str, patterns: list[str]) -> list[str]:
    found = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            found.append(m.group(0))
    return found


def load_lm_subset() -> dict:
    return {
        "Negative": {
            "loss", "losses", "failed", "failure", "adverse", "adversely",
            "impair", "impairment", "deficit", "defaulted", "unable", "inability",
            "decline", "declined", "decrease", "deterioration", "weak", "weakened",
            "uncertain", "uncertainty", "risk", "risks", "volatility", "volatile",
            "challenging", "difficult", "headwind", "concern", "concerns",
        },
        "Positive": {
            "growth", "increase", "improved", "improvement", "strong", "strength",
            "exceeded", "record", "profitable", "profitability", "gain", "gains",
            "efficient", "efficiency", "innovative", "innovation", "leading",
            "outstanding", "exceptional", "robust", "solid", "positive",
        },
        "Uncertainty": {
            "may", "might", "could", "possibly", "uncertain", "uncertainty",
            "approximately", "estimate", "estimates", "forecast", "unclear",
        },
        "Litigious": {
            "claim", "claims", "lawsuit", "litigation", "legal", "court",
            "judgment", "alleged", "complaint", "plaintiff", "defendant",
        },
        "ModalWeak": {"could", "should", "might", "may", "can", "would"},
        "ModalStrong": {"will", "must", "shall", "need", "require", "required"},
    }


def analyze_lm(text: str, lm_dict: dict) -> dict:
    words = re.findall(r"\b[a-z]+\b", text.lower())
    counts = {cat: 0 for cat in lm_dict}
    matched = {cat: [] for cat in lm_dict}
    for w in words:
        for cat, word_set in lm_dict.items():
            if w in word_set:
                counts[cat] += 1
                matched[cat].append(w)
    return {"counts": counts, "matched": {k: list(set(v)) for k, v in matched.items()}}


def analyze_kr_finbert(sentences: list[str]) -> list[dict]:
    try:
        from transformers import pipeline
    except ImportError:
        print("transformers 미설치:\n  pip3 install transformers torch --break-system-packages", file=sys.stderr)
        sys.exit(1)
    print("  KR-FinBert 모델 로드 중...")
    try:
        clf = pipeline("text-classification", model="snunlp/KR-FinBert-SC",
                       tokenizer="snunlp/KR-FinBert-SC", truncation=True, max_length=512)
    except Exception as e:
        print(f"  KR-FinBert 로드 실패: {e}\n  규칙 기반 분석만 사용합니다.", file=sys.stderr)
        return []
    results = []
    for sent in sentences[:200]:
        if len(sent.strip()) < 10:
            continue
        try:
            out = clf(sent)[0]
            results.append({"text": sent[:120], "label": out["label"], "score": round(out["score"], 4)})
        except Exception:
            pass
    return results


def compute_tone(results: dict) -> str:
    ext = len(results.get("external_blame", []))
    def_cnt = len(results.get("defensive", []))
    pos = results.get("lm", {}).get("counts", {}).get("Positive", 0)
    neg = results.get("lm", {}).get("counts", {}).get("Negative", 0)
    opt = len(results.get("over_optimism", []))
    if def_cnt >= 5 or ext >= 7:
        return "방어적"
    if pos > neg * 2 and opt >= 3:
        return "과도한 낙관"
    return "중립/사실 위주"


def render_markdown(results: dict, company: str, lang: str, src: str) -> str:
    lines = [
        f"# 어조 분석 결과: {company}",
        "",
        f"언어: {'한국어 (KR-FinBert + 규칙)' if lang == 'ko' else '영어 (Loughran-McDonald + 규칙)'}",
        f"Source: {src}",
        "",
        "---",
        "",
        "## 언어 패턴 분석",
        "",
        "| 패턴 | 건수 | 예시 (최대 3개) |",
        "|------|------|----------------|",
    ]
    for name, key in [("모호한 형용사", "vague_adj"), ("책임귀속 (외부 탓)", "external_blame"),
                       ("과도한 낙관", "over_optimism"), ("방어적 표현", "defensive")]:
        items = results.get(key, [])
        ex = " / ".join(str(x)[:40] for x in items[:3])
        lines.append(f"| {name} | {len(items)} | {ex} |")

    if lang == "en" and "lm" in results:
        lm = results["lm"]
        lines += ["", "### Loughran-McDonald 단어 빈도", "",
                  "| 카테고리 | 건수 | 대표 단어 |", "|---------|------|---------|"]
        for cat, cnt in lm.get("counts", {}).items():
            words = ", ".join(lm["matched"].get(cat, [])[:5])
            lines.append(f"| {cat} | {cnt} | {words} |")

    if lang == "ko" and results.get("finbert_results"):
        neg_s = [r for r in results["finbert_results"] if "neg" in r["label"].lower() or "부정" in r["label"]]
        pos_s = [r for r in results["finbert_results"] if "pos" in r["label"].lower() or "긍정" in r["label"]]
        lines += ["", f"### KR-FinBert (분석: {len(results['finbert_results'])}문장)",
                  "", f"- 긍정: {len(pos_s)}건 / 부정: {len(neg_s)}건", "", "**부정 예시:**"]
        for item in neg_s[:5]:
            lines.append(f"- [{item['score']:.2f}] {item['text']}")

    tone = compute_tone(results)
    lines += ["", "---", "", f"**어조 판정**: {tone}",
              "", "-> D1 경영진 신뢰도 스코어카드 §2 어조 분석 반영"]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="컨퍼런스콜 어조 분석 (EN/KO)")
    parser.add_argument("--input", required=True)
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument("--company", default="Unknown")
    parser.add_argument("--out", default="tone_result")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"파일 없음: {src}", file=sys.stderr); sys.exit(1)

    text = src.read_text(encoding="utf-8")
    lang = args.lang

    blame_p = EXTERNAL_BLAME_EN if lang == "en" else EXTERNAL_BLAME_KO
    vague_p = VAGUE_ADJ_EN if lang == "en" else VAGUE_ADJ_KO
    opt_p = OVER_OPT_EN if lang == "en" else OVER_OPT_KO
    def_p = DEFENSIVE_EN if lang == "en" else DEFENSIVE_KO

    results = {
        "external_blame": find_matches(text, blame_p),
        "vague_adj": [w for w in vague_p if re.search(r"\b" + re.escape(w) + r"\b", text, re.IGNORECASE)],
        "over_optimism": find_matches(text, opt_p),
        "defensive": find_matches(text, def_p),
    }

    if lang == "en":
        results["lm"] = analyze_lm(text, load_lm_subset())
        results["finbert_results"] = []
    else:
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 15]
        results["finbert_results"] = analyze_kr_finbert(sents)
        results["lm"] = {}

    out_dir = Path(args.out).parent
    out_stem = Path(args.out).name
    (out_dir / f"{out_stem}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / f"{out_stem}.md").write_text(render_markdown(results, args.company, lang, str(src)), encoding="utf-8")

    tone = compute_tone(results)
    print(f"어조 판정: {tone}")
    print(f"외부탓: {len(results['external_blame'])}건 | 모호형용사: {len(results['vague_adj'])}건 | "
          f"방어적: {len(results['defensive'])}건 | 과도낙관: {len(results['over_optimism'])}건")
    print(f"결과: {out_dir / out_stem}.json / .md")


if __name__ == "__main__":
    main()

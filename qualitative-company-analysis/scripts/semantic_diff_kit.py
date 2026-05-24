#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Diff Kit — 공시 텍스트 YoY 의미론적 차이 분석 (KR/EN)

목적:
  두 연도의 사업보고서 위험요인(Item 1A / 사업위험) 텍스트를 비교하여
  신규 추가, 삭제, 표현 강도 변화를 코사인 유사도 기반으로 탐지합니다.
  결과는 disclosure_diff_report.md 양식에 맞춘 Markdown과 JSON으로 출력됩니다.

의존성 설치:
  pip3 install sentence-transformers scikit-learn numpy --break-system-packages

사용 예시:
  python3 semantic_diff_kit.py --prev nvda_2023_item1a.txt --curr nvda_2024_item1a.txt --lang en --out nvda_diff
  python3 semantic_diff_kit.py --prev samsung_2023_risk.txt --curr samsung_2024_risk.txt --lang ko --out samsung_diff
"""

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_sentences(text: str, lang: str) -> list[str]:
    """문장 분리: 한국어(ko)는 마침표·느낌표·물음표 기준, 영어(en)는 약어 보정"""
    if lang == "ko":
        raw = re.split(r"(?<=[.!?])\s+", text.strip())
    else:
        raw = re.split(r"(?<!\b(?:Mr|Dr|vs|etc|No|pp|Fig))\.\s+(?=[A-Z])", text.strip())
    return [s.strip() for s in raw if len(s.strip()) > 20]


def get_embeddings(sentences: list[str], model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print(
            "sentence-transformers 미설치:\n"
            "  pip3 install sentence-transformers --break-system-packages",
            file=sys.stderr,
        )
        sys.exit(1)
    model = SentenceTransformer(model_name)
    return model.encode(sentences, normalize_embeddings=True, show_progress_bar=True)


def cosine_matrix(a, b):
    return np.dot(a, b.T)


HEDGING_UP = [
    ("may adversely affect", "will adversely affect"),
    ("could adversely", "will adversely"),
    ("significant competition", "intense competition"),
    ("may not be able", "will not be able"),
    ("uncertain", "highly uncertain"),
    ("risk", "material risk"),
    ("불확실", "고도로 불확실"),
    ("영향을 미칠 수 있", "영향을 미칠 것"),
    ("위험이 있", "위험이 높"),
]

HEDGING_DOWN = [
    ("will adversely", "may adversely"),
    ("highly uncertain", "uncertain"),
]


def detect_hedging_shift(prev_sent: str, curr_sent: str) -> str | None:
    for before, after in HEDGING_UP:
        if before.lower() in prev_sent.lower() and after.lower() in curr_sent.lower():
            return f"강화  '{before}' -> '{after}'"
    for before, after in HEDGING_DOWN:
        if before.lower() in prev_sent.lower() and after.lower() in curr_sent.lower():
            return f"완화  '{before}' -> '{after}'"
    return None


def run_diff(
    prev_sentences: list[str],
    curr_sentences: list[str],
    threshold_new: float = 0.65,
    threshold_boilerplate: float = 0.95,
    model_name: str = "all-MiniLM-L6-v2",
) -> dict:
    prev_emb = get_embeddings(prev_sentences, model_name)
    curr_emb = get_embeddings(curr_sentences, model_name)

    sim_matrix = cosine_matrix(curr_emb, prev_emb)

    curr_max_sim = sim_matrix.max(axis=1)
    new_sentences = [
        {"idx": i, "text": curr_sentences[i], "max_cos": float(curr_max_sim[i])}
        for i in range(len(curr_sentences))
        if curr_max_sim[i] < threshold_new
    ]

    prev_max_sim = sim_matrix.max(axis=0)
    deleted_sentences = [
        {"idx": i, "text": prev_sentences[i], "max_cos": float(prev_max_sim[i])}
        for i in range(len(prev_sentences))
        if prev_max_sim[i] < threshold_new
    ]

    boilerplate_count = int((curr_max_sim >= threshold_boilerplate).sum())
    boilerplate_ratio = boilerplate_count / len(curr_sentences) if curr_sentences else 0.0
    avg_cos = float(curr_max_sim.mean())

    hedging_changes = []
    for ci in range(len(curr_sentences)):
        best_pi = int(sim_matrix[ci].argmax())
        cos_val = float(sim_matrix[ci, best_pi])
        if threshold_new <= cos_val < threshold_boilerplate:
            shift = detect_hedging_shift(prev_sentences[best_pi], curr_sentences[ci])
            if shift:
                hedging_changes.append(
                    {"prev": prev_sentences[best_pi], "curr": curr_sentences[ci], "cos": cos_val, "shift": shift}
                )

    return {
        "prev_count": len(prev_sentences),
        "curr_count": len(curr_sentences),
        "avg_cos": avg_cos,
        "new_count": len(new_sentences),
        "deleted_count": len(deleted_sentences),
        "boilerplate_ratio": boilerplate_ratio,
        "new_sentences": new_sentences,
        "deleted_sentences": deleted_sentences,
        "hedging_changes": hedging_changes,
    }


def severity_label(cos: float) -> str:
    if cos < 0.30:
        return "상"
    elif cos < 0.50:
        return "중"
    return "하"


def change_level(avg_cos: float) -> str:
    if avg_cos >= 0.85:
        return "소폭 (cos >= 0.85)"
    elif avg_cos >= 0.70:
        return "유의미 (0.70~0.85)"
    return "큰 변화 (< 0.70)"


def render_markdown(result: dict, prev_path: str, curr_path: str, company: str) -> str:
    r = result
    lines = [
        f"# 공시 위험요인 Diff 리포트: {company}",
        "",
        f"이전 문서: `{prev_path}`",
        f"현재 문서: `{curr_path}`",
        "",
        "---",
        "",
        "## 1. 분석 요약",
        "",
        "| 항목 | 값 |",
        "|------|---|",
        f"| 이전 문서 문장 수 | {r['prev_count']} |",
        f"| 현재 문서 문장 수 | {r['curr_count']} |",
        f"| **평균 코사인 유사도** | **{r['avg_cos']:.3f}** |",
        f"| 신규 추가 문장 수 | {r['new_count']} |",
        f"| 삭제된 문장 수 | {r['deleted_count']} |",
        f"| Boilerplate 추정 비율 | {r['boilerplate_ratio']*100:.1f}% (cos > 0.95) |",
        "",
        f"**변화 수준**: {change_level(r['avg_cos'])}",
        "",
        "---",
        "",
        "## 2. 신규 추가된 위험요인 (상위 10개, cos 낮은 순)",
        "",
        "| # | 신규 문장 (요약, 100자) | cos sim | 심각도 |",
        "|---|------------------------|---------|--------|",
    ]
    for i, item in enumerate(sorted(r["new_sentences"], key=lambda x: x["max_cos"])[:10], 1):
        summary = item["text"][:100].replace("|", "｜")
        lines.append(f"| {i} | {summary} | {item['max_cos']:.3f} | {severity_label(item['max_cos'])} |")

    lines += [
        "", "---", "",
        "## 3. 삭제된 위험요인 (상위 10개, cos 낮은 순)",
        "",
        "| # | 삭제된 문장 (요약, 100자) | cos sim | 삭제 사유 추정 |",
        "|---|--------------------------|---------|--------------|",
    ]
    for i, item in enumerate(sorted(r["deleted_sentences"], key=lambda x: x["max_cos"])[:10], 1):
        summary = item["text"][:100].replace("|", "｜")
        lines.append(f"| {i} | {summary} | {item['max_cos']:.3f} | 해소/은폐 추정 |")

    lines += [
        "", "---", "",
        "## 4. 표현 강도 변화",
        "",
        "| 이전 표현 (100자) | 현재 표현 (100자) | cos | 변화 방향 |",
        "|-------------------|-------------------|-----|----------|",
    ]
    for item in r["hedging_changes"][:10]:
        p = item["prev"][:100].replace("|", "｜")
        c = item["curr"][:100].replace("|", "｜")
        lines.append(f"| {p} | {c} | {item['cos']:.3f} | {item['shift']} |")

    lines += [
        "", "---", "",
        "## 5. Boilerplate 비율",
        "",
        f"- Boilerplate (cos > 0.95) 비율: **{r['boilerplate_ratio']*100:.1f}%**",
        "- 50% 초과 -> 공시 투명성 저하 (D3 점수 하향 요인)",
        "- 40% 미만 -> 실질적 업데이트 (D3 점수 상향 요인)",
        "",
        "---",
        "",
        f"[Source: {prev_path} / {curr_path} — semantic_diff_kit.py]",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="공시 텍스트 YoY Semantic Diff 분석 (KR/EN)")
    parser.add_argument("--prev", required=True, help="이전 연도 텍스트 파일 경로")
    parser.add_argument("--curr", required=True, help="현재 연도 텍스트 파일 경로")
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument("--company", default="Unknown")
    parser.add_argument("--out", default="diff_result")
    parser.add_argument("--model", default=None)
    parser.add_argument("--threshold-new", type=float, default=0.65)
    args = parser.parse_args()

    prev_path = Path(args.prev)
    curr_path = Path(args.curr)
    if not prev_path.exists():
        print(f"파일 없음: {prev_path}", file=sys.stderr); sys.exit(1)
    if not curr_path.exists():
        print(f"파일 없음: {curr_path}", file=sys.stderr); sys.exit(1)

    model_name = args.model or ("jhgan/ko-sroberta-multitask" if args.lang == "ko" else "all-MiniLM-L6-v2")

    print(f"[1/3] 텍스트 로드 및 문장 분리 (lang={args.lang})")
    prev_sents = split_sentences(load_text(prev_path), args.lang)
    curr_sents = split_sentences(load_text(curr_path), args.lang)
    print(f"      이전: {len(prev_sents)}문장 / 현재: {len(curr_sents)}문장")

    print(f"[2/3] 임베딩 생성 (model={model_name})")
    result = run_diff(prev_sents, curr_sents, threshold_new=args.threshold_new, model_name=model_name)

    print("[3/3] 결과 저장")
    out_dir = Path(args.out).parent
    out_stem = Path(args.out).name
    json_path = out_dir / f"{out_stem}.json"
    md_path = out_dir / f"{out_stem}.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(result, str(prev_path), str(curr_path), args.company), encoding="utf-8")

    print(f"\n결과: avg_cos={result['avg_cos']:.3f}, 신규={result['new_count']}건, "
          f"삭제={result['deleted_count']}건, Boilerplate={result['boilerplate_ratio']*100:.1f}%")
    print(f"  JSON: {json_path}\n  MD  : {md_path}")


if __name__ == "__main__":
    main()

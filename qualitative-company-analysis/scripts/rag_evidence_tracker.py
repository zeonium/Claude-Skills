#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Evidence Tracker — 주장-원문 매핑 및 AI 환각 검출

목적:
  Claude가 생성한 분석 보고서의 각 주장(claim)이 실제 원문 코퍼스에서
  뒷받침되는지 코사인 유사도로 검증합니다.
  cos < 0.70인 주장은 "환각 의심"으로 플래그합니다.
  결과는 investment_memo.md §6 Evidence Trail에 반영합니다.

의존성 설치:
  pip3 install sentence-transformers numpy --break-system-packages

사용 예시:
  python3 rag_evidence_tracker.py \
    --claims claims.txt \
    --corpus 10k_item1.txt conference_call.txt \
    --company NVIDIA --out nvda_evidence

  python3 rag_evidence_tracker.py \
    --claims samsung_claims.txt \
    --corpus dart_business_report.txt \
    --lang ko --company 삼성전자 --out samsung_evidence
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HALLUCINATION_THRESHOLD = 0.70
STRONG_EVIDENCE_THRESHOLD = 0.85


def load_chunks(paths: list[Path]) -> list[tuple[str, str]]:
    chunks = []
    for p in paths:
        text = p.read_text(encoding="utf-8")
        sentences = [s.strip() for s in text.replace("\n", " ").split(". ") if len(s.strip()) > 20]
        for sent in sentences:
            chunks.append((p.name, sent))
    return chunks


def load_claims(path: Path) -> list[str]:
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


def get_embeddings(texts: list[str], model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("sentence-transformers 미설치:\n  pip3 install sentence-transformers --break-system-packages",
              file=sys.stderr)
        sys.exit(1)
    model = SentenceTransformer(model_name)
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=True)


def find_evidence(claim_emb, corpus_embs, corpus_chunks: list[tuple[str, str]], top_k: int = 3) -> list[dict]:
    sims = np.dot(claim_emb, corpus_embs.T)
    top_idx = sims.argsort()[::-1][:top_k]
    return [{"source": corpus_chunks[i][0], "text": corpus_chunks[i][1][:200], "cos": float(sims[i])}
            for i in top_idx]


def verdict(cos: float) -> str:
    if cos >= STRONG_EVIDENCE_THRESHOLD:
        return "강한 근거"
    elif cos >= HALLUCINATION_THRESHOLD:
        return "약한 근거 (추가 확인 권장)"
    return "환각 의심 (원문 미확인)"


def render_markdown(results: list[dict], company: str) -> str:
    hallucination_count = sum(1 for r in results if r["best_cos"] < HALLUCINATION_THRESHOLD)
    weak_count = sum(1 for r in results if HALLUCINATION_THRESHOLD <= r["best_cos"] < STRONG_EVIDENCE_THRESHOLD)
    strong_count = sum(1 for r in results if r["best_cos"] >= STRONG_EVIDENCE_THRESHOLD)

    lines = [
        f"# RAG Evidence Trail: {company}",
        "",
        f"임계값: 환각 의심 < {HALLUCINATION_THRESHOLD} | 강한 근거 >= {STRONG_EVIDENCE_THRESHOLD}",
        "",
        "## 요약",
        "",
        f"| 판정 | 건수 |",
        f"|------|------|",
        f"| 강한 근거 (cos >= {STRONG_EVIDENCE_THRESHOLD}) | {strong_count} |",
        f"| 약한 근거 ({HALLUCINATION_THRESHOLD} <= cos < {STRONG_EVIDENCE_THRESHOLD}) | {weak_count} |",
        f"| 환각 의심 (cos < {HALLUCINATION_THRESHOLD}) | {hallucination_count} |",
        f"| **합계** | **{len(results)}** |",
        "",
        "---",
        "",
        "## 주장별 근거 검증",
        "",
    ]
    for i, r in enumerate(results, 1):
        lines += [
            f"### Claim {i}: {r['claim'][:120]}",
            "",
            f"**최고 유사도**: {r['best_cos']:.3f} — {verdict(r['best_cos'])}",
            "",
            "**근거 후보 (상위 3개):**",
            "",
        ]
        for j, ev in enumerate(r["evidence"], 1):
            lines += [f"{j}. [{ev['source']}] (cos={ev['cos']:.3f})", f"   > {ev['text'][:180]}", ""]
        lines.append("---")
        lines.append("")

    lines += ["## Investment Memo §6 Evidence Trail", "",
              "| # | 주장 (80자) | cos | 출처 | 판정 |",
              "|---|------------|-----|------|------|"]
    for i, r in enumerate(results, 1):
        claim_short = r["claim"][:80].replace("|", "｜")
        best_ev = r["evidence"][0] if r["evidence"] else {}
        source = best_ev.get("source", "-")
        v = verdict(r["best_cos"])
        lines.append(f"| {i} | {claim_short} | {r['best_cos']:.3f} | {source} | {v} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Investment Memo 주장-원문 매핑 및 AI 환각 검출")
    parser.add_argument("--claims", required=True, help="주장 목록 파일 (한 줄=한 주장)")
    parser.add_argument("--corpus", nargs="+", required=True, help="원문 코퍼스 파일들")
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument("--company", default="Unknown")
    parser.add_argument("--out", default="evidence_result")
    parser.add_argument("--model", default=None)
    parser.add_argument("--threshold", type=float, default=HALLUCINATION_THRESHOLD)
    args = parser.parse_args()

    claims_path = Path(args.claims)
    if not claims_path.exists():
        print(f"파일 없음: {claims_path}", file=sys.stderr); sys.exit(1)

    corpus_paths = [Path(p) for p in args.corpus]
    for cp in corpus_paths:
        if not cp.exists():
            print(f"코퍼스 파일 없음: {cp}", file=sys.stderr); sys.exit(1)

    model_name = args.model or ("jhgan/ko-sroberta-multitask" if args.lang == "ko" else "all-MiniLM-L6-v2")

    global HALLUCINATION_THRESHOLD
    HALLUCINATION_THRESHOLD = args.threshold

    print("[1/4] 주장 및 코퍼스 로드")
    claims = load_claims(claims_path)
    corpus_chunks = load_chunks(corpus_paths)
    print(f"  주장: {len(claims)}건 | 코퍼스 문장: {len(corpus_chunks)}개")

    if not claims:
        print("주장이 없습니다.", file=sys.stderr); sys.exit(1)

    print(f"[2/4] 임베딩 생성 (model={model_name})")
    claim_embs = get_embeddings(claims, model_name)
    corpus_embs = get_embeddings([c[1] for c in corpus_chunks], model_name)

    print("[3/4] 근거 매핑 및 환각 탐지")
    results = []
    for i, (claim, claim_emb) in enumerate(zip(claims, claim_embs)):
        evidence = find_evidence(claim_emb, corpus_embs, corpus_chunks)
        best_cos = evidence[0]["cos"] if evidence else 0.0
        results.append({"claim_no": i+1, "claim": claim, "best_cos": best_cos,
                         "verdict": verdict(best_cos), "evidence": evidence})

    print("[4/4] 결과 저장")
    out_dir = Path(args.out).parent
    out_stem = Path(args.out).name
    (out_dir / f"{out_stem}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / f"{out_stem}.md").write_text(render_markdown(results, args.company), encoding="utf-8")

    hallucination_count = sum(1 for r in results if r["best_cos"] < HALLUCINATION_THRESHOLD)
    print(f"\n환각 의심: {hallucination_count}/{len(results)}건")
    for r in results:
        flag = "환각의심" if r["best_cos"] < HALLUCINATION_THRESHOLD else ("약한근거" if r["best_cos"] < STRONG_EVIDENCE_THRESHOLD else "강한근거")
        print(f"  [{r['best_cos']:.3f}] {flag}: {r['claim'][:80]}")
    print(f"결과: {out_dir / out_stem}.json / .md")


if __name__ == "__main__":
    main()

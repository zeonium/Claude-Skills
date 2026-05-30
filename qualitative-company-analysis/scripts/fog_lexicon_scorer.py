#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOG Lexicon Scorer — Rittenhouse Net Candor Score 자동 채점기

목적:
  CEO 주주 서한·사장의 인사말·컨퍼런스콜 발언에서
  Rittenhouse (Investing Between the Lines, 2013) FOG 분류 + 가점 룰을 적용하여
  Net Candor Score / Candor Index / Communication Efficiency를 산출한다.

배점:
  +5  정성적 목표 ("we aim to improve / ~을 목표로")
  +10 정량적 목표 (숫자 + 기한 패턴)
  +5  목표 맥락 (측정 지표·달성 방안 동반)
  +3  Cash/Cash flow 언급
  +3  FCF 정의·맥락
  -3  상투어 (cliché)
  -3  위즐워드 (weasel word)
  -5  오웰적 자기모순 문장
  -10 전략적 부조화 (수동 입력)

사용:
  python3 fog_lexicon_scorer.py --input letter.txt --lang en --company NVIDIA --out nvda_fog
  python3 fog_lexicon_scorer.py --input letter.txt --lang ko --company 삼성전자 --out samsung_fog
  python3 fog_lexicon_scorer.py --input letter.txt --lang en --detect-enron-pattern --out check

옵션:
  --discord N  전략적 부조화 사례 수 수동 입력 (-10 × N)
  --no-md      Markdown 출력 생략
"""

import argparse
import json
import re
import sys
from pathlib import Path

# =========================================================
# 1. 위즐 워드 사전 (단어당 -3점)
# =========================================================

WEASEL_EN = [
    "solid", "robust", "momentum", "enhanced", "synergy", "synergies",
    "proactive", "optimize", "optimizing", "streamline", "streamlining",
    "best-in-class", "world-class", "transformative", "disruptive",
    "empower", "ecosystem", "journey", "meaningful", "significant",
    "substantial", "considerable", "leverage", "leveraging",
]

WEASEL_KO = [
    "견조한", "견고한", "양호한", "건전한", "긍정적인", "우호적인",
    "충분한", "상당한", "유의미한", "고무적인", "탄탄한", "안정적인",
    "회복세", "모멘텀", "시너지", "최적화", "선제적", "혁신적",
    "전략적",
]

# =========================================================
# 2. 상투어 사전 (문구당 -3점)
# =========================================================

CLICHES_EN = [
    r"talented people",
    r"our greatest asset[s]?",
    r"employees are our greatest assets",
    r"global presence",
    r"financial strength",
    r"significant value for (?:our )?shareholders",
    r"value creation for shareholders",
    r"our future is bright",
    r"customer[-\s]centric",
    r"customer[-\s]first",
    r"people[-\s]first",
    r"innovation engine",
    r"accelerate (?:their )?growth",
    r"transformation journey",
    r"massive market knowledge",
    r"deep expertise",
    r"world[-\s]class team",
    r"best[-\s]in[-\s]class platform",
    r"relentless focus on execution",
    r"unwavering commitment",
]

CLICHES_KO = [
    r"재능 있는 인재",
    r"우수한 인재",
    r"우리의 가장 큰 자산",
    r"직원은 우리의 가장 큰 자산",
    r"글로벌 입지",
    r"재무적 강점",
    r"주주 가치 창출",
    r"주주를 위한 상당한 가치",
    r"미래는 밝다",
    r"고객 중심",
    r"고객 우선",
    r"혁신 엔진",
    r"성장 가속화",
    r"변화의 여정",
    r"방대한 시장 지식",
    r"깊은 전문성",
    r"세계적인 팀",
    r"업계 최고",
    r"끊임없는 집중",
    r"흔들림 없는 헌신",
    r"끊임없는 노력",
    r"일류 기업",
    r"글로벌 리더",
]

# =========================================================
# 3. 오웰적 패턴 (문장당 -5점) — 정규식
# =========================================================

ORWELL_PATTERNS_EN = [
    # 자기모순: not material ... may be material
    r"(?:not material|immaterial)[^.]{1,80}(?:may be material|could be material)",
    r"(?:not significant)[^.]{1,80}(?:may be significant|could be significant)",
    # 이중부정
    r"\bnot (?:unconfident|unhappy|unaware|unlikely|uncomfortable)\b",
    # could potentially eventually
    r"(?:could|may|might) (?:potentially|possibly)[^.]{1,30}(?:eventually|perhaps)",
    # non-recurring ... recurring
    r"non[-\s]recurring[^.]{1,60}(?:recur|recurring|annually|every year)",
    # 수동태 책임 회피
    r"(?:errors|mistakes|decisions|losses) were (?:made|taken|incurred)",
    # 의미상쇄: strong ... despite headwinds (반복)
    r"(?:strong|robust|solid) (?:results|performance)[^.]{1,80}(?:despite|notwithstanding)[^.]{1,80}(?:headwinds|challenges|difficulties)",
    # we believe ... but ... uncertain
    r"\bwe believe\b[^.]{1,80}(?:however|but)[^.]{1,80}(?:uncertain|unclear|cannot predict)",
]

ORWELL_PATTERNS_KO = [
    r"중요하지 않을[^.。]{1,60}중요할 수[도있]",
    r"중대하지 않[다습][^.。]{1,60}중대할 수[도있]",
    r"믿[고으]나[^.。]{1,60}(?:불확실|장담할 수 없|예측할 수 없)",
    r"(?:오류|실수|손실|결정)(?:이|가) (?:발생|초래|이루어)(?:되었|졌)습니다",
    r"일회성[^.。]{1,60}(?:매년 발생|반복|지속)",
    r"(?:강[한건]|견고[한]|탄탄[한])\s*(?:실적|성과)[^.。]{1,80}(?:도전적|어려운|불확실한)[^.。]{1,60}(?:환경|상황)",
]

# =========================================================
# 4. 가점 패턴
# =========================================================

QUALITATIVE_GOAL_EN = [
    r"\bwe aim to (?:improve|increase|expand|grow|reduce|build)\b",
    r"\bour goal is to\b",
    r"\bwe (?:are committed|commit) to\b",
    r"\bwe plan to (?:expand|launch|grow|enter)\b",
    r"\bwe will (?:focus on|prioritize|invest in)\b",
]

QUALITATIVE_GOAL_KO = [
    r"개선을 목표",
    r"성장을 목표",
    r"확장을 목표",
    r"~?을 목표로 (?:한다|합니다|하겠)",
    r"(?:집중|전념)하(?:겠|고자)",
    r"(?:헌신|매진)하(?:겠|고자)",
]

# 정량적 목표: 숫자 + 기한 패턴
QUANT_GOAL_EN = [
    r"(?:grow|increase|reduce|achieve|target)[^.]{1,30}\b\d+(?:\.\d+)?\s*%",
    r"(?:target|goal) of\s+\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M|bn|mn)\b",
    r"\bby (?:FY|fiscal year )?(?:20)?\d{2,4}\b[^.]{1,30}(?:\d+(?:\.\d+)?\s*%|\$\d+)",
    r"\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M)[^.]{1,60}by (?:20)?\d{2,4}",
]

QUANT_GOAL_KO = [
    r"(?:매출|영업이익|EBITDA|점유율|마진)[^.。]{1,30}\d+(?:\.\d+)?%",
    r"(?:매출|영업이익|EBITDA)[^.。]{1,30}\d+(?:조|억)",
    r"(?:20\d{2}년|FY\d{2,4})까지[^.。]{1,40}(?:\d+(?:\.\d+)?%|\d+(?:조|억))",
    r"\d+(?:\.\d+)?% (?:이상|성장|증가)[^.。]{0,30}(?:20\d{2}|FY\d{2,4})",
]

# Cash / FCF 언급 (+3 단순 카운트)
CASH_KEYWORDS_EN = [
    r"\bcash flow\b",
    r"\bfree cash flow\b",
    r"\boperating cash flow\b",
    r"\bFCF\b",
]

CASH_KEYWORDS_KO = [
    r"현금흐름",
    r"잉여현금흐름",
    r"영업현금흐름",
    r"\bFCF\b",
]

# FCF 맥락 (+3) — 정의·5년대조·사용처
FCF_CONTEXT_EN = [
    r"free cash flow[^.]{1,80}(?:defined as|defined by|means|after maintenance)",
    r"(?:FCF|free cash flow)[^.]{1,80}(?:\$?\d+(?:\.\d+)?\s*(?:billion|B))[^.]{1,40}(?:in 20\d{2}|five years ago|5 years ago)",
    r"(?:FCF|free cash flow)[^.]{1,60}(?:returned to shareholders|share repurchase|dividend|buyback)",
    r"(?:maintenance capex|growth capex)[^.]{1,80}(?:separate|distinct|excluding)",
]

FCF_CONTEXT_KO = [
    r"잉여현금흐름[^.。]{1,80}(?:정의|즉|의미)",
    r"(?:FCF|잉여현금흐름)[^.。]{1,80}(?:20\d{2}년|5년 전)[^.。]{1,40}대비",
    r"(?:FCF|잉여현금흐름)[^.。]{1,60}(?:자사주|배당|환원)",
    r"(?:유지|성장)\s*(?:CapEx|자본지출)[^.。]{1,60}(?:분리|제외|구분)",
]

# 엔론 '독성 6종 세트' (한 문단에 4개 이상 동시 등장)
ENRON_TOXIC_6_EN = [
    "talented people", "global presence", "financial strength",
    "massive market knowledge", "synergy", "significant value",
]

ENRON_TOXIC_6_KO = [
    "재능 있는 인재", "글로벌 입지", "재무적 강점",
    "방대한 시장 지식", "시너지", "주주를 위한 상당한 가치",
]


# =========================================================
# 핵심 함수
# =========================================================

def count_word_list(text: str, words: list[str]) -> tuple[int, list[str]]:
    """단어 리스트 (대소문자 무시) 카운트 — 단어 경계 엄수."""
    matched = []
    for w in words:
        pat = r"(?<![\w가-힣])" + re.escape(w) + r"(?![\w가-힣])"
        for m in re.finditer(pat, text, re.IGNORECASE):
            matched.append(m.group(0))
    return len(matched), matched


def count_regex_list(text: str, patterns: list[str]) -> tuple[int, list[str]]:
    """정규식 패턴 리스트 카운트."""
    matched = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE | re.MULTILINE):
            matched.append(m.group(0)[:120])
    return len(matched), matched


def detect_enron_paragraph(text: str, lang: str) -> list[str]:
    """문단 단위에서 독성 6종 세트 중 4개 이상 동시 등장 탐지."""
    toxic = ENRON_TOXIC_6_EN if lang == "en" else ENRON_TOXIC_6_KO
    paragraphs = re.split(r"\n\s*\n", text)
    hits = []
    for i, p in enumerate(paragraphs):
        p_low = p.lower()
        present = [w for w in toxic if w.lower() in p_low]
        if len(present) >= 4:
            hits.append(f"문단 #{i+1}: {len(present)}개 동시 등장 — {', '.join(present)}")
    return hits


def compute_score(counts: dict) -> dict:
    """가점·감점·Net Candor Score 산출."""
    plus = (counts["qual_goal"] * 5
            + counts["quant_goal"] * 10
            + counts["goal_context"] * 5
            + counts["cash_kw"] * 3
            + counts["fcf_context"] * 3)
    minus = (counts["cliche"] * 3
             + counts["weasel"] * 3
             + counts["orwell"] * 5
             + counts["discord"] * 10)
    net = plus - minus
    fog_ratio = minus / (plus + minus) if (plus + minus) > 0 else 0.0
    candor_index = (1 - fog_ratio) * 100
    return {
        "plus": plus,
        "minus": minus,
        "net_candor_score": net,
        "fog_ratio": round(fog_ratio, 4),
        "candor_index": round(candor_index, 2),
    }


def classify(candor_index: float, net: int) -> str:
    if net < 0:
        return "위험 (Red Flag)"
    if candor_index >= 75:
        return "모범 (Best Practice)"
    if candor_index >= 50:
        return "경계 (Watch)"
    return "위험 (Red Flag)"


def render_markdown(results: dict, company: str, lang: str, src: str,
                    word_count: int, enron_hits: list[str]) -> str:
    s = results["scores"]
    c = results["counts"]
    lines = [
        f"# Net Candor Score 결과: {company}",
        "",
        f"언어: {'한국어' if lang == 'ko' else '영어'}",
        f"Source: {src}",
        f"총 단어 수: {word_count:,}",
        "",
        "---",
        "",
        "## 가점 / 감점 집계",
        "",
        "| 항목 | 단위점수 | 건수 | 소계 |",
        "|------|---------|------|------|",
        f"| 정성적 목표 | +5 | {c['qual_goal']} | +{c['qual_goal']*5} |",
        f"| 정량적 목표 | +10 | {c['quant_goal']} | +{c['quant_goal']*10} |",
        f"| 목표 맥락 | +5 | {c['goal_context']} | +{c['goal_context']*5} |",
        f"| Cash/FCF 언급 | +3 | {c['cash_kw']} | +{c['cash_kw']*3} |",
        f"| FCF 맥락 | +3 | {c['fcf_context']} | +{c['fcf_context']*3} |",
        f"| 상투어 | -3 | {c['cliche']} | -{c['cliche']*3} |",
        f"| 위즐워드 | -3 | {c['weasel']} | -{c['weasel']*3} |",
        f"| 오웰적 문장 | -5 | {c['orwell']} | -{c['orwell']*5} |",
        f"| 전략적 부조화 | -10 | {c['discord']} | -{c['discord']*10} |",
        "",
        "---",
        "",
        "## 종합 점수",
        "",
        f"- **가점 합**: {s['plus']}",
        f"- **감점 합**: {s['minus']}",
        f"- **Net Candor Score**: **{s['net_candor_score']}**",
        f"- **FOG 비율**: {s['fog_ratio']*100:.1f}%",
        f"- **Candor Index**: **{s['candor_index']:.1f}** / 100",
        f"- **Communication Efficiency**: {s['net_candor_score']/word_count:.4f} (단위: 단어당)",
        f"- **판정**: {classify(s['candor_index'], s['net_candor_score'])}",
        "",
    ]

    if enron_hits:
        lines += ["---", "", "## 엔론 '독성 6종 세트' 패턴 경보", ""]
        for h in enron_hits:
            lines.append(f"- {h}")
        lines.append("")

    if c["orwell"] > 0:
        lines += ["---", "", "## 오웰적 문장 예시 (최대 5개)", ""]
        for ex in results["matched"]["orwell"][:5]:
            lines.append(f"- {ex}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 후속 조치",
        "",
        "- D1 경영진 신뢰도 스코어카드 §CANDOR-7 통합 — Net Candor Score 섹션에 반영",
        "- Candor Index < 50: 자동 C등급 후보. Step 5 Investment Memo에서 강조.",
        "- Net Score (+) → (-) 전환 (전년 대비): 알림 트리거 발동.",
        "- 상세 해석: `references/candor7_framework.md`, `references/fog_lexicon.md`",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Rittenhouse Net Candor Score 자동 채점")
    parser.add_argument("--input", required=True, help="서한·인사말·콜 텍스트 파일")
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument("--company", default="Unknown")
    parser.add_argument("--out", default="fog_result")
    parser.add_argument("--discord", type=int, default=0,
                        help="전략적 부조화 사례 수 수동 입력 (-10 × N)")
    parser.add_argument("--detect-enron-pattern", action="store_true",
                        help="엔론 '독성 6종 세트' 한 문단 집중 탐지")
    parser.add_argument("--no-md", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"파일 없음: {src}", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8")
    word_count = len(re.findall(r"\S+", text))
    lang = args.lang

    # 사전 선택
    weasel = WEASEL_EN if lang == "en" else WEASEL_KO
    cliches = CLICHES_EN if lang == "en" else CLICHES_KO
    orwell = ORWELL_PATTERNS_EN if lang == "en" else ORWELL_PATTERNS_KO
    qual = QUALITATIVE_GOAL_EN if lang == "en" else QUALITATIVE_GOAL_KO
    quant = QUANT_GOAL_EN if lang == "en" else QUANT_GOAL_KO
    cash_kw = CASH_KEYWORDS_EN if lang == "en" else CASH_KEYWORDS_KO
    fcf_ctx = FCF_CONTEXT_EN if lang == "en" else FCF_CONTEXT_KO

    # 카운트
    weasel_cnt, weasel_m = count_word_list(text, weasel)
    cliche_cnt, cliche_m = count_regex_list(text, cliches)
    orwell_cnt, orwell_m = count_regex_list(text, orwell)
    qual_cnt, qual_m = count_regex_list(text, qual)
    quant_cnt, quant_m = count_regex_list(text, quant)
    cash_cnt, cash_m = count_regex_list(text, cash_kw)
    fcf_cnt, fcf_m = count_regex_list(text, fcf_ctx)

    # 목표 맥락(+5): 정성+정량 목표의 30%가 측정/방안 문구 동반한다고 보수 추정
    goal_context_cnt = int((qual_cnt + quant_cnt) * 0.3)

    counts = {
        "qual_goal": qual_cnt,
        "quant_goal": quant_cnt,
        "goal_context": goal_context_cnt,
        "cash_kw": cash_cnt,
        "fcf_context": fcf_cnt,
        "cliche": cliche_cnt,
        "weasel": weasel_cnt,
        "orwell": orwell_cnt,
        "discord": args.discord,
    }
    scores = compute_score(counts)

    enron_hits = []
    if args.detect_enron_pattern:
        enron_hits = detect_enron_paragraph(text, lang)

    results = {
        "company": args.company,
        "language": lang,
        "source": str(src),
        "word_count": word_count,
        "counts": counts,
        "scores": scores,
        "matched": {
            "weasel": weasel_m[:30],
            "cliche": cliche_m[:30],
            "orwell": orwell_m[:10],
            "qual_goal": qual_m[:20],
            "quant_goal": quant_m[:20],
            "cash_kw": cash_m[:30],
            "fcf_context": fcf_m[:20],
        },
        "enron_pattern_hits": enron_hits,
    }

    out_path = Path(args.out)
    out_dir = out_path.parent if str(out_path.parent) != "." else Path.cwd()
    out_stem = out_path.name
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / f"{out_stem}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if not args.no_md:
        md = render_markdown(results, args.company, lang, str(src), word_count, enron_hits)
        (out_dir / f"{out_stem}.md").write_text(md, encoding="utf-8")

    print(f"Net Candor Score: {scores['net_candor_score']}")
    print(f"Candor Index    : {scores['candor_index']:.1f} / 100  "
          f"({classify(scores['candor_index'], scores['net_candor_score'])})")
    print(f"FOG 비율        : {scores['fog_ratio']*100:.1f}%")
    print(f"가점 {scores['plus']} | 감점 {scores['minus']} | 단어수 {word_count:,}")
    if enron_hits:
        print(f"[ALERT] 엔론 6종 세트 패턴 {len(enron_hits)}건 감지!")
    print(f"결과: {out_dir / out_stem}.json / .md")


if __name__ == "__main__":
    main()

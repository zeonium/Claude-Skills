#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO Letter Forensics — Rittenhouse 5단계 포렌식 보조 진단기

목적:
  CEO 주주 서한에서 자기 집필도 / FCF 맥락 / 실수 대처법 / 오웰 모순을 진단한다.
  fog_lexicon_scorer.py와 함께 사용하면 7-시스템 레이더 자동 채점이 가능하다.

체크 항목:
  --check authorship  : 자기 집필도 (1인칭 빈도 + 일화 + 실수 인정)
  --check fcf         : FCF 맥락 평가 (정의·5년대조·사용처)
  --check mistake     : 실수 대처법 (인정 vs 외부 탓 비율)
  --check orwell      : 오웰 모순 패턴 별도 탐지
  --check all         : 모두 실행 (기본값)

사용:
  python3 ceo_letter_forensics.py --input letter.txt --lang en --check all --out result
  python3 ceo_letter_forensics.py --input letter.txt --lang ko --check fcf
"""

import argparse
import json
import re
import sys
from pathlib import Path


# =========================================================
# 1. 자기 집필도 (Authorship)
# =========================================================

FIRST_PERSON_EN = [r"\bI\b", r"\bI've\b", r"\bI'm\b", r"\bI'd\b",
                   r"\bmy\b", r"\bme\b", r"\bmyself\b"]
FIRST_PERSON_KO = [r"저(는|희|의|에게|와)?", r"나(는|의|에게|와)?", r"제(가|는|의)?"]

ANECDOTE_KEYWORDS_EN = [
    r"\blast (?:week|month|year)\b",
    r"\bI (?:remember|recall|saw|met|visited|talked|spoke)\b",
    r"\b(?:our|a) (?:customer|employee|partner) (?:told|said|wrote|emailed)\b",
    r"\bI was (?:at|in|visiting)\b",
    r"\b(?:walked|drove|flew) to (?:our|the)\b",
]

ANECDOTE_KEYWORDS_KO = [
    r"(?:지난주|지난달|작년|얼마 전)",
    r"제가 (?:기억|만났|봤|들었|방문)",
    r"(?:고객|직원|파트너)(?:이|가|께서) (?:말씀|이야기|전해)",
    r"(?:현장|매장|공장)을 (?:방문|찾았)",
]

# =========================================================
# 2. FCF 맥락
# =========================================================

FCF_DEFINITION_EN = [
    r"free cash flow[^.]{1,80}(?:defined as|defined by|means|is defined|after maintenance|after capex|less capex)",
    r"FCF[^.]{1,80}(?:defined as|defined by|means|is defined)",
]
FCF_DEFINITION_KO = [
    r"잉여현금흐름[^.。]{1,80}(?:정의|즉|의미|뜻하|는 것)",
    r"FCF[^.。]{1,80}(?:정의|즉|의미)",
]

FCF_FIVE_YEAR_EN = [
    r"(?:FCF|free cash flow)[^.]{1,120}(?:\$?\d+(?:\.\d+)?\s*(?:billion|B))[^.]{1,40}(?:in 20\d{2}|five years ago|5 years ago|since 20\d{2})",
    r"(?:five|5) years ago[^.]{1,80}(?:FCF|free cash flow)",
]
FCF_FIVE_YEAR_KO = [
    r"(?:FCF|잉여현금흐름)[^.。]{1,120}(?:5년 전|5년전|20\d{2}년)[^.。]{1,40}(?:대비|비교|증가)",
    r"5년 전[^.。]{1,80}(?:FCF|잉여현금흐름)",
]

FCF_USAGE_EN = [
    r"(?:FCF|free cash flow|cash generated)[^.]{1,80}(?:returned to shareholders|share repurchase|buyback|dividend|reinvest)",
]
FCF_USAGE_KO = [
    r"(?:FCF|잉여현금흐름|창출된 현금)[^.。]{1,80}(?:자사주|배당|환원|재투자)",
]

# =========================================================
# 3. 실수 대처법 (Mistake handling)
# =========================================================

MISTAKE_ADMISSION_EN = [
    r"\bwe (?:failed|missed|underperformed|fell short|made a mistake|got it wrong|should have)\b",
    r"\bI (?:misjudged|was wrong|underestimated|miscalculated)\b",
    r"\bour (?:mistake|error|shortfall|misstep)\b",
    r"\bcandidly\b", r"\bhonestly\b", r"\bfrankly\b",
    r"\bin hindsight\b",
    r"\b(?:my|our) analysis was (?:superficial|wrong|flawed)\b",
]

MISTAKE_ADMISSION_KO = [
    r"우리가 (?:잘못|실수|놓쳤|실패|부족)",
    r"제가 (?:잘못|오판|틀렸|놓쳤)",
    r"솔직히",
    r"돌이켜보면",
    r"(?:사실|솔직히) (?:우리|저희)",
    r"(?:잘못된|틀린) (?:판단|결정|분석)",
]

EXTERNAL_BLAME_EN = [
    r"\b(?:macro|macroeconomic)\b",
    r"\b(?:supply chain|supply-chain)\b",
    r"\b(?:currency|exchange rate|forex)\b",
    r"\bgeopolit\w+\b",
    r"\b(?:industry-wide|sector-wide)\b",
    r"\b(?:regulatory|regulation)\b[^.]{1,30}\b(?:impact|headwind|change)\b",
    r"\b(?:tariff|trade war)\b",
    r"\bseasonal[^.]{1,30}(?:factor|impact|effect)\b",
    r"\bunprecedented (?:environment|conditions)\b",
]

EXTERNAL_BLAME_KO = [
    r"(?:거시경제|매크로)",
    r"(?:공급망|서플라이체인)",
    r"(?:환율|외환|환 효과)",
    r"지정학",
    r"(?:업황|업계 전반)",
    r"(?:규제|제도)[^.。]{1,30}(?:영향|충격|변화)",
    r"(?:계절적|비수기)[^.。]{1,30}(?:요인|영향)",
    r"(?:글로벌|대외)\s*(?:불확실|환경|변동)",
    r"전례 없는 환경",
]

# =========================================================
# 4. 오웰 모순 (fog_lexicon_scorer와 중복되지만 단독 호출 가능)
# =========================================================

ORWELL_EN = [
    r"(?:not material|immaterial)[^.]{1,80}(?:may be material|could be material)",
    r"\bnot (?:unconfident|unhappy|unaware|unlikely|uncomfortable)\b",
    r"non[-\s]recurring[^.]{1,60}(?:recur|recurring|annually|every year)",
    r"(?:errors|mistakes|decisions|losses) were (?:made|taken|incurred)",
]

ORWELL_KO = [
    r"중요하지 않[다습][^.。]{1,60}중요할 수[도있]",
    r"믿[고으]나[^.。]{1,60}(?:불확실|장담할 수 없)",
    r"(?:오류|실수|손실|결정)(?:이|가) (?:발생|초래|이루어)(?:되었|졌)습니다",
    r"일회성[^.。]{1,60}(?:매년 발생|반복|지속)",
]


# =========================================================
# 핵심 함수
# =========================================================

def count_patterns(text: str, patterns: list[str]) -> tuple[int, list[str]]:
    total = 0
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE | re.MULTILINE):
            total += 1
            hits.append(m.group(0)[:120])
    return total, hits


def check_authorship(text: str, lang: str) -> dict:
    """자기 집필도 진단 — 1인칭 빈도 + 일화 + 실수 인정."""
    fp_pat = FIRST_PERSON_EN if lang == "en" else FIRST_PERSON_KO
    an_pat = ANECDOTE_KEYWORDS_EN if lang == "en" else ANECDOTE_KEYWORDS_KO
    mi_pat = MISTAKE_ADMISSION_EN if lang == "en" else MISTAKE_ADMISSION_KO

    fp_cnt, _ = count_patterns(text, fp_pat)
    an_cnt, an_hits = count_patterns(text, an_pat)
    mi_cnt, mi_hits = count_patterns(text, mi_pat)

    word_count = len(re.findall(r"\S+", text))
    fp_density = fp_cnt / max(word_count, 1) * 1000  # per 1000 words

    # 자기집필 점수 = (1인칭 밀도 정규화) + (일화) + (실수 인정)
    fp_score = min(40, fp_density * 5)   # 밀도 8/1000 → 40점 만점
    an_score = min(30, an_cnt * 10)      # 일화 3건 → 30점 만점
    mi_score = min(30, mi_cnt * 10)      # 실수 인정 3건 → 30점 만점
    authorship_score = round(fp_score + an_score + mi_score, 1)

    return {
        "first_person_count": fp_cnt,
        "first_person_density_per_1000": round(fp_density, 2),
        "anecdote_count": an_cnt,
        "anecdote_examples": an_hits[:5],
        "mistake_admission_count": mi_cnt,
        "mistake_examples": mi_hits[:5],
        "authorship_score": authorship_score,
        "verdict": (
            "자기 집필 강함 (CEO 직접 작성 가능성 높음)" if authorship_score >= 60 else
            "자기 집필 약함 (IR 대행 의심)" if authorship_score < 30 else
            "보통"
        ),
    }


def check_fcf(text: str, lang: str) -> dict:
    """FCF 맥락 평가 — 정의·5년대조·사용처."""
    def_pat = FCF_DEFINITION_EN if lang == "en" else FCF_DEFINITION_KO
    fy_pat = FCF_FIVE_YEAR_EN if lang == "en" else FCF_FIVE_YEAR_KO
    use_pat = FCF_USAGE_EN if lang == "en" else FCF_USAGE_KO

    def_cnt, def_hits = count_patterns(text, def_pat)
    fy_cnt, fy_hits = count_patterns(text, fy_pat)
    use_cnt, use_hits = count_patterns(text, use_pat)

    # FCF 단순 언급 카운트
    fcf_mention = len(re.findall(
        r"\b(?:FCF|free cash flow|잉여현금흐름)\b",
        text, re.IGNORECASE
    ))

    # J&J Larsen 패턴 충족 여부
    larsen_pattern = (def_cnt > 0 and fy_cnt > 0)

    score = 0
    if fcf_mention > 0:
        score += 25
    if def_cnt > 0:
        score += 25
    if fy_cnt > 0:
        score += 25
    if use_cnt > 0:
        score += 25

    return {
        "fcf_mention_count": fcf_mention,
        "definition_provided": def_cnt > 0,
        "definition_examples": def_hits[:3],
        "five_year_comparison": fy_cnt > 0,
        "five_year_examples": fy_hits[:3],
        "usage_specified": use_cnt > 0,
        "usage_examples": use_hits[:3],
        "larsen_pattern_match": larsen_pattern,
        "capital_stewardship_score": score,
        "verdict": (
            "자본 수탁 모범 (J&J Larsen 2001 패턴)" if larsen_pattern else
            "FCF 맥락 부족" if score < 50 else
            "보통"
        ),
    }


def check_mistake(text: str, lang: str) -> dict:
    """실수 대처법 — 인정 vs 외부 탓 비율."""
    ad_pat = MISTAKE_ADMISSION_EN if lang == "en" else MISTAKE_ADMISSION_KO
    bl_pat = EXTERNAL_BLAME_EN if lang == "en" else EXTERNAL_BLAME_KO

    ad_cnt, ad_hits = count_patterns(text, ad_pat)
    bl_cnt, bl_hits = count_patterns(text, bl_pat)

    total = ad_cnt + bl_cnt
    ratio = ad_cnt / total if total > 0 else 0.0

    if ratio >= 0.5:
        verdict = "내부 귀인 우세 (Expeditors 패턴) — Leadership +2"
        leadership_bonus = 2
    elif ratio < 0.2 and total > 5:
        verdict = "외부 탓 과다 (GM 패턴) — Leadership -1"
        leadership_bonus = -1
    else:
        verdict = "혼재"
        leadership_bonus = 0

    return {
        "admission_count": ad_cnt,
        "admission_examples": ad_hits[:5],
        "external_blame_count": bl_cnt,
        "blame_examples": bl_hits[:5],
        "internal_attribution_ratio": round(ratio, 3),
        "leadership_bonus": leadership_bonus,
        "verdict": verdict,
    }


def check_orwell(text: str, lang: str) -> dict:
    """오웰 모순 패턴."""
    pat = ORWELL_EN if lang == "en" else ORWELL_KO
    cnt, hits = count_patterns(text, pat)
    return {
        "orwell_sentence_count": cnt,
        "examples": hits[:10],
        "penalty_points": cnt * 5,
        "verdict": (
            "오웰 모순 다수 (AIG 2007 패턴 의심)" if cnt >= 2 else
            "오웰 모순 1건 — 정성 검토 필요" if cnt == 1 else
            "오웰 모순 없음"
        ),
    }


def render_markdown(results: dict, company: str, lang: str, src: str) -> str:
    lines = [
        f"# CEO Letter Forensics: {company}",
        "",
        f"언어: {'한국어' if lang == 'ko' else '영어'}",
        f"Source: {src}",
        "",
        "---",
    ]

    if "authorship" in results:
        a = results["authorship"]
        lines += [
            "",
            "## 1. 자기 집필도 (Authorship)",
            "",
            f"- 1인칭 빈도: {a['first_person_count']}건 "
            f"(밀도 {a['first_person_density_per_1000']}/1000단어)",
            f"- 일화 키워드: {a['anecdote_count']}건",
            f"- 실수 인정 키워드: {a['mistake_admission_count']}건",
            f"- **자기 집필 점수**: {a['authorship_score']} / 100",
            f"- **판정**: {a['verdict']}",
        ]
        if a["anecdote_examples"]:
            lines.append("\n**일화 예시:**")
            for ex in a["anecdote_examples"]:
                lines.append(f"- {ex}")

    if "fcf" in results:
        f = results["fcf"]
        lines += [
            "",
            "## 2. FCF 맥락 (Capital Stewardship)",
            "",
            f"- FCF 단순 언급: {f['fcf_mention_count']}건",
            f"- 정의 제시: {'Y' if f['definition_provided'] else 'N'}",
            f"- 5년 전 대조: {'Y' if f['five_year_comparison'] else 'N'}",
            f"- 사용처 명시: {'Y' if f['usage_specified'] else 'N'}",
            f"- **J&J Larsen 패턴 매칭**: {'YES (+2 ① Capital Stewardship)' if f['larsen_pattern_match'] else 'NO'}",
            f"- **Capital Stewardship 점수**: {f['capital_stewardship_score']} / 100",
            f"- **판정**: {f['verdict']}",
        ]

    if "mistake" in results:
        m = results["mistake"]
        lines += [
            "",
            "## 3. 실수 대처법 (Leadership)",
            "",
            f"- 실수 인정: {m['admission_count']}건",
            f"- 외부 탓: {m['external_blame_count']}건",
            f"- **내부 귀인 비율**: {m['internal_attribution_ratio']*100:.1f}%",
            f"- **Leadership 보너스**: {m['leadership_bonus']:+d}",
            f"- **판정**: {m['verdict']}",
        ]

    if "orwell" in results:
        o = results["orwell"]
        lines += [
            "",
            "## 4. 오웰 모순 패턴",
            "",
            f"- 오웰 문장 수: {o['orwell_sentence_count']}건",
            f"- 감점: -{o['penalty_points']} 점",
            f"- **판정**: {o['verdict']}",
        ]
        if o["examples"]:
            lines.append("\n**예시:**")
            for ex in o["examples"][:5]:
                lines.append(f"- {ex}")

    lines += [
        "",
        "---",
        "",
        "## 후속 조치",
        "",
        "- `templates/ceo_letter_candor7_report.md`에 결과 통합",
        "- 7-시스템 레이더 ① Capital Stewardship / ⑤ Leadership 점수 보정",
        "- 자기집필 < 30점 시 Step 5 Pre-mortem에서 IR 대행 가설 검증",
        "- 상세: `references/candor7_framework.md`, `references/case_library.md`",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="CEO Letter 5단계 포렌식 보조 진단기")
    parser.add_argument("--input", required=True)
    parser.add_argument("--lang", default="en", choices=["en", "ko"])
    parser.add_argument("--company", default="Unknown")
    parser.add_argument("--check", default="all",
                        choices=["all", "authorship", "fcf", "mistake", "orwell"])
    parser.add_argument("--out", default="letter_forensics")
    parser.add_argument("--no-md", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"파일 없음: {src}", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8")
    lang = args.lang

    results = {"company": args.company, "language": lang, "source": str(src)}

    if args.check in ("all", "authorship"):
        results["authorship"] = check_authorship(text, lang)
    if args.check in ("all", "fcf"):
        results["fcf"] = check_fcf(text, lang)
    if args.check in ("all", "mistake"):
        results["mistake"] = check_mistake(text, lang)
    if args.check in ("all", "orwell"):
        results["orwell"] = check_orwell(text, lang)

    out_path = Path(args.out)
    out_dir = out_path.parent if str(out_path.parent) != "." else Path.cwd()
    out_stem = out_path.name
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / f"{out_stem}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if not args.no_md:
        md = render_markdown(results, args.company, lang, str(src))
        (out_dir / f"{out_stem}.md").write_text(md, encoding="utf-8")

    # 요약 출력
    print(f"=== {args.company} CEO Letter Forensics ===")
    if "authorship" in results:
        print(f"자기집필 점수: {results['authorship']['authorship_score']} / 100 "
              f"— {results['authorship']['verdict']}")
    if "fcf" in results:
        print(f"FCF 맥락 점수: {results['fcf']['capital_stewardship_score']} / 100 "
              f"— {results['fcf']['verdict']}")
    if "mistake" in results:
        print(f"실수 대처: 인정 {results['mistake']['admission_count']} / "
              f"외부탓 {results['mistake']['external_blame_count']} "
              f"({results['mistake']['internal_attribution_ratio']*100:.1f}%) "
              f"— {results['mistake']['verdict']}")
    if "orwell" in results:
        print(f"오웰 문장: {results['orwell']['orwell_sentence_count']}건 — "
              f"{results['orwell']['verdict']}")
    print(f"결과: {out_dir / out_stem}.json / .md")


if __name__ == "__main__":
    main()

---
name: financial-analysis
description: 기업 재무분석 통합 스킬 - 재무제표·재무비율·DuPont·현금흐름·Red Flag·Peer 비교·업종 벤치마크를 종합하여 ⭐등급(지표)과 A+~D 투자등급(종합)을 산출합니다. 사용자가 재무 숫자(NL/표/CSV/JSON)를 직접 제공하면 Mode A로 1페이지 빠른 판정을, 기업명·티커를 제공하면 MCP로 3~5년 시계열 데이터를 수집해 Mode B 8섹션 심층 보고서를 생성합니다. "재무분석·재무제표 분석·재무비율·ROE·ROIC·DuPont·부채비율·영업이익률·현금흐름·회계 건전성·Red Flag·Beneish·Altman Z-Score·Peer 비교·업종 벤치마크·투자등급·이익의 질·경영진단" 등 재무진단 관련 요청이 있으면 반드시 이 스킬을 사용하세요. 적정주가(DCF)는 intrinsic-value-analyzer, 해자 분석은 eco-moat-ai, 분기 실적은 earnings-analysis로 위임합니다.
---

# Financial Analysis — 기업 재무진단 통합 스킬

본 스킬은 **재무제표 분석의 4계층(계산→해석→진단→통찰)**을 하나의 워크플로우로 엮어
사용자에게 **행동 가능한 재무 진단(Actionable Diagnosis)**을 제공합니다.

---

## 0. 작동 원칙 & 언어 정책

1. **Data-First** — 모든 판단은 재무제표 원본 수치를 근거로 합니다. 인상평가·추측 금지.
2. **Trend > Point** — 단일 연도 수치보다 3~5년 **추세와 속도 변화**를 우선합니다.
3. **Context Matters** — 동일 비율도 업종에 따라 해석이 달라집니다. 업종 벤치마크 필수 병기.
4. **Cash Doesn't Lie** — 이익과 현금흐름의 괴리를 항상 추적합니다.
5. **Notes Over Numbers** — 주석에 숨은 리스크(우발부채·특수관계자 거래·수익인식 정책)를 점검합니다.

**언어 정책:**
- 사용자 언어에 맞추어 출력 (한국어 요청 → 한국어, 영어 요청 → 영어)
- 한국어 출력 시 전문용어는 **`한국어명 (영문약어)`** 표기 — 예: 자기자본이익률 (ROE)
- 영어 출력 시 약어 그대로 사용 — 예: ROE, EBITDA, FCF

---

## 1. 모드 자동 분기 (Mode A / Mode B)

사용자가 모드를 명시하지 않아도 아래 규칙으로 자동 판정합니다.

```
┌───────────────────────────────────────┐
│  사용자 요청                           │
└───────────────────────────────────────┘
              ↓
    ┌──────────────────┐
    │ 기업명/티커 있음? │
    └──────────────────┘
       │            │
      No            Yes
       │            │
       ↓            ↓
 ┌──────────┐  ┌──────────────┐
 │ 숫자 있음? │  │ 데이터 제공?  │
 └──────────┘  └──────────────┘
   │      │     │          │
  Yes    No    Yes         No
   ↓      ↓     ↓          ↓
Mode A  [요청] Mode B    MCP 수집
               (수집생략)   →
                          Mode B
```

### Mode A · Quick Scan 트리거 (아래 모두 충족)
- 사용자가 재무 숫자를 직접 제공 (NL 문장 / 표 / CSV / JSON)
- 기업명·티커가 언급되지 않았거나 추가 데이터 수집 불필요
- "심층 / Deep / Peer / 투자등급 / Red Flag / 3년 / 시계열" 키워드 없음

**산출물:** 1페이지 ⭐ 등급 대시보드 (→ `references/06_report_templates.md` §1)

### Mode B · Deep Diagnosis 트리거 (하나라도 충족)
- 기업명·티커가 명시되고 실데이터 수집 필요
- 3~5년 시계열 분석 요청
- "심층 / Deep / Peer / 투자등급 / Red Flag / 통찰 / 경영진단" 등 키워드
- 사용자가 직접 제공했더라도 다기간(3년 이상) 데이터

**산출물:** 8섹션 A+~D 투자등급 보고서 (→ `references/06_report_templates.md` §2)

---

## 2. Mode A 실행 절차 (Quick Scan)

1. 제공된 재무 숫자에서 **5대 축 핵심 지표** 계산
   (매출성장률 / 영업이익률 / ROE / 총자산회전율 / 부채비율 / 이자보상배율 / 유동비율)
2. 업종 정보가 있으면 `references/02_ratios.md`의 해당 업종 벤치마크로 **⭐ 등급 부여**
3. 업종 불명 시 **General(일반)** 기준 적용 + 출력에 명시
4. 3줄 요약(강점·약점·종합) + 주의 포인트 + 다음 단계 안내
5. 적정주가 / 분기 실적 / 해자 등 요청이 섞여 있으면 **Delegation Matrix**(§4)로 위임 안내

> ⭐ 등급 4단계 (개별 지표):
> ⭐⭐⭐⭐ 탁월 / ⭐⭐⭐ 양호 / ⭐⭐ 보통 / ⭐ 미흡

---

## 3. Mode B 실행 절차 (Deep Diagnosis 7 Steps)

| Step | 작업 | 상세 파일 |
|------|------|---------|
| 1 | 자료 수집 & 맥락 설정 (MCP 호출) | `references/07_data_sources.md` |
| 2 | 데이터 정규화 (일회성 조정·SBC·환율·M&A) | `references/01_framework.md` §4 |
| 3 | 5대 축 재무비율 시계열 계산 | `references/02_ratios.md` |
| 4 | DuPont 분해 + ROIC vs WACC + 현금흐름 패턴 | `references/03_dupont_cashflow.md` |
| 5 | Red Flag 30 + Beneish M-Score + Altman Z | `references/04_red_flags.md` |
| 6 | Peer 비교 (3~5개사) | `references/05_industries_peer.md` |
| 7 | Insight 3대 프레임 + 최종 A+~D 등급 | `references/01_framework.md` §5 |

**최종 출력:** 8섹션 구조의 심층 보고서
(→ `references/06_report_templates.md` §2 템플릿 엄수)

> 🎯 종합 투자등급 (기업 전체):
> **A+** 최우량 / **A** 우량 / **B** 보통 / **C** 주의 / **D** 위험
>
> ⭐(지표)과 A+~D(종합)는 **다른 추상화 레벨**입니다. 혼용 금지.

---

## 4. Delegation Matrix — When to Delegate

본 스킬은 **재무진단** 범위에 집중하고, 아래 영역은 타 스킬·MCP로 위임합니다.

| 영역 | 이 스킬 | 위임 대상 |
|------|-------|----------|
| 재무비율 계산·해석 | ✅ 직접 | — |
| 5대 축(성장·수익·활동·안정·유동) 진단 | ✅ 직접 | — |
| DuPont·ROIC·WACC 스프레드 | ✅ 직접 | — |
| Red Flag / Beneish / Altman | ✅ 직접 | — |
| 산업·Peer 비교 | ✅ 직접 | — |
| 현금흐름 **요약 패턴(A~E)** | ✅ 직접 | 심층 운전자본·FCF Bridge → `anthropic-skills:cash-flow-analysis` |
| 적정주가 (DCF / RIM / Multiple) | ❌ | `anthropic-skills:intrinsic-value-analyzer` |
| 분기 실적·EPS 서프라이즈·가이던스 | ❌ | `anthropic-skills:earnings-analysis` |
| 경제적 해자 (Moat) | ❌ | `anthropic-skills:eco-moat-ai` |
| DCF·Budget·Scenario 모델(xlsx) | ❌ | `anthropic-skills:creating-financial-models` |
| 종목 스크리닝·유니버스 | ❌ | `anthropic-skills:value-screener` |
| 주가 차트·테크니컬 | ❌ | `anthropic-skills:technical-analysis`, `stock-analysis` |
| 정량 모델·백테스트 | ❌ | `anthropic-skills:quant-analyst`, `backtesting-frameworks` |
| **데이터 수집** | ❌ (호출 안내만) | MCP: korea-stock, open-dart-reader, kis, sec-edgar, FMP, yfmcp, finnhub, japan-corporate, ecos, kosis, fred |
| **시각화** | ❌ (데이터만 준비) | `anthropic-skills:plotly`, `seaborn` |
| **문서 산출** (docx/pptx/xlsx) | ❌ (마크다운까지) | `anthropic-skills:docx`, `pptx`, `xlsx` |

### 위임 예시
- 사용자: "삼성전자 적정주가 계산해줘"
  → "**재무진단은 본 스킬**에서 진행해 드리고, 적정주가 산출은
  `intrinsic-value-analyzer` 스킬로 이어가시는 것을 권고드립니다. DCF에 필요한
  FCF·WACC 추정치는 본 분석 결과를 그대로 활용할 수 있습니다."

- 사용자: "삼성전자 경제적 해자는?"
  → "해자 분석은 `eco-moat-ai` 스킬 전문 영역입니다. 본 스킬은 가격결정력·자본배분
  효율성·운영실행력 3대 프레임으로 해자의 **정량적 흔적**을 추적합니다. 심층 정성
  분석은 eco-moat-ai로 연계 권고."

---

## 5. MCP 라우팅 요약 (기업 국적 × 데이터 유형)

```
데이터 유형        | 한국 상장            | 미국 상장              | 일본 상장         | 글로벌
──────────────────|---------------------|----------------------|-----------------|------
재무제표 원본     | korea-stock (1)     | sec-edgar (1)        | japan-corporate | —
주석·서술 섹션    | open-dart-reader(1)| sec-edgar filings    | japan-corporate | —
재무비율          | KIS (1)             | FMP (1) / finnhub(2) | japan-corporate | FMP
Peer 리스트       | KIS 업종 분류       | FMP peers (1)        | FMP             | FMP, finnhub
시계열 주가       | pykrx (1)           | yfmcp (1)            | yfmcp (2)       | yfmcp
애널리스트 컨센   | korean-research     | finnhub(1)/FMP(2)    | —               | finnhub
뉴스             | marketaux/newsdata  | finnhub/marketaux    | —               | marketaux
거시지표         | ecos (1), kosis(2)  | fred (1)             | —               | fred, oecd-data
```

**호출 원칙:**
- 1순위 MCP 실패 시 2순위로 자동 폴백
- 재무제표 원본은 **법정 공시(DART/SEC) 우선** — 상용 서비스보다 정확
- 모든 KIS 호출에 `env_dv: "real"` 필수
- 상세 호출 예시 → `references/07_data_sources.md`

---

## 6. 에지 케이스 처리

| 케이스 | 처리 방법 |
|--------|----------|
| 업종 정보 불명 | General(일반) 기준 적용 + "업종 미상으로 General 기준 적용" 명시 |
| 데이터 일부 누락 | 계산 가능한 지표만 산출, 누락 항목은 "N/A" + 대체 지표 제안 |
| 분기 데이터만 있음 | Annualize 전제 명시 후 Mode A 적용 or 4분기 합산 |
| 3년 미만 데이터 | Mode B는 Mode A로 다운그레이드 후 "시계열 부족" 경고 |
| 단위 불명 (천원/백만원/억원/원) | 단위를 사용자에게 확인하거나 합리적 추정 후 명시 |
| 금융업 | DuPont·Altman 일반 공식 부적용 명시, NIM·BIS·NPL 중심 판단 |
| 바이오 초기 (R&D 단계) | Altman Z 적용 불가 표시, FCF·Runway 중심 재구성 |
| 적자 기업 | ROE·ROIC 해석 주의 명기, EV/Sales·FCF 마진 대체 지표 활용 |
| IFRS 16 이전/이후 혼재 | 리스 제외 EBITDA 기준으로 통일 비교 |
| 환율·기능통화 차이 | 기능통화 원본 우선 + USD 환산값 병기 |
| MCP 전부 실패 | 사용자에게 직접 재무제표 첨부 요청 (자료 포기 금지) |
| 수치 신뢰성 의심 | 교차 확인 (DART vs KIS, SEC vs FMP) 후 판단 유보 가능 |

---

## 7. 파일 네비게이션

```
financial-analysis/
├── SKILL.md                       ← 현재 파일 (진입점)
└── references/
    ├── 01_framework.md            ← 4계층 철학 + 7단계 워크플로우 + 최종 등급 로직
    ├── 02_ratios.md               ← 50+ 비율 공식 + 8업종 × 4등급 벤치마크
    ├── 03_dupont_cashflow.md      ← DuPont 3/5 + ROIC + 현금흐름 A~E 패턴
    ├── 04_red_flags.md            ← Red Flag 30 + Beneish M + Altman Z
    ├── 05_industries_peer.md      ← 7업종 심화 해석 + Peer 방법론
    ├── 06_report_templates.md     ← Mode A 1페이지 + Mode B 8섹션 템플릿
    └── 07_data_sources.md         ← MCP 호출 예시 + 우선순위 매트릭스
```

**진입 순서:**
1. 요청을 분석해 모드 분기 (§1)
2. Mode A면 `02_ratios.md` + `06_report_templates.md` §1만 참조
3. Mode B면 7단계 순서대로 `01 → 02 → 03 → 04 → 05 → 06`
4. 데이터 수집 필요 시 언제든 `07_data_sources.md` 호출
5. 타 스킬 위임 상황이면 §4 Delegation Matrix 메시지 출력

---

## 8. 품질 보증 체크 (최종 출력 직전)

- [ ] 모든 수치에 **출처**가 표기되어 있는가? (DART/SEC/FMP 등)
- [ ] 업종 벤치마크와 비교하여 등급이 매겨졌는가?
- [ ] 시계열 추세(▲/▼/→)가 일관되게 표시되었는가?
- [ ] ⭐(지표)와 A+~D(종합) 등급이 **혼동 없이 분리**되어 있는가?
- [ ] 위임 대상 요청(DCF·해자 등)을 임의로 처리하지 않고 **위임 안내**로 출력했는가?
- [ ] 면책 조항("투자 참고용, 최종 판단은 이용자 책임") 포함되었는가?
- [ ] 한국어 출력 시 전문용어에 **한글(영문약어)** 병기가 되어 있는가?

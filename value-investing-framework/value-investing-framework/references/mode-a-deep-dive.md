# Mode A: 단일 종목 풀 분석 절차

단일 기업이 입력되었을 때 그린월드 프레임워크를 끝까지 적용한다. 아래 9단계를 순서대로 수행하라.

## 1. 종목 정규화·시장 식별

- 한국 6자리(`^\d{6}$`) → KRX 시장 (KOSPI/KOSDAQ 자동 판별: `korea-stock-mcp:get_market_type`)
- 미국 알파벳 티커(`^[A-Z]{1,5}$`) → SEC-EDGAR + yfinance
- 종목명만 주어지면:
  - 한국 의심 → `naver-stock:search_codes` → 6자리 코드 확정
  - 미국 의심 → `finnhub:finnhub_symbol_lookup` → 티커 확정
- 모호한 경우 `cross-market-equity-router` 스킬에 위임

산출: `{name, code, market, currency, share_class}`

## 2. 기업·산업 개요 + 역발상 적합성

데이터 수집:
- 비즈니스 모델 1~2문장 요약
- 산업 분류 (KSIC, SIC, GICS)
- 시가총액
- 52주 가격 위치 = (현재가 - 52주 저점) / (52주 고점 - 52주 저점)
- PER, PBR (역사적 평균과 비교)
- 6개월·12개월 가격 모멘텀

역발상 적합성 점수 (정성):
- 52주 위치 < 30% → 소외 (+)
- PER, PBR 산업 평균 대비 -30% 이상 → 저평가 시그널 (+)
- 12개월 모멘텀 음수 → 실망주 (+)
- 시가총액 소형~중형 → 정보 비대칭 가능성 (+)
- 최근 6개월 거래량 급감 → 관심 이탈 (+)

이 단계에서는 점수만 매기고, 부적합 판정은 내리지 않는다 (그린월드는 단순 인기/소외만으로 분류하지 않음).

## 3. 자산가치 (AV) 계산

먼저 산업 분류부터:
- **사양 산업 신호**: 매출 5년 CAGR < 0, 산업 시총 축소, 대체기술 위협 명백
- **존속 산업 신호**: 매출 안정 또는 성장, 시장 성숙기 또는 성장기

분기 후 상세 절차는 `references/asset-value-calculation.md`. 산출은 `scripts/compute_av_liquidation.py` 또는 `scripts/compute_av_reproduction.py`.

산출: `{av_total, av_per_share, methodology, key_adjustments}`

## 4. 수익력가치 (EPV) 계산

상세는 `references/epv-calculation.md`. 다음 순서:
1. 최근 5~7년 영업이익(EBIT) 시계열 확보
2. 일회성 손익 제외
3. 경기 평탄화 (필요 시)
4. D&A vs Maintenance CapEx 조정
5. NOPAT = 조정 EBIT × (1 - 유효세율)
6. WACC 산정 (`scripts/compute_wacc.py`)
7. EPV(Enterprise) = NOPAT / WACC → EPV(Equity) = EPV(EV) - Net Debt → 주당 EPV
   - `scripts/compute_epv.py`

산출: `{epv_total, epv_per_share, normalized_ebit, wacc, assumptions}`

## 5. 매트릭스 분류

`references/matrix-classification.md` + `scripts/matrix_classify.py`.

비율 = EPV / AV

- < 0.7 → **Case A** (가치 함정 의심)
- 0.7 ~ 1.3 → **Case B** (평범, 진입장벽 없음)
- > 1.3 → **Case C** (프랜차이즈)

교차 검증 — ROIC vs WACC:
- ROIC > WACC + 2%p → 프랜차이즈 추가 증거 (Case C 강화)
- ROIC < WACC → Case A 가능성 증가 (자본 파괴)

산출: `{ratio, case, roic, roic_vs_wacc, confidence}`

## 6. Case별 분기 분석

- **Case A**: `references/case-a-catalyst.md` 적용. 촉매제 검색 후 Conditional Buy / Avoid 판정.
- **Case B**: 진입장벽 없는 평범한 비즈니스. 성장 무가치. 내재가치 = (AV + EPV) / 2 정도로 보수 추정.
- **Case C**: `references/case-c-franchise.md` 적용. 해자 검증 + 성장가치 산출.

## 7. 안전마진 평가

`scripts/compute_margin_of_safety.py`.

- 보수적 내재가치 산출 (Case별 최저 추정값 사용)
- 안전마진 = (내재가치 - 현재가) / 내재가치
- 0.33 이상 → 매수 검토
- 0.50 이상 → 강력 매수
- 음수 또는 0.10 미만 → 매수 부적합

## 8. 최종 의견 BUY/HOLD/AVOID

판정 매트릭스:

| 안전마진 | Case | 의견 |
|---|---|---|
| ≥ 0.50 | B/C | **STRONG BUY** |
| ≥ 0.33 | B/C | **BUY** |
| ≥ 0.33 | A + 강한 촉매 | **CONDITIONAL BUY** |
| 0.10 ~ 0.33 | 모든 Case | **HOLD** |
| < 0.10 | 모든 Case | **AVOID** |
| 음수 | 모든 Case | **AVOID** (고평가) |
| 자본잠식 + 촉매 없음 | A | **AVOID** |

부가 정보:
- 분할매수 가격대: 현재가에서 안전마진 0.50 지점까지 3~5분할
- 모니터링 포인트: Case별 핵심 KPI (Case A=Catalyst 진척, Case B=경쟁환경, Case C=ROIC 유지)
- 리스크 요인: 데이터 결손, 산업 위험, 거시 위험 등

## 9. 보고서 출력

`assets/report-template-ko.md` 양식 사용. 출력 순서는 SKILL.md의 Output Contract 참조.

사용자가 명시적으로 요청하면 `xlsx` 스킬에 계산 내역 위임, `pptx` 또는 `plotly` 스킬에 시각화 위임.

## 데이터 결손 대응

5년 미만 데이터:
- 3년 데이터로 EPV 산출, 추정 신뢰도 "Low" 표기
- 1~2년만 있으면 EPV는 N/A로 두고 AV만 산출, Mode B의 Special 분류와 동일하게 처리

자본잠식:
- EPV 계산 생략 또는 음수로 두고 Case A 청산가치 모드로 전환
- Catalyst가 없으면 즉시 AVOID

극단적 고PBR + 적자:
- AV 계산 의미 약함 → 사용자에게 "본 프레임워크는 고성장 적자 기업에 적합하지 않다" 안내, `intrinsic-value-analyzer`로 라우팅

# AV vs EPV 매트릭스 분류

`scripts/matrix_classify.py`가 자동화. 분류 기준과 해석 가이드를 정리한다.

## 핵심 비율

```
ratio = EPV / AV   (Enterprise 기준 또는 주당 기준 동일)
```

## 분류 임계값

| Case | ratio | 명칭 | 의미 |
|---|---|---|---|
| **A** | < 0.7 | Value Trap 의심 | 자산은 있는데 수익을 못 내는 상태 |
| **B** | 0.7 ~ 1.3 | Commodity Business | 진입장벽이 없어 경쟁이 초과수익을 침식 |
| **C** | > 1.3 | Franchise | 진입장벽(해자)이 EPV > AV를 만든다 |

임계값은 가이드라인이며 경계(0.7, 1.3)에서는 ROIC 교차 검증으로 최종 분류한다.

## ROIC vs WACC 교차 검증

```
ROIC = NOPAT / Invested Capital
Invested Capital = Equity + Total Debt - Cash
```

| ROIC 상황 | 해석 | 분류 강화/약화 |
|---|---|---|
| ROIC > WACC + 3%p | 자본을 효율적으로 활용, 경제적 이익 창출 | Case C 가능성 강화 |
| ROIC > WACC + 0~3%p | 양호 | Case B 또는 약한 Case C |
| ROIC ≈ WACC | 경쟁시장 평균 | Case B 강화 |
| ROIC < WACC | 자본 파괴, 부실 경영 또는 사양 산업 | Case A 강화 |

### 모순 케이스 처리

- EPV/AV > 1.3 (Case C 후보) 인데 ROIC < WACC → 산식 검증 (Maintenance CapEx 과소 추정 가능성). 둘 다 재계산 후 결과가 변하지 않으면 Case A로 재분류 (자산이 비효율 운영 중).
- EPV/AV < 0.7 (Case A 후보) 인데 ROIC > WACC + 3%p → AV가 과대 추정되었을 가능성 (재생산 비용에 무형자산을 과하게 자본화). AV 재검토 권장.

## Case A: Value Trap 의심

자산은 있는데 수익력이 부족한 상태. 두 가지 시나리오:

1. **부실 경영** — 같은 자산으로 수익을 내야 하는데 못 냄. **외부 촉매(M&A, 행동주의, 경영진 교체)** 가 있으면 잠재 가치 실현 가능.
2. **사양 산업** — 자산이 점차 의미 없어짐. 청산가치만 남고, EPV는 계속 감소.

후속 분석: `references/case-a-catalyst.md`

내재가치 추정:
- 촉매제 있음: AV의 70~80% (촉매 성공 확률 가중)
- 촉매제 없음: 청산가치 (가장 보수적)
- 사양 산업 + 촉매 없음: 사실상 AVOID

## Case B: Commodity Business

진입장벽이 없어 경쟁이 초과수익을 침식한다. 이런 비즈니스는:

- 성장이 가치를 창출하지 않음 (성장에 필요한 자본이 그 성장으로 얻는 수익과 같음)
- AV와 EPV가 거의 같다는 것 자체가 경쟁이 초과수익을 침식했다는 증거

내재가치 추정:
```
내재가치 = max(AV, EPV)  또는  (AV + EPV) / 2
```

보수적으로 둘 중 낮은 값을 채택해도 됨. 보고서에는 두 값 모두 제시.

매수 의견은 안전마진에만 의존. 안전마진 0.33 이상이면 BUY 가능.

## Case C: Franchise

진입장벽(해자)가 존재해 EPV > AV. 이 격차가 **프랜차이즈 가치 = EPV - AV**.

해자의 종류 (그린월드 분류):
1. **고객 캡티브 (Customer Captivity)** — 전환 비용, 습관, 학습 비용
2. **규모의 경제 (Economies of Scale)** — 로컬 규모, 지리적 우위
3. **독점적 자원/기술** — 특허, 면허, 자원 매장
4. **네트워크 효과** (현대 추가)
5. **규제 우위** (현대 추가)

해자 검증은 `references/case-c-franchise.md`에서 상세. 정성 검증은 `eco-moat-codex` 스킬에 위임 권장.

내재가치 = AV + Franchise Value + Growth Value
```
Franchise Value = EPV - AV
Growth Value    = 별도 산출 (Case C 분석에서)
```

## 분류 표시 (보고서)

```
| 항목 | 값 |
|---|---|
| AV (주당) | XX,XXX원 |
| EPV (주당) | YY,YYY원 |
| EPV / AV 비율 | Z.ZZ |
| 1차 분류 | Case B |
| ROIC (5년 평균) | A.A% |
| WACC | B.B% |
| ROIC - WACC | C.C%p |
| ROIC 검증 | 일치 (분류 유지) |
| 최종 Case | **Case B** |
| 분류 신뢰도 | High / Medium / Low |
```

## 분류 신뢰도 평가

- **High**: AV/EPV 비율이 임계값에서 멀고 ROIC 검증과 일치
- **Medium**: 임계값 근처 또는 ROIC와 약간 불일치
- **Low**: 임계값 근처 + ROIC 강한 불일치 → 두 가지 Case로 모두 분석 권장

## 다음 단계 라우팅

- Case A → `references/case-a-catalyst.md`
- Case B → 본 문서 위 "Case B" 절로 충분, 별도 reference 없음
- Case C → `references/case-c-franchise.md`

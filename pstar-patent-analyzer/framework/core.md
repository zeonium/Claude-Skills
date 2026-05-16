# P-STAR v2.2 — 6-Step 분석 프로토콜

## 분석 모드 선택

| 입력 특허 수 | 모드 | 실행 단계 |
|------------|------|----------|
| 1건 | 단건 모드 | S1(기본형태) → S2(구체성+수치근거) → S3(한계) → S4(기술충돌) → S6 |
| 2건 이상 | 다건 모드 | S1(기본형태) → S2(구체성+수치근거) → S3(한계) → S4(기술충돌) → S5 → S6 |

---

## Phase 0: 특허 데이터 취득

우선순위 순서로 데이터를 취득한다:

1. **google-patents-serpapi MCP** (최우선) — `serpapi_google_patents_details` 도구 호출
   - `patent_id` 파라미터: `"patent/USXXXXXXXXXX"` 또는 `"patent/USXXXXXXX B2"` 형식
   - 취득 대상: title, abstract, claims (전체), inventors, assignees, publication_date, priority_date, classifications (CPC), cited_by, citations
2. **사용자 PDF** — PDF 스킬 또는 Read 도구로 텍스트 추출
3. **사용자 제공 청구항 텍스트** — 그대로 사용

취득 후 다음을 확인한다:
- 독립항 수 및 번호
- 종속항 수
- CPC 분류 코드 (도메인 판단용)
- 출원인 및 등록일

---

## S1 체크리스트 — TRM 태깅 (특허의 기본 형태)

`framework/trm.md`를 로드하여 수행한다.

```
□ 독립항 수 확인 (각 독립항별 TRM 개별 판정)
□ 각 독립항의 TRM 유형 판정 (Composition / Apparatus / Method / Use)
□ 이중청구 여부 판정 (기존 5유형과 비교)
□ 신규 이중청구 유형 발견 시 → pending_hypotheses.md에 가설 등록
□ 기존 귀납 레퍼런스와 매칭 확인
```

---

## S2 체크리스트 — CAL (구체성 수준) + QET (수치 근거)

`framework/cal.md`와 `framework/qet.md`를 로드하여 수행한다.

```
□ 독립항별 CAL 유형 판정 (CAL-1/2/3/2N/Functional/3E)
□ 종속항에서 CAL-3E 패턴 탐색 (열거 Table이 있는가?)
□ 복합 CAL 패턴 탐색 (3중레이어, 계층화)
□ CAL-IP 해석 — 보호범위 + 회피 전략 + 난이도
□ QET 도출 (수치가 포함된 모든 청구항에서)
□ R-QET 탐색 (두 성분 간 시간적·비율 관계)
□ R-QET-D 탐색 (복잡도·부품수·공정수 감소 수치)
```

---

## S3 체크리스트 — 관계 + NP (기존 방식의 한계)

`framework/relations.md`를 로드하여 수행한다.

```
□ 관계 맵 작성 (최소 3개 관계 도출)
□ NP — Negative Pathway 도출 (최소 1개 필수)
□ requires_prior_to 탐색 — 공정 순서 의존성이 있는가?
□ [다건 모드 추가]
  □ competes_with 관계 식별
  □ subsumes 관계 식별 (한 특허 청구범위가 다른 것을 포함하는가?)
  □ fails_unless 관계 식별
```

---

## S4 체크리스트 — M-패턴 (핵심 기술 충돌)

`framework/m_patterns.md`를 로드하여 수행한다.

```
□ Level A 탐색 (M-1, M-2, M-3) — 전 도메인 보편
□ Level B 탐색 (M-4, M-5, M-8)
  ★ M-4: 현재 5도메인 확인. 새 도메인 발견 시 LevelA 격상 → pending_hypotheses 갱신
□ Level C 탐색 (M-6, M-7, M-9, M-10) — 도메인 특화
  ★ M-9 서브타입 ST-3/ST-4 추가 귀납 여부 탐색
□ 식별된 M-패턴별 TRIZ 원리 검증
  — triz-patent-analyzer의 triz_matrix_solver.py 재활용 (tools/triz_matrix_ref.md 참조)
□ 신규 M-패턴 후보 발견 시 → pending_hypotheses.md에 가설 등록
```

---

## S5 체크리스트 — DDP + CD-DDP (다건 전용)

`framework/ddp.md`와 `knowledge/cd_ddp_ledger.md`를 로드하여 수행한다.

```
□ 도메인 내 DDP 집계 (Strong ≥3건 / Moderate =2건 / One-off =1건)
□ CD-DDP 원장 업데이트 예비 계산 (건수 증가 확인)
□ White Space 식별 (미탐색 TRIZ 원리 공간)
□ 특허 간 포트폴리오 포지션 분석
```

---

## S6 체크리스트 — 전략 종합

```
□ [단건] 혁신 제안 카드 출력 (아래 형식)
□ [다건] 비교 매트릭스 + 관계 그래프 출력
□ White Space (회피·확장 기회) 최소 3개 도출
□ 프레임워크 기여 항목 목록 확인 → 자가 갱신 프로토콜 진입
```

### 혁신 제안 카드 형식 (단건)

```
┌──────────────────────────────────────────────────┐
│  혁신 제안 카드 | [특허번호]                        │
├──────────────────────────────────────────────────┤
│  핵심 혁신                                        │
│  [발명의 핵심을 1~2문장으로 요약]                   │
├──────────────────────────────────────────────────┤
│  M-패턴    [주패턴(LevelX)] + [보조패턴(LevelY)]   │
│  ↳ 핵심 기술 충돌                                  │
│  핵심 TRIZ [#원리1 + #원리2 + ...]                │
│  TRM       [유형] (이중청구 여부)                  │
│  ↳ 특허의 기본 형태                               │
│  CAL       [독립항 CAL] + [종속항 주요 CAL]        │
│  ↳ 구체성 수준                                    │
├──────────────────────────────────────────────────┤
│  White Space (회피/확장 기회)                     │
│  ① [기회1]                                       │
│  ② [기회2]                                       │
│  ③ [기회3]                                       │
└──────────────────────────────────────────────────┘
```

### 다건 출력 항목

1. 특허 간 관계 그래프 (competes_with / subsumes / requires_prior_to)
2. CAL 분포 히트맵 (도메인별 청구 추상도)
3. M-패턴 공통·고유 분포
4. DDP / CD-DDP 히트맵
5. IP 기회 영역 (White Space + subsumes 취약점)
6. 비교 매트릭스

---

## 후속 연계 안내 (S6 완료 후)

분석 완료 후 사용자에게 다음 스킬과의 연계를 안내한다:

| 목적 | 연계 스킬 |
|------|----------|
| TRIZ 발명 원리 심화 적용 아이디어 생성 | `triz-patent-analyzer` |
| 핵심 특허 품질 정량 점수 | `patent-quality-scorer` |
| 기술 시각화 이미지 프롬프트 생성 | `patent-visual-reporter` |
| 인용 네트워크 경쟁 포지션 분석 (다건) | `patent-citation-analyst` |

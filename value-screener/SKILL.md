---
name: value-screener
description: >
  투자 대가들의 종목 선정 기준으로 주식을 스크리닝하고 정량적 점수를 부여하는 전문 스크리닝 시스템.
  다음 상황에서 반드시 활성화:
  - "종목 스크리닝", "종목 선정", "투자 대상 찾아줘", "어떤 종목이 좋아", "주식 골라줘"
  - "가치투자 기준으로", "그레이엄", "버핏", "그린블라트", "린치", "슐로스", "클라만"
  - "모멘텀 투자", "역발상 투자", "CANSLIM", "PEG ratio", "Magic Formula"
  - "스프레드시트 업로드 후 분석", "엑셀 데이터로 스크리닝"
  - "PER PBR ROE 기준 필터", "안전마진 종목", "딥밸류", "GARP"
  - 사용자가 종목 목록이나 재무 데이터를 주면서 "분석해줘", "점수 매겨줘", "순위 매겨줘"
  - "투자 대가 기준", "거장들의 방식", "워런 버핏처럼", "피터 린치 방식"
  세부 기준은 references/ 파일을 읽어서 적용한다.
---

# Investment Master Stock Screener

투자 대가들(그레이엄, 버핏, 그린블라트, 린치, 슐로스, 클라만, 오닐, 드레만)의 검증된 종목 선정 기준을 정량화하여, 각 종목이 얼마나 기준에 부합하는지 0-100점으로 점수를 산출하는 시스템이다.

## 빠른 트리아지 (어떤 상황인지 먼저 파악)

### 입력 유형
- **스프레드시트 모드**: 사용자가 xlsx/csv 파일을 업로드한 경우 → [Step 1A]
- **MCP 자동 조회 모드**: 사용자가 시장/섹터/조건을 말한 경우 → [Step 1B]
- **종목 리스트 모드**: 사용자가 종목명/코드를 직접 나열한 경우 → [Step 1C]
- **인라인 데이터 모드**: 사용자가 표 형태로 직접 재무 데이터를 제공한 경우 → 바로 Step 2로

### 분석 스타일 선택
사용자가 명시하지 않으면 기본값 사용:
- **전체 분석** (기본): 8개 마스터 스코어 모두 산출
- **가치투자형**: 그레이엄+버핏+그린블라트+클라만+슐로스+린치
- **모멘텀형**: 오닐 CANSLIM + 린치 GARP
- **역발상형**: 드레만 + 클라만 + 슐로스

---

## Step 1A: 스프레드시트 입력 처리

사용자가 파일을 업로드하면:
1. `anthropic-skills:xlsx` 스킬을 활용해 파일을 읽는다
2. 컬럼 자동 인식 (한국어/영어 모두 지원)
3. 상세 컬럼 매핑은 `references/data-sources.md` 참조

---

## Step 1B: MCP 자동 조회 모드

사용자가 "KOSPI 전체", "코스닥 IT 섹터", "시총 1000억 이상" 같은 조건을 말한 경우:

**참조**: `references/data-sources.md` 를 읽고 적절한 MCP를 선택한다.

우선순위:
1. `mcp__kiwoom-openapi__*` — 한국 주식 기본/실시간 데이터
2. `mcp__korea-stock__*` — 재무제표, DART 공시
3. `mcp__krx__*` — KRX 공식 거래 데이터
4. `mcp__naver-stock__*` — 네이버 주식 랭킹/시세
5. `mcp__kis-openapi-mcp__*` — KIS 증권 API

**Sequential Thinking 활용**: 복수의 MCP를 조합해야 할 때 `mcp__sequential-thinking__sequentialthinking`을 사용해 분석 순서를 먼저 계획한다.

---

## Step 1C: 종목 리스트 직접 입력

사용자가 "삼성전자, SK하이닉스, NAVER 분석해줘" 처럼 말하는 경우:
1. 한국 주식이면 `mcp__kiwoom-openapi__kiwoom_stock_basic_info` 로 기본 정보 조회
2. 재무제표는 `mcp__korea-stock__get_financial_statement` 로 조회
3. 미국 주식이면 `stock-analysis` 스킬 참조

---

## Step 2: 마스터별 스코어 산출

**참조**: `references/scoring-system.md` 를 읽어 정확한 점수 계산 공식을 적용한다.

8개 마스터 스코어 (각 0-100점):

| 마스터 | 스코어명 | 핵심 지표 | 상세 기준 파일 |
|--------|---------|-----------|--------------|
| 벤저민 그레이엄 | Graham Score | P/E, P/B, 유동비율, 배당 안정성 | `references/graham-criteria.md` |
| 워런 버핏 | Buffett Score | ROE, FCF, D/E, 이자보상배율 | `references/buffett-criteria.md` |
| 조엘 그린블라트 | Greenblatt Score | EY 랭킹, ROC 랭킹 | `references/greenblatt-criteria.md` |
| 피터 린치 | Lynch Score | PEG, EPS CAGR, D/E | `references/lynch-criteria.md` |
| 월터 슐로스 | Schloss Score | P/Tangible Book, 52주 저점 | `references/schloss-criteria.md` |
| 세스 클라만 | Klarman Score | P/NCAV, P/B 극저평가 | `references/klarman-criteria.md` |
| 윌리엄 오닐 | Momentum Score | EPS 성장, 상대강도, 신고가 | `references/momentum-criteria.md` |
| 데이비드 드레만 | Contrarian Score | P/E 하위, 어닝서프라이즈 | `references/momentum-criteria.md` |

**데이터 없는 지표**: 해당 점수 항목을 제외하고 나머지 항목 가중치를 비례 상향하여 재정규화한다. 결측 데이터가 30% 초과이면 해당 마스터 스코어에 "(데이터 부족)" 표시.

---

## Step 3: 종합 스코어 및 투자 스타일 가중치 적용

| 스타일 | 가중치 |
|--------|--------|
| **균형형** | 8개 마스터 동일 가중치 (각 12.5%) |
| **가치투자형** | 그레이엄 20%+버핏 20%+그린블라트 15%+클라만 15%+슐로스 15%+린치 15% |
| **모멘텀형** | 오닐 40%+린치 30%+버핏 30% |
| **역발상형** | 드레만 40%+클라만 30%+슐로스 30% |

---

## Step 4: 결과 출력

**참조**: `references/output-format.md` 를 읽어 정확한 형식을 적용한다.

결과는 항상:
1. **요약 랭킹 테이블** (종합 점수 내림차순)
2. **종목별 상세 분석** (상위 종목 위주, 사용자 요청 시 전체)
3. **투자 적합성 평가** (강점, 약점, 주의사항)
4. **면책 고지** (투자 조언 아님)

종목 수가 20개 초과이면 먼저 상위 10개 결과를 보여주고 "전체 결과를 보시겠습니까?" 로 확인.

---

## 중요 원칙

- **정확성 우선**: 데이터가 없으면 추측하지 말고 "데이터 없음"으로 표시
- **설명 의무**: 각 점수가 왜 그 값인지 근거 지표를 함께 표시
- **한국 시장 특수성**: 금융/보험/증권 섹터는 그린블라트 Magic Formula 적용 제외 권고
- **상대 평가 병행**: 절대 기준 점수 외에 동종 업계 내 상대 위치도 언급
- **면책 고지 필수**: 모든 결과 말미에 "이 분석은 정보 제공 목적이며 투자 조언이 아닙니다" 추가

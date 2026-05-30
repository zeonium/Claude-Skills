# 데이터 소스 신뢰도 체계 (T1~T4)

## 신뢰도 4단계

| 티어 | 이름 | 신뢰도 | 특징 | Peter 환경 MCP |
|------|------|--------|------|--------------|
| T1 | 공식 공시 | ★★★★★ | 법적 책임 수반, 검증된 수치 | open-dart-reader, sec-edgar, kis MCP |
| T2 | 자본배분 이력 | ★★★★☆ | 행동 기반 (말보다 행동) | kis MCP, yfinance, finviz-plus |
| T3 | 제3자 관찰 데이터 | ★★★☆☆ | 편향 존재, 교차검증 필요 | alphaear-sentiment, Glassdoor 검색, KIPRIS |
| T4 | Scuttlebutt / AI 보조 | ★★☆☆☆ | 가장 낮은 신뢰도, 가설 생성용 | sequential-thinking, brave-search, tavily |

---

## T1: 공식 공시 데이터

### KR 기업 (open-dart-reader MCP)

```python
# 사업보고서 (11011): 연간 종합
corp = opendart_find_corp_code(company_name="삼성전자")
report = opendart_document(corp_code=corp, bsns_year="2024", reprt_code="11011")

# 분기보고서 (11014 / 11013 / 11012)
q_report = opendart_document(corp_code=corp, bsns_year="2024", reprt_code="11014")

# 기업지배구조 보고서 (A001)
cg = opendart_document(corp_code=corp, bsns_year="2024", reprt_code="A001")

# 임원·주요주주 특수관계인 거래 (D001)
insider = opendart_major_shareholders_exec(corp_code=corp, bsns_year="2024")
```

주요 공시 코드:
- `11011`: 사업보고서 (연간)
- `11012`: 반기보고서
- `11013`: 1분기 보고서
- `11014`: 3분기 보고서
- `A001`: 기업지배구조 보고서
- `D001`: 임원·주요주주 소유보고서

### US 기업 (sec-edgar MCP)

```python
# 10-K: 연간보고서 (Item 1A: 위험요인, Item 7: MD&A)
filings = get_recent_filings(ticker="NVDA", form_type="10-K", limit=2)
item1a = get_filing_sections(accession_number=filings[0]["accession"], sections=["1A"])

# DEF 14A: 주주총회 위임장 (경영진 보상)
proxy = get_recent_filings(ticker="NVDA", form_type="DEF 14A", limit=1)

# Form 4: 내부자 거래
insider = get_insider_transactions(ticker="NVDA", days=180)
```

---

## T2: 자본배분 이력 데이터

자본배분은 '말'이 아닌 '행동'으로 평가한다. T1 공시와 교차하여 신뢰도 높음.

### 활용 지표
- 자사주 매입 타이밍 (주가 대비 저점 매입 여부)
- 배당 성장률 지속성
- M&A 후 ROI (인수 3년 후 성과)
- CapEx 집행 vs. 공언 가이던스 대비 실행률

### MCP 활용
```python
# KIS MCP — 항상 env_dv: "real" 필수
buyback = kis_domestic_stock(env_dv="real", tr_id="FHKST01010100", ...)

# yfinance (MCP 툴 사용, bash 직접 설치 금지)
hist = yfinance_get_price_history(symbol="NVDA", period="5y")
info = yfinance_get_ticker_info(symbol="NVDA")
```

---

## T3: 제3자 관찰 데이터

### alphaear-sentiment (ISQ 점수)
- 멀티소스 감성 통합 점수 (0~100)
- 업종 대비 백분위 + 추세 방향성
- D5 차원의 주요 입력값

### Glassdoor / 잡플래닛 검색
- brave-search 또는 tavily로 최근 리뷰 검색
- 독성 키워드 빈도 계산 (D4 입력값)
- 주의: 자발적 작성 편향 → 이직자 리뷰 과대 대표

### KIPRIS (한국 특허)
```python
patents = kipris_kr_search_advanced(
    applicant="삼성전자",
    from_date="20220101",
    to_date="20241231",
    ipc="H01L"
)
```

### USPTO (미국 특허)
- sec-edgar 또는 brave-search로 특허 데이터 검색
- 고피인용 특허: Google Patents Scholar 활용

---

## T4: Scuttlebutt & AI 보조

### sequential-thinking MCP
- 가설 생성, 상충 가능성 탐색
- Pre-mortem 강제 질문 구조화
- **주의**: 이 단계의 결론은 반드시 T1~T3로 교차검증 후 사용

### brave-search / tavily
- 현장 감성, 미확인 정보 수집
- **주의**: 출처 불명확, 환각 의심 → RAG Evidence Tracker로 검증

---

## 활용 규칙

1. **T1 우선**: 정량 수치는 반드시 T1 출처에서 확인
2. **T3 교차검증**: T3 데이터만으로 투자 판단 금지
3. **T4 가설 생성 전용**: T4 데이터는 가설 수립에만 사용, 결론 도출 금지
4. **KIS MCP 규칙**: 모든 KIS MCP 호출에 `env_dv: "real"` 필수
5. **RAG 검증**: AI가 생성한 주장 → `scripts/rag_evidence_tracker.py`로 원문 확인

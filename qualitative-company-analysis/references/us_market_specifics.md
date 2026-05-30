# 미국 시장 특화 분석 가이드

## SEC Form 매핑

| Form | 내용 | 분석 용도 |
|------|------|---------|
| 10-K | 연간보고서 | Item 1A (위험요인), Item 7 (MD&A) |
| 10-Q | 분기보고서 | 분기별 사업 현황 변화 |
| 8-K | 수시보고서 | 중요 사건 (CEO 교체, M&A, 실적 발표) |
| DEF 14A | 주주총회 위임장 | 경영진 보상, 이사회 구성 |
| Form 4 | 내부자 거래 신고 | 임원 지분 매수/매도 |
| Schedule 13D/G | 5% 이상 주주 | 대주주 변동 |

## sec-edgar MCP 호출 패턴

### 10-K 위험요인 추출 (Semantic Diff 입력값)
```python
# 최근 2개년 10-K 가져오기
filings = get_recent_filings(ticker="NVDA", form_type="10-K", limit=2)

# Item 1A 위험요인 추출
item1a_curr = get_filing_sections(
    accession_number=filings[0]["accession_number"],
    sections=["1A"]
)
item1a_prev = get_filing_sections(
    accession_number=filings[1]["accession_number"],
    sections=["1A"]
)
# → 두 텍스트를 파일로 저장 후 semantic_diff_kit.py 실행
```

### 재무 지표 조회
```python
# 핵심 재무 지표
metrics = get_key_metrics(ticker="NVDA")

# 분기/연간 재무제표
financials = get_financials(ticker="NVDA", period="annual", limit=5)
```

### 내부자 거래 분석
```python
# Form 4 내부자 거래
insider = get_insider_transactions(ticker="NVDA", days=180)
summary = get_insider_summary(ticker="NVDA")
```

### 8-K 중요 사건
```python
# 최근 8-K (CEO 교체, M&A 등)
events = analyze_8k(ticker="NVDA", days=90)
```

## Risk Factors YoY Diff 분석 방법

1. **텍스트 추출**: sec-edgar로 Item 1A 섹션 추출
2. **전처리**: 보일러플레이트 헤더/푸터 제거
3. **Semantic Diff 실행**:
   ```bash
   python3 scripts/semantic_diff_kit.py \
     --prev nvda_2023_item1a.txt \
     --curr nvda_2024_item1a.txt \
     --lang en --company NVIDIA --out nvda_diff
   ```
4. **결과 해석**:
   - 신규 문장 (cos < 0.65): 경영진이 새로 인식한 위험
   - 삭제된 문장: 해소된 위험 또는 의도적 은폐 가능성
   - 표현 강도 변화: "may" → "will" 격상은 확실성 증가 신호

## 컨퍼런스콜 Q&A 어조 분석

1. **소스 확보**:
   - sec-edgar MCP의 `earningsTranscript` 도구
   - 또는 financial-modeling-prep MCP
2. **어조 분석**:
   ```bash
   python3 scripts/tone_analysis.py \
     --input nvda_q4_transcript.txt --lang en
   ```
3. **Loughran-McDonald 사전**: Negative/Positive/Uncertainty/Litigious 단어 분류
4. **Moving Targets 분석**:
   ```bash
   python3 scripts/moving_targets_detector.py \
     --transcripts q1.txt q2.txt q3.txt q4.txt \
     --quarters FY24Q1 FY24Q2 FY24Q3 FY24Q4 --lang en
   ```

## DEF 14A 경영진 보상 분석

중점 확인 항목:
1. **CEO 총보상 구성**: 기본급 vs. 장기 인센티브(주식) 비율
2. **성과 지표 연동**: EPS/TSR 기반 vs. 조작 가능 지표 기반
3. **Pay Ratio**: CEO 보상 / 중간 직원 보상
4. **Say-on-Pay 투표**: 70% 미만 반대는 적신호

high pay ratio + 주가 하락 = D3 강력 하향 요인

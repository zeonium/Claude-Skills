# 한국 시장 특화 분석 가이드

## DART 공시 코드 체계

| 코드 | 문서명 | 분석 용도 |
|------|--------|---------|
| 11011 | 사업보고서 (연간) | 전체 사업 현황, 위험요인, 경영진 현황 |
| 11012 | 반기보고서 | H1 중간 점검 |
| 11013 | 1분기보고서 | Q1 단기 모니터링 |
| 11014 | 3분기보고서 | Q3 단기 모니터링 |
| A001 | 기업지배구조 보고서 | CoE 준수 여부, 이사회 독립성 |
| D001 | 임원·주요주주 소유보고서 | 내부자 지분 변동 |
| F007 | 최대주주 변경 | 지배구조 리스크 탐지 |

## open-dart-reader MCP 호출 패턴

### 기본 회사 정보 조회
```python
# 기업 코드 조회
corp = opendart_find_corp_code(company_name="삼성전자")
# 또는
corp = opendart_resolve_corp(query="005930")  # 종목코드로 조회

# 회사 기본 정보
info = opendart_company(corp_code=corp["corp_code"])
```

### 사업보고서 특정 섹션 추출
```python
# 위험요인 섹션 추출 (Semantic Diff 입력값)
risk = opendart_extract_document_sections(
    corp_code="00126380",
    bsns_year="2024",
    reprt_code="11011",
    section_keywords=["사업위험", "위험요소", "주요 위험"]
)
```

### 재무제표 조회
```python
# 연결 재무제표
fs = opendart_finstate(
    corp_code="00126380",
    bsns_year="2024",
    reprt_code="11011",
    fs_div="CFS"  # CFS: 연결, OFS: 별도
)
```

### 임원 내부자 거래
```python
insider = opendart_major_shareholders_exec(
    corp_code="00126380",
    bsns_year="2024",
    reprt_code="11011"
)
```

## 기업지배구조 보고서 CoE 분석

CoE(기업지배구조 핵심원칙) 주요 점검 항목:
1. **주주 권리 보호**: 집중투표제, 전자투표제 채택 여부
2. **이사회 독립성**: 사외이사 비율 >= 50%, 이사회 내 위원회 설치
3. **감사 체계**: 감사위원회 전원 사외이사 여부
4. **보상 투명성**: 임원 보상 개별 공시 여부
5. **주주 소통**: IR 정책, 공정공시 이력

미준수 항목 -> D3 점수 하향 요인 (항목당 -3~5점)

## 한국 시장 한계 및 보정 방법

### 한계
- 컨퍼런스콜 Q&A: 한국어 전용, 영어 분석 도구 직접 적용 불가
- Glassdoor: 글로벌 기업 리뷰 위주 -> 잡플래닛 대체 사용
- 단기 실적 압박: 분기 단위 숫자 게임이 더 심함

### 보정 방법
- tone_analysis.py `--lang ko` 옵션으로 KR-FinBert 활성화
- 잡플래닛 리뷰 -> brave-search로 최근 리뷰 수집
- KIPRIS로 특허 분석 (USPTO 대체)
- ECOS MCP로 산업별 거시경제 데이터 보완

## KIS MCP 활용 규칙

**중요**: 모든 KIS MCP 호출에 `env_dv: "real"` 필수

```python
# 일봉 OHLCV
candle = kis_domestic_stock(
    env_dv="real",
    tr_id="FHKST01010100",  # 주식 현재가 조회
    ...
)

# 해외주식 (US)
us_stock = kis_overseas_stock(
    env_dv="real",
    tr_id="HHDFS00000300",
    ...
)
```

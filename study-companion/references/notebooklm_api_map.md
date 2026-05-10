# NotebookLM MCP API 매핑표

Study Companion 스킬이 사용하는 NotebookLM MCP 도구 매핑.  
모든 도구 이름은 `notebooklm__` 접두사를 사용한다.

## 9차원 자료 ↔ MCP 도구 매핑

| 차원 | MCP 도구 | 주요 파라미터 | 비고 |
|------|---------|------------|------|
| Summary L1/L2 | `notebooklm__notebook_query` | prompt=SUMMARY_3LAYER_TPL | JSON 파싱 필요 |
| Summary L3 | `notebooklm__report_create` | — | 심화 요약 모드 |
| Mind Map | `notebooklm__mind_map_create` | scope=chapter_title | studio_status 폴링 필요 |
| Flashcards | `notebooklm__flashcards_create` | — | 15장 권장 |
| Quiz (형성평가) | `notebooklm__quiz_create` | — | 난이도 미지원 시 prompt에 명시 |
| Examples | `notebooklm__notebook_query` | prompt=EXAMPLES_TPL | — |
| Socratic | `notebooklm__notebook_query` | prompt=SOCRATIC_TPL | — |
| Application | `notebooklm__notebook_query` | prompt=APPLICATION_TPL | — |
| Cross-Ref | `notebooklm__research_start` → `notebooklm__research_import` | — | 외부 자료 탐색 |
| Audio Overview | `notebooklm__audio_overview_create` | — | 통근·이동 시 활용 |
| Slide Deck | `notebooklm__slide_deck_create` | — | 마일스톤 보고용 |
| Infographic | `notebooklm__infographic_create` | — | 시각 요약 |

## 노트북 관리 도구

| 용도 | MCP 도구 | 설명 |
|------|---------|------|
| 노트북 생성 | `notebooklm__notebook_create` | 제목 + 소스 목록 |
| URL 소스 추가 | `notebooklm__notebook_add_url` | — |
| 텍스트 소스 추가 | `notebooklm__notebook_add_text` | — |
| Drive 소스 추가 | `notebooklm__notebook_add_drive` | Google Drive URL |
| 노트북 설명 조회 | `notebooklm__notebook_describe` | suggested_topics 반환 |
| 노트북 목록 | `notebooklm__notebook_list` | — |
| 노트북 쿼리 | `notebooklm__notebook_query` | 자유형식 질문 |

## 비동기 Studio 도구

| 용도 | MCP 도구 | 폴링 여부 |
|------|---------|---------|
| Studio 상태 확인 | `notebooklm__studio_status` | 필요 (10초 간격, 최대 120초) |
| Studio 삭제 | `notebooklm__studio_delete` | — |

## 폴링 패턴

```
1. 비동기 생성 도구 호출 → studio_id 반환
2. notebooklm__studio_status(studio_id) 호출
3. status == "complete" → 완료
4. status == "in_progress" → 10초 대기 후 재시도
5. 120초 초과 → 사용자 알림 + 백그라운드 큐 등록
```

## 에러 처리 정책

- **MCP 연결 실패**: "NotebookLM이 연결되어 있지 않습니다. Claude Desktop 설정을 확인해 주세요." 안내 후 종료
- **Transient 오류**: 최대 3회 재시도 (2→4→8초 지수 백오프)
- **Studio 타임아웃**: 다음 차원으로 진행, 타임아웃된 자료는 나중에 백그라운드 생성
- **콘텐츠 없음**: notebook_query 결과가 비어있으면 "이 섹션에 대한 자료를 찾을 수 없습니다" 안내

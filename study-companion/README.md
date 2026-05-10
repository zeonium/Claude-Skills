# Study Companion Skill — 개발자 가이드

> **버전**: v2.3 — Long-Term Memory Edition | **런타임**: Claude Desktop / Code (Windows·macOS)  
> **MCP 의존**: `notebooklm`, `memory`, `obsidian-mcp-tools` (선택: `sequential-thinking`)

---

## 아키텍처 개요

```
SKILL.md                    ← Claude가 읽는 런타임 매뉴얼
scripts/                    ← Python 모듈 (로직 구현)
  models.py                 ← Pydantic 데이터 모델
  storage.py                ← 로컬 JSON 파일 I/O
  notebooklm_adapter.py     ← NotebookLM MCP 추상화
  memory_adapter.py         ← Memory MCP Knowledge Graph
  note_persistence.py       ← Filesystem MCP → Obsi_Sapi
  onboarding.py             ← Phase 1: 온보딩
  curriculum.py             ← Phase 2: 시러버스
  daily_session.py          ← Phase 3: 일일 세션
  content_generator.py      ← 9차원 자료 디스패처
  assessment.py             ← 형성평가 + IRT
  srs.py                    ← FSRS-Lite SRS 엔진
  progress_tracker.py       ← 대시보드
  utils.py                  ← 공통 헬퍼
references/
  prompts.md                ← 9개 프롬프트 템플릿
  schemas.md                ← 데이터 스키마 명세
  notebooklm_api_map.md     ← MCP 도구 매핑표
  educational_theory.md     ← 교육 이론 배경
  workflow_diagrams.md      ← Mermaid 다이어그램
assets/
  templates/                ← Obsidian 노트 템플릿
  obsi_sapi_init/           ← Obsi_Sapi 볼트 시드 파일
tests/                      ← pytest 단위 테스트
```

---

## 테스트 커버리지

| 모듈 | 테스트 파일 | 커버 항목 |
|------|-----------|---------|
| `models.py` | `test_models.py` | 모델 기본값, JSON 직렬화, ID 생성 |
| `curriculum.py` | `test_curriculum.py` | 시간 추정, 시러버스 빌드, 재계획 |
| `srs.py` | `test_srs.py` | FSRS 스케줄링, 평가 파싱, 경계값 |

---

## 확장 포인트

| 기능 | 현재 구현 | 확장 방법 |
|------|---------|---------|
| SRS 엔진 | FSRS-Lite | `fsrs-py` 라이브러리 교체 (인터페이스 동일) |
| 노트 백엔드 | Obsidian (Filesystem MCP) | `NotePersistenceAdapter` 서브클래스 |
| 능력 추정 | 간이 BKT | 완전 IRT 모델 교체 |
| 학습 스타일 | 수집만 | Felder-Silverman 기반 커리큘럼 조정 (v1.3) |

---

## 마일스톤 로드맵

| 버전 | 상태 | 내용 |
|------|------|------|
| v1.0 | ✅ | 기본 골격 + 어댑터 레이어 |
| v1.1 | ✅ | 온보딩 + 커리큘럼 + 일일 세션 |
| v1.2 | ✅ | Obsi_Sapi 전용 볼트 격리 |
| v2.0 | ✅ | obsidian-mcp-tools 전환·다중 교재 |
| v2.1 | ✅ | 챕터 퀴즈 + 시험 대비 |
| v2.2 | ✅ | 핵심 개념 시각화 (Mermaid + Sequential Thinking) |
| **v2.3** | ✅ | **Long-Term Memory Edition** — 비유·은유·실제 사례·기억술 3차원 추가 (12차원), `07_DeepEncoding/` 폴더 신설, Dual Coding · Story-based Memory · Method of Loci 이론 적용 |
| v2.4 | 예정 | 학습 스타일 기반 커리큘럼 조정 |

---

## v2.3 변경 요약 (Long-Term Memory Edition)

**무엇이 바뀌었나**:
- 9차원 → **12차원** 학습자료 (`analogy`, `case_study`, `memory_hook` 추가)
- 새 의도 `MEMORIZE` — "비유로 설명해줘", "사례 보여줘", "외우기 어려워" 트리거
- Acquire 단계에서 핵심 개념마다 비유·사례·기억훅 자동 동반 (학습자가 "빠른 모드" 선택 시 비활성)
- Obsidian 볼트에 `07_DeepEncoding/{book-title}/` 폴더 신설 — "기억의 사전" 역할
- 새 프롬프트 3종 (`§ 6.13 ANALOGY_METAPHOR_TPL`, `§ 6.14 CASE_STUDY_TPL`, `§ 6.15 MEMORY_HOOK_TPL`)
- 새 reference: `references/analogy_library.md` (도메인별 비유 카탈로그 + 한계 체크리스트)
- `educational_theory.md` § 7~11 — Dual Coding, Elaborative Encoding, Story-based Memory, Method of Loci 추가

**왜**: 단순 정의 암기는 며칠 내 잊혀진다. 비유는 추상을 구체로 변환하고(Dual Coding), 사례는 서사로 묶고(Story-based Memory), 기억술은 다중 인출 단서를 제공한다(Method of Loci). 세 차원이 동시에 작동할 때 학습 내용은 비로소 학습자의 장기기억에 새겨진다.

**호환성**: 기존 v2.2 사용자의 데이터는 모두 호환. `07_DeepEncoding/` 폴더는 첫 세션 시 자동 생성. `LearnerProfile`에 `familiar_domain`, `analogy_domains_used`, `deep_encoding_enabled` 필드 추가 (기본값 호환).

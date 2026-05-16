# TRIZ 모순 행렬 호출 참조

P-STAR S4 M-패턴 분석에서 모순 파라미터가 특정되면,
`triz-patent-analyzer` 스킬의 스크립트를 직접 재활용하여 TRIZ 원리를 검증한다.
별도 구현 없이 기존 스크립트를 호출하므로 중복이 없다.

## 호출 방법

```bash
python3 ~/.claude/skills/triz-patent-analyzer/scripts/triz_matrix_solver.py \
  --improving "<개선 파라미터 번호>" \
  --worsening "<악화 파라미터 번호>" \
  --matrix_file ~/.claude/skills/triz-patent-analyzer/references/matrix_data.json
```

## 파라미터 번호 참조

39가지 공학 변수는 `~/.claude/skills/triz-patent-analyzer/references/39_parameters.md`에 있다.
필요 시 Read 도구로 로드한다.

## 반환값 처리

| status | 의미 | 처리 |
|--------|------|------|
| `success` | 정상 | 반환된 원리 번호를 M-패턴 TRIZ 원리와 대조 |
| `success_reverse_lookup` | 역방향 조회 성공 | 결과 사용, 신중 검토 표시 |
| `no_matrix_intersection` | 교차점 없음 | 인접 변수(±1~2) 재시도 또는 생략 |
| `error_*` | 오류 | 해당 M-패턴의 TRIZ 원리는 프레임워크 참조값으로 대체 |

## M-패턴별 대표 모순 파라미터 (참고)

| M-패턴 | 개선 파라미터 | 악화 파라미터 | 주요 TRIZ 원리 |
|--------|-------------|-------------|-------------|
| M-1 | #9 속도 또는 #14 강도 | #1 이동물체 무게 | #2 #28 #13 |
| M-2 | 도메인별 가변 | 도메인별 가변 | #15 #10 #1 |
| M-3 | #30 물체에 작용하는 힘 | #14 강도 | #22 #35 #40 |
| M-4 | #21 동력 | #19 에너지 사용 | #35 #3 #28 |
| M-5 | #35 적응성·만능성 | #14 강도 | #28 #6 #37 |
| M-7 | #39 생산성 | #19 에너지 사용 | #15 #10 #3 |

> 이 표는 참고용이다. 실제 분석에서는 특허의 구체적 모순을 기반으로 파라미터를 새로 정의한다.

## 발명 원리 상세 참조

특정 원리의 상세 설명이 필요하면:
```
Read ~/.claude/skills/triz-patent-analyzer/references/40_principles.md
```
해당 원리 번호 섹션을 참조한다.

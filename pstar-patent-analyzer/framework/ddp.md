# DDP + CD-DDP

## DDP — Dominant Design Pattern (다건 전용)

단일 도메인 내 복수 특허에서 반복 등장하는 TRIZ 원리.

### 등급 기준

| 등급 | 기준 | 의미 |
|------|------|------|
| **Strong** | ≥ 3건 | 해당 도메인의 지배적 설계 원리 |
| **Moderate** | = 2건 | 유의미한 패턴, 추가 귀납 필요 |
| **One-off** | = 1건 | 단발 관찰, 가설 단계 |
| **White Space** | = 0건 | 미탐색 혁신 공간 — IP 기회 |

### DDP 분석 절차 (다건 모드 S5)

1. 분석 대상 특허들의 M-패턴 목록 취합
2. 각 TRIZ 원리별 등장 빈도 집계
3. Strong/Moderate/One-off/White Space 분류
4. White Space → IP 기회 영역으로 제안

---

## CD-DDP — Cross-Domain Dominant Design Pattern

전체 귀납 특허(현재 15건)에서 도메인 횡단적으로 등장하는 TRIZ 원리.

`knowledge/cd_ddp_ledger.md`가 최신 집계 원장이다. 분석 완료 후 반드시 갱신한다.

### CD-DDP 격상 기준

| 격상 | 조건 |
|------|------|
| One-off → Moderate | 2번째 귀납 확인 |
| Moderate → Strong | 3번째 귀납 확인 |
| LevelC M-패턴 → LevelB | 추가 도메인 확인 |
| LevelB M-패턴 → LevelA | 충분한 도메인 확인 (M-4: 6도메인) |

### CD-DDP 해석법

- **★★★ Strong 원리** (#3 #15 #35 #40 #13): 특허 혁신의 보편적 메커니즘. 새 특허도 이 원리를 활용할 가능성 높음.
- **Moderate 원리** (#17 #6 #1 #10): 특정 기술군에서 유효. 추가 귀납 주시.
- **One-off 원리** (#28 #25 #4 #2): 아직 패턴 미확정. 발견 시 가설 등록.
- **White Space**: 39가지 TRIZ 원리 중 아직 귀납 미확인 원리 → 혁신 기회.

---

## DDP 출력 형식 (다건 모드 S5)

```
[도메인] DDP 분석:
  Strong  (≥3건): #원리1(이름), #원리2(이름)
  Moderate (2건): #원리3(이름)
  One-off  (1건): #원리4(이름)
  White Space: #원리X, #원리Y (IP 기회)

CD-DDP 원장 변경 예상:
  #원리N: [현재 등급] → [갱신 후 등급] (이 특허 기여)
```

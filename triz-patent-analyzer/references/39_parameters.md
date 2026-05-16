# TRIZ 39가지 공학 변수 (Engineering Parameters)

스크립트 호출 시 변수 번호를 사용하십시오. 자연어 입력도 지원되지만 번호가 가장 정확합니다.

## 변수 목록

| 번호 | 한국어 변수명 | 영어 변수명 |
|------|--------------|-------------|
| 1 | 이동 물체의 무게 | Weight of moving object |
| 2 | 정지 물체의 무게 | Weight of stationary object |
| 3 | 이동 물체의 길이 | Length of moving object |
| 4 | 정지 물체의 길이 | Length of stationary object |
| 5 | 이동 물체의 면적 | Area of moving object |
| 6 | 정지 물체의 면적 | Area of stationary object |
| 7 | 이동 물체의 부피 | Volume of moving object |
| 8 | 정지 물체의 부피 | Volume of stationary object |
| 9 | 속도 | Speed |
| 10 | 힘 | Force |
| 11 | 응력 또는 압력 | Stress or pressure |
| 12 | 형상 | Shape |
| 13 | 구조 안정성 | Stability of the object's composition |
| 14 | 강도 | Strength |
| 15 | 이동 물체의 작동 지속 시간 | Duration of action by a moving object |
| 16 | 정지 물체의 작동 지속 시간 | Duration of action by a stationary object |
| 17 | 온도 | Temperature |
| 18 | 조명 강도 | Illumination intensity |
| 19 | 이동 물체의 에너지 소비 | Use of energy by moving object |
| 20 | 정지 물체의 에너지 소비 | Use of energy by stationary object |
| 21 | 동력 | Power |
| 22 | 에너지 손실 | Loss of energy |
| 23 | 물질 손실 | Loss of substance |
| 24 | 정보 손실 | Loss of information |
| 25 | 시간 손실 | Loss of time |
| 26 | 물질의 양 | Quantity of substance / the matter |
| 27 | 신뢰성 | Reliability |
| 28 | 측정 정확도 | Measurement accuracy |
| 29 | 제조 정밀도 | Manufacturing precision |
| 30 | 물체에 작용하는 유해 효과 | Object-generated harmful side effects |
| 31 | 해로운 부작용 | Harmful side effects |
| 32 | 제조 용이성 | Ease of manufacture |
| 33 | 작동 편의성 | Ease of operation |
| 34 | 수리 편의성 | Ease of repair |
| 35 | 적응성 또는 다양성 | Adaptability or versatility |
| 36 | 장치 복잡성 | Device complexity |
| 37 | 제어 및 측정의 어려움 | Difficulty of detecting and measuring |
| 38 | 자동화 정도 | Extent of automation |
| 39 | 생산성 | Productivity |

---

## 변수 선택 가이드

### 개선 변수 (Improving Parameter)
발명이 향상시키려는 속성입니다. "무엇을 더 좋게 만들려는가?"에 해당합니다.
- 더 강하게 → #14 강도
- 더 빠르게 → #9 속도
- 더 가볍게 → #1 또는 #2 무게
- 더 오래 → #15 또는 #16 지속 시간
- 더 정밀하게 → #28 측정 정확도 또는 #29 제조 정밀도
- 더 안전하게 → #27 신뢰성
- 더 많이 생산 → #39 생산성

### 악화 변수 (Worsening Parameter)
개선으로 인해 희생되는 속성입니다. "개선하면 무엇이 나빠지는가?"에 해당합니다.
- 더 무거워짐 → #1 또는 #2 무게
- 더 복잡해짐 → #36 장치 복잡성
- 더 많은 에너지 소비 → #19, #20, #21 에너지 관련
- 더 불안정해짐 → #13 구조 안정성
- 제조가 어려워짐 → #32 제조 용이성
- 수명 단축 → #15 또는 #16 지속 시간

### 일반적인 모순 패턴 예시

| 개선하려는 것 | 악화되는 것 | 개선 변수 | 악화 변수 |
|--------------|------------|-----------|-----------|
| 강도 향상 | 무게 증가 | #14 | #1 |
| 속도 향상 | 안정성 저하 | #9 | #13 |
| 속도 향상 | 복잡성 증가 | #9 | #36 |
| 정밀도 향상 | 제조 복잡성 증가 | #29 | #36 |
| 생산성 향상 | 에너지 소비 증가 | #39 | #21 |
| 신뢰성 향상 | 장치 복잡성 증가 | #27 | #36 |
| 소형화 | 강도 저하 | #7 | #14 |
| 자동화 | 장치 복잡성 증가 | #38 | #36 |

### 소프트웨어/IT 도메인 매핑 가이드

물리적 발명 외 소프트웨어/IT 특허도 TRIZ로 분석 가능합니다:

| IT 개념 | 대응 TRIZ 변수 |
|---------|---------------|
| 처리 속도 | #9 속도 |
| 메모리/저장용량 | #7 또는 #8 부피 |
| 시스템 안정성 | #13 구조 안정성 |
| 보안 수준 | #27 신뢰성 |
| 코드 복잡도 | #36 장치 복잡성 |
| 정보 정확도 | #28 측정 정확도 |
| 응답 시간 | #25 시간 손실 |
| 처리량(Throughput) | #39 생산성 |
| 에너지 효율 | #22 에너지 손실 |

# 교육 이론 배경

Study Companion 스킬에 적용된 교육 이론 및 설계 원칙.

## 1. Bloom의 분류 체계 (Revised Bloom's Taxonomy)

| 수준 | 한국어 | 동사 예시 |
|------|-------|---------|
| Remember | 기억 | 정의한다, 열거한다, 확인한다 |
| Understand | 이해 | 설명한다, 요약한다, 분류한다 |
| Apply | 적용 | 계산한다, 사용한다, 해결한다 |
| Analyze | 분석 | 비교한다, 분류한다, 구분한다 |
| Evaluate | 평가 | 판단한다, 비판한다, 정당화한다 |
| Create | 창조 | 설계한다, 제안한다, 구성한다 |

각 챕터의 `bloom_objectives`는 이 6단계를 기반으로 작성된다.  
진단 평가 문항은 Remember~Apply에 집중, 마일스톤 평가는 Apply~Evaluate까지 확장.

## 2. 4-Stage 학습 루프 근거

| Stage | 이론 기반 | 효과 |
|-------|---------|------|
| Activate (회상 점화) | Testing Effect (Roediger & Karpicke, 2006) | 인출 연습이 장기 기억 강화 |
| Acquire (신규 학습) | Cognitive Load Theory (Sweller, 1988) | 한 차원씩 제시로 인지 부하 분산 |
| Apply (문제 풀이) | Desirable Difficulties (Bjork, 1994) | 적절한 어려움이 학습 촉진 |
| Reflect (메타인지) | Metacognition (Flavell, 1979) | 자기 모니터링이 학습 효율 향상 |

## 3. 간격 반복 학습 (Spaced Repetition)

FSRS-Lite는 Forgetting Curve (Ebbinghaus, 1885) 기반.

```
기억 유지율 R = e^(-t/S)
t: 마지막 복습 후 경과 시간
S: stability (안정성)
목표 R = 0.9 (90% 기억 확률 유지)
```

복습 인터벌 I = S × ln(R_target) / ln(0.9)

## 4. 9차원 학습자료 설계 원칙

| 차원 | 이론 |
|------|------|
| Summary | Generative Learning (Wittrock, 1989) |
| Mind Map | Dual Coding Theory (Paivio, 1971) |
| Flashcards | Active Recall + Spaced Repetition |
| Examples | Worked Example Effect (Sweller, 1985) |
| Socratic | Socratic Method + Zone of Proximal Development |
| Assessment | Formative Assessment (Black & Wiliam, 1998) |
| Application | Transfer-Appropriate Processing |
| Cross-Ref | Elaborative Interrogation |
| Reflection | Metacognitive Monitoring |

## 5. 간이 IRT (Item Response Theory)

능력 추정 θ 업데이트:
- 정답: +0.2σ (학습 영향 계수 0.2)
- 오답: -0.2σ
- θ 범위: -3.0 ~ +3.0 (표준정규 가정)
- 초기 θ = 진단 점수 × 사전지식 가중치 (onboarding.estimate_theta_from_diagnostic)

## 6. Felder-Silverman 학습 스타일 (선택 기능)

4축으로 학습 스타일 측정 (LearnerProfile.learning_style에 저장):
- Active ↔ Reflective
- Sensing ↔ Intuitive  
- Visual ↔ Verbal
- Sequential ↔ Global

현재 v1.0에서는 수집만 하고 커리큘럼 조정에는 미적용 (v1.3 예정).

---

## 7. Dual Coding Theory (Paivio, 1971) — v2.3

언어 정보와 시각 정보가 별개의 인코딩 시스템에 저장되며, 두 채널이 동시에 활성화될 때
회상률이 단일 모달리티 대비 약 **2배** 강화된다는 이론.

| 단일 인코딩 | 이중 인코딩 |
|-----------|-----------|
| "Bayes 정리는 사후확률을 사전확률로 갱신하는 공식이다" (언어만) | 언어 정의 + "스팸 필터가 새 메일을 분류하며 학습하는 모습" (시각·동작 이미지 동반) |

**비유·은유는 추상 개념을 구체 이미지로 변환하는 가장 효율적인 도구**이므로 Dual Coding의 핵심 활용처다.  
Study Companion v2.3의 `analogy` 차원은 모든 핵심 개념에 대해 강제로 시각 이미지를 결부시켜 이중 인코딩을 보장한다.

추가 근거:
- Clark & Paivio (1991), "Dual Coding Theory and Education"
- Mayer (2009), Cognitive Theory of Multimedia Learning — 텍스트+이미지 동시 제시가 텍스트만보다 학습 전이 효과 높음

---

## 8. Levels of Processing & Elaborative Encoding (Craik & Lockhart, 1972) — v2.3

기억의 강도는 정보 저장 시간이 아니라 **처리의 깊이(depth of processing)** 에 의해 결정된다.

| 처리 수준 | 예시 | 회상률 |
|---------|------|------|
| 표면 (shallow) | 글자 모양·발음 인식 | 낮음 |
| 중간 (intermediate) | 의미 파악·정의 암기 | 중간 |
| 심층 (deep, elaborative) | 기존 지식과 연결·자기 경험 결부·비유 생성 | 높음 |

**Elaborative Encoding**은 새 정보를 기존 의미망에 풍부하게 연결할수록 회상이 강화되는 메커니즘이다.  
비유는 "친숙한 도메인의 풍부한 의미망 ↔ 새 개념"의 교량 역할을 하므로 elaboration의 가장 효과적인 형태.

Study Companion v2.3은 학습자의 친숙 도메인(`familiar_domain`)을 온보딩 시 수집해
모든 비유 생성에 활용함으로써 elaborative depth를 최대화한다.

---

## 9. Story-based Memory (Bower & Clark, 1969) — v2.3

무관한 단어 12개 목록을 두 그룹에 제시한 실험:
- 통제군 (단순 암기): 회상률 약 **13%**
- 실험군 (이야기로 묶어 암기): 회상률 약 **93%**

→ **이야기 구조가 회상을 약 7배 강화**한다는 고전적 결과.

이유:
1. 이야기는 인과 관계로 항목들을 결합 → 한 항목이 다음 항목의 인출 단서가 됨
2. 등장인물·배경이 기억의 "맥락 단서(context cue)" 제공
3. 감정·갈등·해결 구조가 편도체 활성화 → 정서 기억으로 강화

Study Companion v2.3의 `case_study` 차원은 이 효과를 활용해 추상 개념을 
시간·장소·인물이 등장하는 서사로 인코딩한다.

추가 근거:
- Schank & Abelson (1995), Knowledge and Memory: The Real Story
- Heath & Heath (2007), Made to Stick — "Stories as Simulators"

---

## 10. Method of Loci & Mnemonics — v2.3

고대 그리스·로마 수사학자들이 긴 연설을 외우기 위해 사용한 기억술.  
"기억의 궁전"이라 불리며, 학습자가 잘 아는 공간을 머릿속에서 걸으며 각 위치에 외울 항목을 배치하는 방식.

**작동 원리**:
1. 공간 기억은 진화적으로 가장 강한 기억 시스템 (생존에 직결)
2. 위치 단서가 인출 시 자동으로 활성화 → 항목 회상 트리거
3. 작업기억의 7±2 한계를 우회 — 위치 자체가 외부 저장소 역할

**경험적 효과** (Wagner et al., 2017, Neuron):
- 4주간 매일 30분 기억궁전 훈련 → 단어 목록 회상률이 약 26개에서 62개로 향상
- 신경 영상에서 해마-신피질 연결 패턴 변화 관찰

**기타 기억술 (보조)**:
- **두문자어 (Acronym)**: "ROY G BIV" (무지개 7색) — 의미 단위로 청크화
- **첫글자 문장 (Acrostic)**: "수금지화목토천해" → 행성 순서
- **이야기 사슬 (Story Method)**: § 9 참조
- **이상함 효과 (Bizarreness Effect)**: 이상하고 충격적인 이미지가 평범한 이미지보다 잘 기억됨 (McDaniel & Einstein, 1986)

Study Companion v2.3의 `memory_hook` 차원은 두문자·이야기·기억궁전을 
한 패키지로 묶어 학습자에게 제공하여 다중 인출 경로를 확보한다.

---

## 11. v2.3 차원과 이론 매핑 요약

| v2.3 차원 | 한국어 | 핵심 이론 |
|---------|------|---------|
| `analogy` | 비유·은유 | Dual Coding (§ 7) + Elaborative Encoding (§ 8) |
| `case_study` | 실제 사례 | Story-based Memory (§ 9) |
| `memory_hook` | 기억 훅 | Method of Loci & Mnemonics (§ 10) |

세 차원은 상호보완적 인지 경로를 동시에 활성화하므로 한 개념에 대한 
**다중 인출 단서(multiple retrieval cues)** 를 제공한다.  
한 단서가 작동하지 않을 때 다른 단서가 회상을 보장하여 기억의 견고성(robustness)이 강화된다.

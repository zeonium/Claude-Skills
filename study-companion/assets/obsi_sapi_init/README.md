# Obsi_Sapi — Study Companion 전용 Obsidian 볼트

이 볼트는 **Study Companion Claude Desktop 스킬**이 학습 노트를 자동 저장하는 전용 볼트입니다.

## 설치 및 등록

1. Obsidian 앱 실행
2. 왼쪽 하단 금고(Vault) 아이콘 클릭
3. **"Open folder as vault"** 선택
4. `D:\Obsi\Obsi_Sapi` 폴더 선택
5. 볼트 이름: `Obsi_Sapi`

## 권장 Obsidian 플러그인

| 플러그인 | 용도 |
|---------|------|
| **Spaced Repetition** | 05_Flashcards 플래시카드 복습 |
| **Dataview** | 학습 통계 쿼리 |
| **Templater** | 99_Templates 자동화 |
| **Calendar** | 02_Sessions 날짜 뷰 |

## 볼트 폴더 구조

| 폴더 | 내용 |
|------|------|
| `01_Books/` | 교재별 인덱스 노트 |
| `02_Sessions/` | 일일 학습 세션 노트 |
| `03_Milestones/` | 주차별 마일스톤 보고서 |
| `04_Concepts/` | 개념 노트 (백링크 허브) |
| `05_Flashcards/` | SRS 플래시카드 |
| `06_Reflections/` | 메타인지 일지 |
| `99_Templates/` | Templater 호환 템플릿 |

## 주의사항

- 폴더 이름(01_Books, 02_Sessions 등)을 변경하면 자동 저장이 중단될 수 있습니다.
- 노트 저장에 `obsidian-mcp-tools` MCP를 사용합니다. INSTALL.md의 2단계를 참조하세요.
- 이 볼트의 파일은 Study Companion 스킬이 관리합니다. 직접 편집은 가능하나 frontmatter를 수정하면 동기화가 깨질 수 있습니다.

## 데이터 백업

볼트 전체를 정기적으로 백업하는 것을 권장합니다:

```powershell
# 예시: 주간 백업
Compress-Archive -Path "D:\Obsi\Obsi_Sapi" -DestinationPath "D:\Backup\Obsi_Sapi_$(Get-Date -Format 'yyyy-MM-dd').zip"
```

# Study Companion Skill — 설치 가이드

> **지원 플랫폼**: Windows 10/11 x64 및 macOS Monterey 이상  
> **Skill 버전**: v2.3 — Long-Term Memory Edition  
> **소요 시간**: 약 15분

## v2.3 신규 기능 한눈에

이번 버전은 학습 내용을 **장기기억**에 새기기 위한 인지심리학 기반 자료 3종을 추가했습니다.

| 신규 차원 | 한국어 | 트리거 발화 예시 |
|---------|------|--------------|
| `analogy` | 🌉 비유·은유 | "비유로 설명해줘", "쉽게 설명해줘" |
| `case_study` | 📜 실제 사례 | "사례 보여줘", "역사적 예 알려줘" |
| `memory_hook` | 🔗 기억 훅 | "외우기 어려워", "기억술", "암기 비법" |

**자동 동반**: Acquire 단계에서 새 핵심 개념이 등장할 때마다 위 3개 자료가 자동 생성·동반 출력됩니다. "빠른 모드", "간단히"라고 말씀하시면 비활성됩니다.

**저장 위치**: 챕터 종료 시 비유·사례·기억훅이 통합되어 Obsidian 볼트의  
`07_DeepEncoding/{book-title}/{ChXX}_{chapter-title}_심화기억노트.md` 파일로 저장됩니다.

---

> 아래에서 해당 플랫폼 섹션으로 이동하세요:  
> - [Windows 설치](#windows-설치)  
> - [macOS 설치](#macos-설치)

---

## Windows 설치

---

## 1단계: 사전 준비

### 1.1 Python 3.11+ 설치 확인

```powershell
python --version
# Python 3.11.x 이상이어야 함
```

없으면 [python.org](https://python.org)에서 설치.

### 1.2 Claude Desktop 설치 확인

Claude Desktop이 설치·실행 중이어야 합니다.

### 1.3 필수 MCP 연결 확인

Claude Desktop에 다음 MCP가 연결되어 있어야 합니다:

| MCP | 용도 | 연결 상태 확인 |
|-----|------|-------------|
| `notebooklm` | 학습 자료 생성 | Claude에서 "노트북 목록 보여줘" |
| `memory` | 진도 영구 저장 | Claude에서 "메모리 그래프 확인" |
| `obsidian-mcp-tools` | Obsidian 볼트 노트 저장 | 아래 2단계 참조 |

---

## 2단계: obsidian-mcp-tools MCP 설정

### 2.1 Obsidian Local REST API 플러그인 설치

Obsidian 앱에서:
1. **설정(⚙) → 커뮤니티 플러그인 → 찾아보기**
2. `Local REST API` 검색 후 설치 및 활성화
3. **설정 → Local REST API** 에서 API 키 확인 또는 생성

### 2.2 Claude Desktop 설정에 obsidian-mcp-tools 추가

`%APPDATA%\Claude\claude_desktop_config.json`에 아래 내용을 추가하세요.

```json
{
  "mcpServers": {
    "obsidian-mcp-tools": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "여기에_API_키_입력",
        "OBSIDIAN_BASE_URL": "https://127.0.0.1:27124"
      }
    }
  }
}
```

> **주의**: `OBSIDIAN_API_KEY`는 Obsidian Local REST API 플러그인에서 발급받은 키를 입력하세요.  
> 기본 포트는 `27124`이며, 플러그인 설정에서 변경 가능합니다.

### 2.3 연결 확인

Claude Desktop 재시작 후:
```
Claude에서: "obsidian 서버 정보 보여줘"
```
볼트 이름과 경로가 응답으로 오면 연결 성공입니다.

---

## 3단계: Obsidian 볼트 확인

노트가 저장될 볼트가 Obsidian에서 열려 있어야 합니다.

- 기존 볼트를 사용하는 경우: Obsidian에서 해당 볼트가 열린 상태인지 확인
- 신규 볼트 생성: **Obsidian → Create new vault** 로 빈 볼트 생성 후 열기

> Study Companion 스킬은 첫 실행 시 `initialize_vault()`를 자동 호출하여  
> `_index.md`, `01_Books/`, `02_Sessions/` 등 기본 폴더 구조를 생성합니다.

---

## 4단계: Skill 파일 설치

```powershell
# study-companion 폴더를 skills 디렉토리로 복사
$dest = "$env:USERPROFILE\.claude\skills\study-companion"
Copy-Item -Path ".\study-companion" -Destination $dest -Recurse -Force

# 또는 .skill 파일이 있다면:
# .skill 파일을 더블클릭 → Claude Desktop이 자동 설치
```

---

## 5단계: Python 의존성 설치

```powershell
cd "$env:USERPROFILE\.claude\skills\study-companion"
pip install -r requirements.txt
```

---

## 6단계: Claude Desktop 재시작

Claude Desktop을 완전히 종료 후 재시작합니다.  
시스템 트레이에서 Claude 아이콘 우클릭 → Quit → 재실행.

---

## 7단계: 첫 실행 확인

Claude Desktop에서 다음과 같이 말씀하세요:

```
이 책으로 공부 시작
```

또는 PDF를 첨부하며:

```
이 자료로 학습 커리큘럼 만들어줘
```

Study Companion 스킬이 활성화되면 성공입니다! 🎉

---

## 문제 해결

### "NotebookLM이 연결되어 있지 않습니다"

→ Claude Desktop에서 notebooklm MCP 연결 상태 확인.  
→ `claude_desktop_config.json`에 notebooklm 서버 설정 추가 필요.

### "obsidian-mcp-tools MCP 연결 실패" 오류

→ Obsidian이 실행 중이고 Local REST API 플러그인이 활성화되어 있는지 확인.  
→ `claude_desktop_config.json`의 `OBSIDIAN_API_KEY` 값이 올바른지 확인.  
→ Obsidian Local REST API 포트(기본 27124)가 방화벽에 의해 차단되지 않았는지 확인.

### "_index.md 없음" 경고

→ Claude에서 "볼트 초기화해줘"라고 말하면 `initialize_vault()`가 실행됩니다.  
→ 학습 자체는 차단되지 않으므로 우선 학습 진행 후 초기화해도 됩니다.

### Skill이 트리거되지 않음

→ Claude Desktop 재시작.  
→ `%USERPROFILE%\.claude\skills\study-companion\SKILL.md` 파일 존재 확인.

### pytest 실행 (개발자용)

```powershell
cd "E:\Workspace\claude-works\study-companion"
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## macOS 설치

### 1단계: 사전 준비

#### 1.1 Python 3.11+ 설치 확인

```bash
python3 --version
# Python 3.11.x 이상이어야 함
```

없으면 [python.org](https://python.org) 또는 `brew install python@3.11` 으로 설치.

#### 1.2 Node.js 설치 확인 (obsidian-mcp-tools MCP용)

```bash
node --version
# v18 이상 권장
```

없으면 `brew install node` 또는 [nodejs.org](https://nodejs.org) 에서 설치.

#### 1.3 Claude Desktop 설치 확인

Claude Desktop (macOS 버전)이 설치·실행 중이어야 합니다.

#### 1.4 필수 MCP 연결 확인

Windows와 동일하게 `notebooklm`, `memory`, `obsidian-mcp-tools` 세 MCP가 필요합니다.

---

### 2단계: obsidian-mcp-tools MCP 설정 (macOS)

#### 2.1 Obsidian Local REST API 플러그인 설치

Windows와 동일 절차 (Obsidian → 커뮤니티 플러그인 → Local REST API 설치).

#### 2.2 Claude Desktop 설정에 obsidian-mcp-tools 추가

macOS 설정 파일 경로: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "obsidian-mcp-tools": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "여기에_API_키_입력",
        "OBSIDIAN_BASE_URL": "https://127.0.0.1:27124"
      }
    }
  }
}
```

터미널에서 편집:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

---

### 3단계: Obsidian 볼트 확인

Windows와 동일. 볼트가 Obsidian에서 열려 있어야 합니다.

---

### 4단계: Skill 파일 설치 (macOS)

```bash
# study-companion 폴더를 skills 디렉토리로 복사
DEST="$HOME/.claude/skills/study-companion"
cp -R ./study-companion "$DEST"

# 또는 .skill 파일이 있다면:
# .skill 파일을 더블클릭 → Claude Desktop이 자동 설치
```

---

### 5단계: Python 의존성 설치 (macOS)

```bash
cd "$HOME/.claude/skills/study-companion"
pip3 install -r requirements.txt
```

---

### 6단계: Claude Desktop 재시작

```bash
# 완전히 종료 후 재시작
osascript -e 'quit app "Claude"'
open -a Claude
```

---

### 7단계: 첫 실행 확인

Windows와 동일 — Claude Desktop에서 "이 책으로 공부 시작"을 입력하세요.

---

### macOS 문제 해결

#### "npx: command not found" 오류

```bash
# Node.js PATH 확인
which node
# /usr/local/bin/node 또는 /opt/homebrew/bin/node 가 나와야 함

# Claude Desktop 재시작 후 재시도
# 또는 claude_desktop_config.json의 command를 절대경로로:
"command": "/opt/homebrew/bin/npx"
```

#### "SSL certificate verification failed" 오류 (obsidian-mcp-tools)

Obsidian Local REST API가 자체 서명 인증서를 사용합니다.  
`OBSIDIAN_BASE_URL`을 `http://127.0.0.1:27124` (https → http)로 변경하거나  
플러그인 설정에서 SSL을 비활성화하세요.

#### Apple Silicon (M1/M2/M3) 관련

```bash
# Python arm64 버전 확인
python3 -c "import platform; print(platform.machine())"
# arm64 가 나오면 정상
```

---

## 설치 후 권장 Obsidian 플러그인

| 플러그인 | 설치 | 용도 |
|---------|------|------|
| Local REST API | Community Plugins | obsidian-mcp-tools MCP 연동 (필수) |
| Spaced Repetition | Community Plugins | 플래시카드 복습 |
| Dataview | Community Plugins | 학습 통계 |
| Calendar | Community Plugins | 세션 달력 뷰 |


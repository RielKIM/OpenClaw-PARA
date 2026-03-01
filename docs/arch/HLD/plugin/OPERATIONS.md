# OPERATIONS — Plugin (OpenClaw PARA Memory Plugin)

**버전**: 3.0 | **날짜**: 2026-03-01 | **상태**: Design Phase

> Hub 운영/배포: `docs/arch/HLD/hub/OPERATIONS.md`

---

## 1. 플러그인 배포

### 설치

```bash
git clone https://github.com/para-hub/para-memory-plugin.git
cd para-memory-plugin
npm install

# OpenClaw에 배포
cp -r . ~/.openclaw/workspace/skills/project-centric-context-engineering/

# 플러그인 활성화
echo '{"enabled": true}' > ~/.openclaw/config.json

# PARA 구조 초기화 (기존 memory/ 폴더 마이그레이션)
node tools/migrate-memory.js
```

### 업데이트

- 핫 리로드 지원 (재시작 불필요)
- `openclaw.plugin.json`을 통한 도구 등록 관리

### 로컬 저장소 경로

```
~/.openclaw/workspace/
├── memory/
│   ├── projects/
│   ├── areas/
│   ├── resources/
│   └── archive/
└── skills/
    └── project-centric-context-engineering/
```

---

## 2. PageIndex 서버 실행

### Python 직접 실행

```bash
cd pageindex-server/
pip install -r requirements.txt
cp .env.example .env    # OPENAI_API_KEY 설정
uvicorn server:app --host 127.0.0.1 --port 37779
```

### Docker Compose 실행

```bash
cd pageindex-server/
docker-compose up -d
```

> 자세한 서버 설계: `docs/arch/LLD/hub/pageindex-server.md`

# PageIndex Local Server — 상세 설계

**컴포넌트**: PageIndex 로컬 서버 (독립 서비스)
**관련 요구사항**: FR-2.2, FR-2.3
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

- VectifyAI `pageindex` 라이브러리를 HTTP API로 래핑
- Markdown 파일을 헤더 기반 계층 트리로 파싱·저장
- LLM 추론 기반 관련 노드 검색
- 로컬 Python 직접 실행 또는 Docker 컨테이너 실행 모두 지원

---

## 2. 위치

```
OpenClaw-PARA/
├── plugin/             # TypeScript 플러그인 (클라이언트)
├── hub/                # Phase 2 클라우드 Hub (별개)
├── pageindex-server/   # ← 이 컴포넌트
│   ├── server.py       # FastAPI 앱 진입점
│   ├── indexer.py      # pageindex md_to_tree 래퍼
│   ├── searcher.py     # LLM 추론 검색
│   ├── store.py        # 트리 JSON 저장/조회
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── openclaw/           # OpenClaw 소스 참조
```

> Phase 2 클라우드 Hub(`hub/`)와 **완전히 별개**. 항상 로컬에서만 실행.

---

## 3. 실행 방법

### 방법 A — Python 직접 실행

```bash
cd pageindex-server
pip install -r requirements.txt
python server.py
# 또는
uvicorn server:app --host 127.0.0.1 --port 37779 --reload
```

### 방법 B — Docker

```bash
cd pageindex-server
docker compose up -d

# 중단
docker compose down

# 로그 확인
docker compose logs -f
```

### 상태 확인

```bash
curl http://localhost:37779/health
# → {"status": "ok", "version": "0.1.0"}
```

---

## 4. HTTP API

### 공통

| 항목 | 값 |
|------|-----|
| Base URL | `http://127.0.0.1:37779` |
| 인증 | 없음 (localhost only) |
| Content-Type | `application/json` |

---

### `GET /health`

서버 상태 확인.

**응답 200:**
```json
{ "status": "ok", "version": "0.1.0" }
```

---

### `POST /index`

Markdown 파일을 파싱하여 트리로 인덱싱.

**요청:**
```json
{
  "file_path":  "/Users/uk/.openclaw/workspace/memory/projects/abc/index.md",
  "project_id": "abc",
  "category":   "projects"
}
```

**응답 200:**
```json
{
  "doc_id":     "sha256_hash_of_file_path",
  "node_count": 12,
  "indexed_at": "2026-03-01T12:00:00Z"
}
```

**동작:**
1. `file_path` 파일 읽기
2. `pageindex.md_to_tree()` 호출 → 트리 생성
3. `{data_dir}/{doc_id}.tree.json` 저장
4. 메타 인덱스 업데이트 (`index.json`)

---

### `POST /search`

LLM 추론으로 관련 노드 검색.

**요청:**
```json
{
  "query":      "오키나와 여행 예산",
  "project_id": "abc",       // null이면 전체 검색
  "category":   "projects",  // null이면 archive 제외 전체
  "limit":      5
}
```

**응답 200:**
```json
{
  "results": [
    {
      "project_id":      "abc",
      "project_title":   "오키나와 여행 2026",
      "file_path":       "/…/index.md",
      "node_id":         "1.2",
      "section":         "예산 계획",
      "content":         "항공권: 약 50만원\n숙박: ...",
      "relevance_score": 0.95,
      "reasoning":       "예산 계획 섹션이 질문과 직접 관련됨"
    }
  ],
  "query_ms": 1240
}
```

---

### `DELETE /index`

인덱스 삭제 (파일 삭제/아카이브 시).

**요청:**
```json
{ "file_path": "/…/index.md" }
```

**응답 200:**
```json
{ "deleted": true, "doc_id": "sha256_hash" }
```

---

### `POST /reindex`

항목 전체 재인덱싱 (디렉토리 내 모든 Markdown 파일).

**요청:**
```json
{ "item_path": "/Users/uk/.openclaw/workspace/memory/projects/abc/" }
```

**응답 200:**
```json
{ "indexed_files": 4, "skipped": 0 }
```

---

## 5. 내부 구조

### 5.1 indexer.py — 트리 파싱

```python
from pageindex import md_to_tree

def index_file(file_path: str, project_id: str, category: str) -> dict:
    tree = md_to_tree(
        md_path=file_path,
        if_add_node_summary="yes",   # 노드 요약 생성
        if_add_node_id="yes",
        if_add_node_text="yes",
    )
    tree["project_id"] = project_id
    tree["category"]   = category
    tree["indexed_at"] = datetime.utcnow().isoformat() + "Z"
    return tree
```

### 5.2 searcher.py — LLM 추론 검색

```python
SEARCH_PROMPT = """
당신은 문서 검색 전문가입니다.
아래 문서 트리와 사용자 질문이 주어집니다.
질문의 답이 있을 가능성이 높은 노드를 관련성 높은 순으로 반환하세요.

질문: {query}

문서 트리 (node_id, title, summary만 포함):
{tree_summary}

다음 JSON 형식으로만 응답하세요:
{{
  "thinking": "어느 섹션에 답이 있는지 간단한 추론",
  "node_list": [
    {{"node_id": "1.2", "reason": "예산 관련 직접 언급"}},
    ...
  ]
}}
"""

def search(query: str, trees: list[dict], limit: int) -> list[dict]:
    tree_summary = build_tree_summary(trees)   # node_id + title + summary만 추출
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",                   # 검색 추론용 (비용 절감)
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": SEARCH_PROMPT.format(
            query=query, tree_summary=tree_summary
        )}]
    )
    parsed = json.loads(response.choices[0].message.content)
    return extract_nodes(parsed["node_list"], trees, limit)
```

### 5.3 store.py — JSON 파일 저장

```
{data_dir}/                           # 기본: ~/.openclaw/workspace/.pageindex/
├── index.json                        # 전체 doc 메타 목록
│   [ { doc_id, file_path, project_id, category, indexed_at, node_count } ]
└── trees/
    ├── {sha256(file_path)}.tree.json  # 트리 전체 (content 포함)
    └── {sha256(file_path)}.meta.json  # 검색용 요약 (node_id + title + summary)
```

meta 파일을 별도 저장하여 검색 시 LLM 프롬프트 토큰 최소화.

---

## 6. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 데이터 디렉토리를 호스트와 공유
VOLUME ["/root/.openclaw/workspace/.pageindex"]

ENV OPENAI_API_KEY=""
ENV PAGEINDEX_DATA_DIR="/root/.openclaw/workspace/.pageindex"
ENV PAGEINDEX_PORT="37779"

EXPOSE 37779

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "37779"]
```

---

## 7. docker-compose.yml

```yaml
services:
  pageindex-server:
    build: .
    ports:
      - "127.0.0.1:37779:37779"    # localhost only (외부 노출 안 함)
    volumes:
      - ~/.openclaw/workspace/.pageindex:/root/.openclaw/workspace/.pageindex
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PAGEINDEX_DATA_DIR=/root/.openclaw/workspace/.pageindex
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:37779/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

---

## 8. requirements.txt

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pageindex>=0.1.0          # VectifyAI/PageIndex
openai>=1.101.0
pydantic>=2.10.0
python-dotenv>=1.1.0
```

---

## 9. 포트 배정

| 서비스 | 포트 |
|--------|------|
| claude-mem | 37777 |
| (예비) | 37778 |
| **PageIndex 서버** | **37779** |

---

## 10. 성능 목표

| 항목 | 목표 |
|------|------|
| `/health` 응답 | < 10ms |
| `/index` (파일당) | < 500ms (LLM 요약 포함 시 < 3s) |
| `/search` | < 2s (LLM API latency 포함) |

---

## 11. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| Python 직접 실행 → health check | 수동 |
| Docker 실행 → health check | 수동 |
| `/index` 요청 → tree.json 생성 확인 | 통합 |
| `/search` LLM 추론 결과 | 통합 |
| 볼륨 마운트 경로 공유 확인 | 수동 (Docker) |

# LLD 참조: docs/arch/LLD/hub/pageindex-server.md
# FastAPI 앱 진입점
#
# 실행 방법:
#   python server.py
#   uvicorn server:app --host 127.0.0.1 --port 37779 --reload

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import indexer
import searcher
from store import get_doc_id, delete_tree

VERSION = "0.1.0"
PORT = int(os.getenv("PAGEINDEX_PORT", "37779"))

app = FastAPI(title="PageIndex Local Server", version=VERSION)


# ── 요청/응답 스키마 ──────────────────────────────────────────

class IndexRequest(BaseModel):
    file_path:  str
    project_id: str
    category:   str

class DeleteIndexRequest(BaseModel):
    file_path: str

class ReindexRequest(BaseModel):
    item_path: str

class SearchRequest(BaseModel):
    query:      str
    project_id: str | None = None
    category:   str | None = None
    limit:      int = 5


# ── 엔드포인트 ────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.post("/index")
def index(req: IndexRequest):
    # TODO: indexer.index_file() 호출
    # TODO: 파일 없으면 HTTPException(404)
    raise NotImplementedError


@app.delete("/index")
def delete_index(req: DeleteIndexRequest):
    # TODO: store.delete_tree() 호출
    # TODO: doc_id 없으면 HTTPException(404)
    raise NotImplementedError


@app.post("/reindex")
def reindex(req: ReindexRequest):
    # TODO: indexer.reindex_item() 호출
    # TODO: 디렉토리 없으면 HTTPException(404)
    raise NotImplementedError


@app.post("/search")
def search(req: SearchRequest):
    # TODO: searcher.search() 호출
    # TODO: (results, query_ms) → { results, query_ms } 반환
    raise NotImplementedError


# ── 직접 실행 ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=PORT, reload=False)

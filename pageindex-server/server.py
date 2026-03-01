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
PORT    = int(os.getenv("PAGEINDEX_PORT", "37779"))

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
    try:
        result = indexer.index_file(req.file_path, req.project_id, req.category)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return result


@app.delete("/index")
def delete_index(req: DeleteIndexRequest):
    doc_id = get_doc_id(req.file_path)
    deleted = delete_tree(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"인덱스를 찾을 수 없습니다: {req.file_path}")
    return {"deleted": True, "doc_id": doc_id}


@app.post("/reindex")
def reindex(req: ReindexRequest):
    try:
        result = indexer.reindex_item(req.item_path)
    except NotADirectoryError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@app.post("/search")
def search(req: SearchRequest):
    results, query_ms = searcher.search(
        query=req.query,
        project_id=req.project_id,
        category=req.category,
        limit=req.limit,
    )
    return {"results": results, "query_ms": query_ms}


# ── 직접 실행 ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=PORT, reload=False)

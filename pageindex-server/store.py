# LLD 참조: docs/arch/LLD/hub/pageindex-server.md § 5.3
# 트리 JSON 저장/조회
#
# 저장 구조:
#   {data_dir}/
#   ├── index.json                         ← 전체 doc 메타 목록
#   └── trees/
#       ├── {doc_id}.tree.json             ← 트리 전체 (content 포함)
#       └── {doc_id}.meta.json             ← 검색용 요약 (node_id + title + summary)

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(os.getenv("PAGEINDEX_DATA_DIR", Path.home() / ".openclaw/workspace/.pageindex"))


def get_doc_id(file_path: str) -> str:
    return hashlib.sha256(file_path.encode()).hexdigest()[:16]


def _ensure_dirs() -> None:
    (DATA_DIR / "trees").mkdir(parents=True, exist_ok=True)


def save_tree(doc_id: str, tree: dict) -> None:
    # TODO: 트리 전체 저장 (.tree.json)
    # TODO: 검색용 요약 저장 (.meta.json) — node_id + title + summary만 추출
    # TODO: index.json 메타 업데이트
    raise NotImplementedError


def load_meta(doc_id: str) -> dict | None:
    # TODO: .meta.json 읽기, 없으면 None 반환
    raise NotImplementedError


def load_tree(doc_id: str) -> dict | None:
    # TODO: .tree.json 읽기, 없으면 None 반환
    raise NotImplementedError


def delete_tree(doc_id: str) -> bool:
    # TODO: .tree.json, .meta.json 삭제, index.json 업데이트
    raise NotImplementedError


def list_docs(project_id: str | None = None, category: str | None = None) -> list[dict]:
    # TODO: index.json 에서 조건에 맞는 doc 목록 반환
    raise NotImplementedError

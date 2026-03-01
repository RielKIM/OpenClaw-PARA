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

DATA_DIR = Path(os.getenv("PAGEINDEX_DATA_DIR", Path.home() / ".openclaw/workspace/.pageindex"))


def get_doc_id(file_path: str) -> str:
    return hashlib.sha256(file_path.encode()).hexdigest()[:16]


def _ensure_dirs() -> None:
    (DATA_DIR / "trees").mkdir(parents=True, exist_ok=True)


def _index_path() -> Path:
    return DATA_DIR / "index.json"


def _load_index() -> list[dict]:
    p = _index_path()
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _save_index(records: list[dict]) -> None:
    _ensure_dirs()
    with open(_index_path(), "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def _flatten_nodes(nodes: list[dict]) -> list[dict]:
    """트리 노드를 재귀적으로 평탄화하여 {node_id, title, summary} 목록 반환."""
    flat = []
    for node in nodes:
        flat.append({
            "node_id": node.get("node_id", ""),
            "title":   node.get("title", ""),
            "summary": (node.get("summary") or "")[:200],
        })
        children = node.get("nodes") or node.get("sub_nodes") or node.get("children") or []
        flat.extend(_flatten_nodes(children))
    return flat


def save_tree(doc_id: str, tree: dict) -> None:
    _ensure_dirs()

    # 트리 전체 저장
    tree_path = DATA_DIR / "trees" / f"{doc_id}.tree.json"
    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

    # 검색용 요약 저장 (LLM 프롬프트 토큰 최소화)
    root_nodes = tree.get("nodes") or tree.get("sub_nodes") or tree.get("children") or []
    meta = {
        "doc_id":        doc_id,
        "file_path":     tree.get("file_path", ""),
        "project_id":    tree.get("project_id", ""),
        "project_title": tree.get("title", ""),
        "category":      tree.get("category", ""),
        "indexed_at":    tree.get("indexed_at", ""),
        "nodes":         _flatten_nodes(root_nodes),
    }
    meta_path = DATA_DIR / "trees" / f"{doc_id}.meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # index.json 업데이트
    records = _load_index()
    records = [r for r in records if r["doc_id"] != doc_id]
    records.append({
        "doc_id":     doc_id,
        "file_path":  tree.get("file_path", ""),
        "project_id": tree.get("project_id", ""),
        "category":   tree.get("category", ""),
        "indexed_at": tree.get("indexed_at", ""),
        "node_count": tree.get("node_count", len(meta["nodes"])),
    })
    _save_index(records)


def load_meta(doc_id: str) -> dict | None:
    meta_path = DATA_DIR / "trees" / f"{doc_id}.meta.json"
    if not meta_path.exists():
        return None
    with open(meta_path, encoding="utf-8") as f:
        return json.load(f)


def load_tree(doc_id: str) -> dict | None:
    tree_path = DATA_DIR / "trees" / f"{doc_id}.tree.json"
    if not tree_path.exists():
        return None
    with open(tree_path, encoding="utf-8") as f:
        return json.load(f)


def delete_tree(doc_id: str) -> bool:
    tree_path = DATA_DIR / "trees" / f"{doc_id}.tree.json"
    meta_path = DATA_DIR / "trees" / f"{doc_id}.meta.json"

    if not tree_path.exists() and not meta_path.exists():
        return False

    tree_path.unlink(missing_ok=True)
    meta_path.unlink(missing_ok=True)

    records = _load_index()
    records = [r for r in records if r["doc_id"] != doc_id]
    _save_index(records)
    return True


def list_docs(project_id: str | None = None, category: str | None = None) -> list[dict]:
    records = _load_index()
    if project_id is not None:
        records = [r for r in records if r.get("project_id") == project_id]
    if category is not None:
        records = [r for r in records if r.get("category") == category]
    return records

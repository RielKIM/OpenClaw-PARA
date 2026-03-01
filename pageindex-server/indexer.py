# LLD 참조: docs/arch/LLD/hub/pageindex-server.md § 5.1
# pageindex md_to_tree 래퍼
#
# pageindex 라이브러리: https://github.com/VectifyAI/PageIndex
# pip install pageindex

import glob
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from pageindex import md_to_tree
except ImportError:
    md_to_tree = None  # type: ignore[assignment]

from store import get_doc_id, list_docs, save_tree


def _count_nodes(nodes: list) -> int:
    """트리 노드 수 재귀 계산."""
    count = 0
    for node in nodes:
        count += 1
        children = node.get("nodes") or node.get("sub_nodes") or node.get("children") or []
        count += _count_nodes(children)
    return count


def index_file(file_path: str, project_id: str, category: str) -> dict:
    if md_to_tree is None:
        raise RuntimeError("pageindex 라이브러리가 설치되지 않았습니다. pip install pageindex")

    if not Path(file_path).exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    tree = md_to_tree(
        md_path=file_path,
        if_add_node_summary="yes",
        if_add_node_id="yes",
        if_add_node_text="yes",
    )

    indexed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tree["project_id"] = project_id
    tree["category"]   = category
    tree["indexed_at"] = indexed_at
    tree["file_path"]  = file_path

    root_nodes = tree.get("nodes") or tree.get("sub_nodes") or tree.get("children") or []
    node_count = _count_nodes(root_nodes)
    tree["node_count"] = node_count

    doc_id = get_doc_id(file_path)
    save_tree(doc_id, tree)

    return {
        "doc_id":     doc_id,
        "node_count": node_count,
        "indexed_at": indexed_at,
    }


def reindex_item(item_path: str) -> dict:
    item_path = str(Path(item_path).resolve())

    if not Path(item_path).is_dir():
        raise NotADirectoryError(f"디렉토리를 찾을 수 없습니다: {item_path}")

    md_files = glob.glob(os.path.join(item_path, "**/*.md"), recursive=True)

    # 기존 인덱스에서 file_path → {project_id, category} 조회
    existing = {r["file_path"]: r for r in list_docs()}

    indexed = 0
    skipped = 0

    for md_file in md_files:
        md_file = str(Path(md_file).resolve())
        record = existing.get(md_file)

        if record:
            project_id = record["project_id"]
            category   = record["category"]
        else:
            # 경로 구조에서 추론: .../memory/{category}/{project_id}/...
            try:
                item_parts = Path(item_path).parts
                project_id = item_parts[-1]
                category   = item_parts[-2]
            except IndexError:
                skipped += 1
                continue

        try:
            index_file(md_file, project_id, category)
            indexed += 1
        except Exception:
            skipped += 1

    return {"indexed_files": indexed, "skipped": skipped}

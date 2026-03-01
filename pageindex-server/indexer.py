# LLD 참조: docs/arch/LLD/hub/pageindex-server.md § 5.1
# 마크다운 헤딩 기반 트리 파서
#
# pageindex 라이브러리(VectifyAI)는 PDF 클라우드 API로 로컬 .md 파싱 불가.
# 동일한 트리 구조를 직접 구현: 헤딩(#~######) → 계층 트리 + node_id 부여.

import glob
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from store import get_doc_id, list_docs, save_tree


# ── 마크다운 파서 ──────────────────────────────────────────────

def _parse_sections(content: str) -> list[dict]:
    """마크다운 텍스트를 헤딩 기반 섹션 목록으로 파싱."""
    lines = content.split("\n")
    sections: list[dict] = []
    current_title: str | None = None
    current_level = 0
    current_lines: list[str] = []

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.+)", line)
        if m:
            if current_title is not None:
                sections.append({
                    "level": current_level,
                    "title": current_title.strip(),
                    "text":  "\n".join(current_lines).strip(),
                })
            current_level = len(m.group(1))
            current_title = m.group(2)
            current_lines = []
        else:
            current_lines.append(line)

    if current_title is not None:
        sections.append({
            "level": current_level,
            "title": current_title.strip(),
            "text":  "\n".join(current_lines).strip(),
        })

    return sections


def _build_tree(sections: list[dict]) -> list[dict]:
    """섹션 목록을 계층 트리로 변환, node_id 부여 (예: "1", "1.1", "1.2.3")."""
    root: list[dict] = []
    stack: list[tuple[int, dict]] = []   # (level, node)
    level_counters: dict[int, int] = {}

    for section in sections:
        level = section["level"]

        # 현재 레벨보다 깊은 카운터 초기화
        for k in list(level_counters.keys()):
            if k > level:
                del level_counters[k]
        level_counters[level] = level_counters.get(level, 0) + 1

        node_id = ".".join(
            str(level_counters[l])
            for l in sorted(level_counters)
            if l <= level
        )

        text = section["text"]
        node: dict = {
            "node_id": node_id,
            "title":   section["title"],
            "text":    text,
            "summary": text[:200] if text else "",
            "nodes":   [],
        }

        while stack and stack[-1][0] >= level:
            stack.pop()

        if stack:
            stack[-1][1]["nodes"].append(node)
        else:
            root.append(node)

        stack.append((level, node))

    return root


def _parse_md_tree(file_path: str) -> dict:
    """마크다운 파일 → 헤딩 기반 계층 트리 dict 반환."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    sections = _parse_sections(content)

    # 최초 # 헤딩을 문서 제목으로 사용
    title = Path(file_path).stem
    for sec in sections:
        if sec["level"] == 1:
            title = sec["title"]
            break

    return {
        "title": title,
        "nodes": _build_tree(sections),
    }


# ── 공개 API ──────────────────────────────────────────────────

def _count_nodes(nodes: list) -> int:
    count = 0
    for node in nodes:
        count += 1
        count += _count_nodes(node.get("nodes", []))
    return count


def index_file(file_path: str, project_id: str, category: str) -> dict:
    if not Path(file_path).exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    tree = _parse_md_tree(file_path)

    indexed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tree["project_id"] = project_id
    tree["category"]   = category
    tree["indexed_at"] = indexed_at
    tree["file_path"]  = file_path

    node_count = _count_nodes(tree.get("nodes", []))
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
    existing = {r["file_path"]: r for r in list_docs()}

    indexed = 0
    skipped = 0

    for md_file in md_files:
        md_file = str(Path(md_file).resolve())
        record  = existing.get(md_file)

        if record:
            project_id = record["project_id"]
            category   = record["category"]
        else:
            try:
                parts      = Path(item_path).parts
                project_id = parts[-1]
                category   = parts[-2]
            except IndexError:
                skipped += 1
                continue

        try:
            index_file(md_file, project_id, category)
            indexed += 1
        except Exception:
            skipped += 1

    return {"indexed_files": indexed, "skipped": skipped}

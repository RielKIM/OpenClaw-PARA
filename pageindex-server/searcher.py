# LLD 참조: docs/arch/LLD/hub/pageindex-server.md § 5.2
# LLM 추론 기반 검색

import json
import os
import time

from openai import OpenAI

from store import list_docs, load_meta, load_tree

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SEARCH_PROMPT = """당신은 문서 검색 전문가입니다.
아래 문서 트리와 사용자 질문이 주어집니다.
질문의 답이 있을 가능성이 높은 노드를 관련성 높은 순으로 반환하세요.

질문: {query}

문서 트리 (node_id, title, summary만 포함):
{tree_summary}

다음 JSON 형식으로만 응답하세요:
{{
  "thinking": "어느 섹션에 답이 있는지 간단한 추론",
  "node_list": [
    {{"node_id": "1.2", "reason": "관련 내용 직접 언급"}},
    ...
  ]
}}

관련 섹션이 없으면 node_list를 빈 배열로 반환하세요."""


def _build_tree_summary(metas: list[dict]) -> str:
    """meta 목록에서 LLM 프롬프트용 요약 문자열 생성."""
    parts = []
    for meta in metas:
        parts.append(f"[문서: {meta.get('project_title', '')} | {meta.get('file_path', '')}]")
        for node in meta.get("nodes", []):
            summary = (node.get("summary") or "")[:100]
            parts.append(f"  [{node['node_id']}] {node['title']}: {summary}")
    return "\n".join(parts)


def _find_node(nodes: list[dict], node_id: str) -> dict | None:
    """node_id로 트리에서 노드를 재귀적으로 탐색."""
    for node in nodes:
        if node.get("node_id") == node_id:
            return node
        children = node.get("nodes") or node.get("sub_nodes") or node.get("children") or []
        found = _find_node(children, node_id)
        if found:
            return found
    return None


def _extract_nodes(node_list: list[dict], doc_map: dict, limit: int) -> list[dict]:
    """LLM이 반환한 node_list로 실제 트리에서 콘텐츠 추출."""
    results = []

    for rank, item in enumerate(node_list[:limit * 2]):  # 여유분 탐색
        if len(results) >= limit:
            break

        node_id = item.get("node_id", "")
        reason  = item.get("reason", "")
        relevance_score = max(0.1, 1.0 - rank * 0.15)

        for doc_id, (meta, tree) in doc_map.items():
            root_nodes = tree.get("nodes") or tree.get("sub_nodes") or tree.get("children") or []
            node = _find_node(root_nodes, node_id)
            if node:
                content = (
                    node.get("text")
                    or node.get("node_text")
                    or node.get("content")
                    or node.get("summary")
                    or ""
                )
                results.append({
                    "project_id":      meta.get("project_id", ""),
                    "project_title":   meta.get("project_title", ""),
                    "file_path":       meta.get("file_path", ""),
                    "node_id":         node_id,
                    "section":         node.get("title", ""),
                    "content":         content,
                    "relevance_score": relevance_score,
                    "reasoning":       reason,
                })
                break

    return results


def search(
    query:      str,
    project_id: str | None,
    category:   str | None,
    limit:      int,
) -> tuple[list[dict], int]:
    start_ms = int(time.time() * 1000)

    # 대상 doc 목록 조회
    docs = list_docs(project_id=project_id, category=category)

    # project_id / category 미지정 시 archive 제외
    if project_id is None and category is None:
        docs = [d for d in docs if d.get("category") != "archive"]

    if not docs:
        return [], int(time.time() * 1000) - start_ms

    # meta + tree 로드
    doc_map: dict[str, tuple[dict, dict]] = {}
    metas: list[dict] = []

    for record in docs:
        doc_id = record["doc_id"]
        meta = load_meta(doc_id)
        tree = load_tree(doc_id)
        if meta and tree:
            doc_map[doc_id] = (meta, tree)
            metas.append(meta)

    if not metas:
        return [], int(time.time() * 1000) - start_ms

    # LLM 호출
    tree_summary = _build_tree_summary(metas)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{
            "role":    "user",
            "content": SEARCH_PROMPT.format(query=query, tree_summary=tree_summary),
        }],
        timeout=30,
    )

    raw    = response.choices[0].message.content
    parsed = json.loads(raw)

    node_list = parsed.get("node_list", [])
    results   = _extract_nodes(node_list, doc_map, limit)

    query_ms = int(time.time() * 1000) - start_ms
    return results, query_ms

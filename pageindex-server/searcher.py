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
    # TODO: meta 목록에서 node_id + title + summary만 추출하여 JSON 문자열 반환
    # TODO: 토큰 초과 방지를 위해 summary는 100자로 자르기
    raise NotImplementedError


def _extract_nodes(node_list: list[dict], doc_map: dict, limit: int) -> list[dict]:
    # TODO: node_list의 node_id로 tree에서 실제 content 추출
    # TODO: relevance_score = 1.0 - (rank * 0.15) 로 계산
    # TODO: limit개까지만 반환
    raise NotImplementedError


def search(
    query: str,
    project_id: str | None,
    category: str | None,
    limit: int,
) -> tuple[list[dict], int]:
    # TODO: list_docs(project_id, category) 로 대상 doc 목록 조회
    # TODO: 각 doc의 .meta.json 로드
    # TODO: _build_tree_summary() 로 LLM 프롬프트용 요약 생성
    # TODO: OpenAI gpt-4o-mini 호출 (response_format=json_object)
    # TODO: 응답 파싱 → _extract_nodes()
    # TODO: (results, query_ms) 반환
    raise NotImplementedError

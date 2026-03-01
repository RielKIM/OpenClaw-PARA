# LLD 참조: docs/arch/LLD/hub/pageindex-server.md § 5.1
# pageindex md_to_tree 래퍼
#
# pageindex 라이브러리: https://github.com/VectifyAI/PageIndex
# pip install pageindex

from datetime import datetime, timezone

# TODO: pageindex 설치 후 import 활성화
# from pageindex import md_to_tree

from store import get_doc_id, save_tree


def index_file(file_path: str, project_id: str, category: str) -> dict:
    # TODO: pageindex.md_to_tree() 호출
    #   tree = md_to_tree(
    #       md_path=file_path,
    #       if_add_node_summary="yes",
    #       if_add_node_id="yes",
    #       if_add_node_text="yes",
    #   )
    # TODO: tree에 메타데이터 추가 (project_id, category, indexed_at)
    # TODO: store.save_tree() 호출
    # TODO: { doc_id, node_count, indexed_at } 반환
    raise NotImplementedError


def reindex_item(item_path: str) -> dict:
    # TODO: item_path 디렉토리 내 모든 .md 파일 순회
    # TODO: 각 파일에 대해 index_file() 호출
    # TODO: { indexed_files, skipped } 반환
    raise NotImplementedError

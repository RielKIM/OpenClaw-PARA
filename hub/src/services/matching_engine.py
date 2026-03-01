# LLD 참조: docs/arch/LLD/hub/matching-engine.md
class MatchingEngine:
    """6차원 유사도 기반 프로젝트 매칭"""

    async def find_similar(self, query_metadata: dict, user_reputation: int, top_k: int = 5):
        # TODO: pgvector KNN → 다차원 유사도 → 접근권한 필터링
        raise NotImplementedError

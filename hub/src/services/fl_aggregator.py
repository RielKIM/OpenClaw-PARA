# LLD 참조: docs/arch/LLD/hub/fl-aggregator.md
class FLAggregator:
    """연합 학습 그래디언트 집계 (MIN_PARTICIPANTS=10)"""
    MIN_PARTICIPANTS = 10

    async def receive_gradient(self, user_id: str, model_version: str,
                                encrypted_gradients: bytes, sample_size: int):
        raise NotImplementedError

    async def aggregate_round(self, model_version: str):
        # TODO: 참여자 < 10 → 스킵 / SMPC 집계 → 그래디언트 즉시 삭제
        raise NotImplementedError

    async def get_insights(self, category: str, subcategory: str):
        # TODO: n < MIN_PARTICIPANTS 시 거부
        raise NotImplementedError

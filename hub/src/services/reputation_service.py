# LLD 참조: docs/arch/LLD/hub/reputation-service.md
class ReputationService:
    """평판 점수 계산 및 이벤트 처리"""

    async def calculate_score(self, user_id: str):
        raise NotImplementedError

    async def process_event(self, event: dict):
        # 직접 DB 업데이트 금지 — 반드시 이 메서드를 통해서만
        raise NotImplementedError

    async def apply_inactivity_penalty(self):
        """배치 처리 — 매일 자정 실행"""
        raise NotImplementedError

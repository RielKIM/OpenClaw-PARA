# LLD 참조: docs/arch/LLD/hub/access-control.md
class AccessControlService:
    """평판 등급 기반 접근 제어 + 감사 로그"""

    async def check_access(self, user_id: str, content: dict, access_type: str):
        raise NotImplementedError

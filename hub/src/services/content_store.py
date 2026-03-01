# LLD 참조: docs/arch/LLD/hub/content-store.md
class ContentStore:
    """Agent 전용 암호화 콘텐츠 저장 (RSA-4096 + AES-256-GCM)"""

    async def save(self, knowledge_graph: dict) -> str:
        # TODO: 암호화 → S3 저장 → DB 메타데이터 기록
        raise NotImplementedError

    async def fetch(self, content_id: str) -> dict:
        # TODO: S3 조회 → Hub 개인키로 복호화 → 메모리 내 전달
        # 로컬 캐시 저장 금지
        raise NotImplementedError

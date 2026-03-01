# LLD 참조: docs/arch/LLD/hub/hub-api.md § 3
from fastapi import APIRouter, Depends
router = APIRouter()

@router.post("/search")
async def search_similar_projects():
    # TODO: MatchingEngine.find_similar()
    raise NotImplementedError

@router.post("/share")
async def share_project():
    # TODO: AnonymizerService → ContentStore.save()
    raise NotImplementedError

@router.get("/{content_id}/content")
async def get_agent_content(content_id: str):
    # TODO: AccessControlService.check_access() → ContentStore.fetch()
    # 메모리 내 전달, 로컬 저장 금지
    raise NotImplementedError

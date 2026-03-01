# LLD 참조: docs/arch/LLD/hub/hub-api.md § 4
from fastapi import APIRouter
router = APIRouter()

@router.get("/me/reputation")
async def get_my_reputation():
    # TODO: ReputationService.calculate_score()
    raise NotImplementedError

@router.post("/ratings")
async def submit_rating():
    # TODO: ReputationService.process_event('rating_4plus_received')
    raise NotImplementedError

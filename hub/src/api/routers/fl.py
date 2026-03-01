# LLD 참조: docs/arch/LLD/hub/hub-api.md § 5
from fastapi import APIRouter
router = APIRouter()

@router.post("/gradients")
async def submit_gradients():
    # TODO: FLAggregator.receive_gradient()
    raise NotImplementedError

@router.get("/model/latest")
async def get_latest_model():
    # TODO: ModelStore.get_latest()
    raise NotImplementedError

@router.get("/insights/{category}/{subcategory}")
async def get_insights(category: str, subcategory: str):
    # TODO: FLAggregator.get_insights() — n<10 시 거부
    raise NotImplementedError

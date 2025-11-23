from fastapi import APIRouter
from .endpoints import data, predict, dashboard, analytics, pile_history

router = APIRouter(prefix="/api/v1")

router.include_router(data.router, prefix="/data", tags=["Data"])
router.include_router(predict.router, prefix="/predict", tags=["Prediction"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(pile_history.router, prefix="/pile", tags=["Pile History"])
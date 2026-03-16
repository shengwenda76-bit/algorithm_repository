"""API v1 总路由。"""

from fastapi import APIRouter

from app.api.v1.algorithms import router as algorithms_router
from app.api.v1.executions import router as executions_router

router = APIRouter(prefix="/api/v1")
router.include_router(algorithms_router)
router.include_router(executions_router)

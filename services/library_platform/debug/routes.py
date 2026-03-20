"""本文件用于放置算法调试执行接口的占位定义。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from services.library_platform.debug.service import DebugExecutionError, DebugExecutionService
from services.library_platform.registry.service import AlgorithmNotFoundError
from services.library_platform.schemas import DebugExecuteRequestSchema, DebugExecuteResponseSchema


DEBUG_EXECUTE_ROUTE = "/algorithms/{code}/execute"

DEBUG_ROUTES = [
    {
        "method": "POST",
        "path": DEBUG_EXECUTE_ROUTE,
        "module": "debug",
        "summary": "执行算法调试请求。",
    },
]


def build_debug_router(debug_service: DebugExecutionService) -> APIRouter:
    """构建调试执行路由。"""

    router = APIRouter()

    @router.post(DEBUG_EXECUTE_ROUTE, response_model=DebugExecuteResponseSchema)
    def execute_algorithm(code: str, payload: DebugExecuteRequestSchema) -> DebugExecuteResponseSchema:
        """执行指定算法的调试请求。"""

        try:
            result = debug_service.execute(code=code, payload=payload.model_dump())
            return DebugExecuteResponseSchema.model_validate(result)
        except AlgorithmNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except DebugExecutionError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return router

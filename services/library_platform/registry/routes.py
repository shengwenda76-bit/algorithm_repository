"""本文件用于放置算法注册和校验接口的占位定义。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from services.library_platform.registry.service import (
    DuplicateAlgorithmVersionError,
    InvalidRegistrationPayloadError,
    RegistryService,
)
from services.library_platform.schemas import (
    RegistrationRequestSchema,
    RegistrationResponseSchema,
    ValidationResultSchema,
)

REGISTER_ROUTE = "/algorithms/register"
VALIDATE_ROUTE = "/algorithms/validate"

REGISTRY_ROUTES = [
    {
        "method": "POST",
        "path": REGISTER_ROUTE,
        "module": "registry",
        "summary": "注册新的算法或算法版本。",
    },
    {
        "method": "POST",
        "path": VALIDATE_ROUTE,
        "module": "registry",
        "summary": "校验算法元数据和算法包信息。",
    },
]


def build_registry_router(registry_service: RegistryService) -> APIRouter:
    """构建注册中心路由。"""

    router = APIRouter()

    @router.post(
        REGISTER_ROUTE,
        status_code=status.HTTP_201_CREATED,
        response_model=RegistrationResponseSchema,
    )
    def register_algorithm(payload: RegistrationRequestSchema) -> RegistrationResponseSchema:
        """注册新的算法或算法版本。"""

        try:
            result = registry_service.register(payload.model_dump())
            return RegistrationResponseSchema.model_validate(result)
        except DuplicateAlgorithmVersionError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        except InvalidRegistrationPayloadError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post(VALIDATE_ROUTE, response_model=ValidationResultSchema)
    def validate_algorithm(payload: RegistrationRequestSchema) -> ValidationResultSchema:
        """校验算法元数据和算法包信息。"""

        result = registry_service.validate_payload(payload.model_dump())
        return ValidationResultSchema.model_validate(result)

    return router

"""本文件用于放置算法目录查询接口的占位定义。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from services.library_platform.registry.service import (
    AlgorithmNotFoundError,
    RegistryService,
)
from services.library_platform.schemas import (
    AlgorithmDetailResponseSchema,
    AlgorithmListResponseSchema,
    AlgorithmVersionDetailResponseSchema,
    AlgorithmVersionListResponseSchema,
)

LIST_ROUTE = "/algorithms"
DETAIL_ROUTE = "/algorithms/{code}"
VERSIONS_ROUTE = "/algorithms/{code}/versions"
VERSION_DETAIL_ROUTE = "/algorithms/{code}/versions/{version}"

CATALOG_ROUTES = [
    {
        "method": "GET",
        "path": LIST_ROUTE,
        "module": "catalog",
        "summary": "查询算法列表。",
    },
    {
        "method": "GET",
        "path": DETAIL_ROUTE,
        "module": "catalog",
        "summary": "查询指定算法详情。",
    },
    {
        "method": "GET",
        "path": VERSIONS_ROUTE,
        "module": "catalog",
        "summary": "查询指定算法的版本列表。",
    },
    {
        "method": "GET",
        "path": VERSION_DETAIL_ROUTE,
        "module": "catalog",
        "summary": "查询指定算法版本的完整元数据。",
    },
]


def build_catalog_router(registry_service: RegistryService) -> APIRouter:
    """构建目录查询路由。"""

    router = APIRouter()

    @router.get(LIST_ROUTE, response_model=AlgorithmListResponseSchema)
    def list_algorithms() -> AlgorithmListResponseSchema:
        """返回已注册算法列表。"""

        return AlgorithmListResponseSchema.model_validate(registry_service.list_algorithms())

    @router.get(DETAIL_ROUTE, response_model=AlgorithmDetailResponseSchema)
    def get_algorithm(code: str) -> AlgorithmDetailResponseSchema:
        """返回指定算法详情。"""

        try:
            return AlgorithmDetailResponseSchema.model_validate(registry_service.get_algorithm(code))
        except AlgorithmNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @router.get(VERSIONS_ROUTE, response_model=AlgorithmVersionListResponseSchema)
    def list_versions(code: str) -> AlgorithmVersionListResponseSchema:
        """返回指定算法的版本列表。"""

        try:
            return AlgorithmVersionListResponseSchema.model_validate(registry_service.list_versions(code))
        except AlgorithmNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @router.get(VERSION_DETAIL_ROUTE, response_model=AlgorithmVersionDetailResponseSchema)
    def get_version(code: str, version: str) -> AlgorithmVersionDetailResponseSchema:
        """返回指定算法版本详情。"""

        try:
            return AlgorithmVersionDetailResponseSchema.model_validate(
                registry_service.get_version(code, version)
            )
        except AlgorithmNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return router

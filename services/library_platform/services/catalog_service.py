from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from services.library_platform.repositories.algorithm_repository import AlgorithmRepository

class CatalogService:
    def __init__(self, repository: AlgorithmRepository):
        self._repository = repository

    def list_algorithms(self, category: Optional[str] = None, status: str = "active", page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        skip = (page - 1) * page_size
        items, total = self._repository.list_algorithms(category, status, skip, page_size)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_algorithm_detail(self, code: str) -> Dict[str, Any]:
        detail = self._repository.get_version_detail(code)
        if not detail:
            raise HTTPException(status_code=404, detail={
                "error": "ALGORITHM_NOT_FOUND",
                "message": f"Algorithm {code} not found.",
                "detail": {}
            })
        return detail

    def list_versions(self, code: str) -> Dict[str, Any]:
        versions = self._repository.list_versions(code)
        if not versions:
            raise HTTPException(status_code=404, detail={
                "error": "ALGORITHM_NOT_FOUND",
                "message": f"Algorithm {code} not found.",
                "detail": {}
            })
        return {
            "code": code,
            "items": versions
        }

    def get_version_detail(self, code: str, version: str) -> Dict[str, Any]:
        detail = self._repository.get_version_detail(code, version)
        if not detail:
            raise HTTPException(status_code=404, detail={
                "error": "VERSION_NOT_FOUND",
                "message": f"Algorithm version {code}:{version} not found.",
                "detail": {}
            })
        return detail

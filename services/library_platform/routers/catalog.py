from typing import Optional
from fastapi import APIRouter, Depends, Query, status
import logging

from services.library_platform.schemas.catalog import AlgorithmListResponse, AlgorithmDetailResponse, VersionListResponse, VersionDetailResponse
from services.library_platform.services.catalog_service import CatalogService
from services.library_platform.dependencies import get_catalog_service

router = APIRouter(prefix="/algorithms", tags=["catalog"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=AlgorithmListResponse, status_code=status.HTTP_200_OK)
def list_algorithms(
    category: Optional[str] = Query(None, description="Filter by category"),
    algorithm_status: str = Query("active", alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: CatalogService = Depends(get_catalog_service)
):
    logger.info(f"Listing algorithms: page={page}, page_size={page_size}")
    return service.list_algorithms(category=category, status=algorithm_status, page=page, page_size=page_size)

@router.get("/{code}", response_model=AlgorithmDetailResponse, status_code=status.HTTP_200_OK)
def get_algorithm_detail(
    code: str,
    service: CatalogService = Depends(get_catalog_service)
):
    logger.info(f"Getting algorithm detail for code: {code}")
    return service.get_algorithm_detail(code)

@router.get("/{code}/versions", response_model=VersionListResponse, status_code=status.HTTP_200_OK)
def list_versions(
    code: str,
    service: CatalogService = Depends(get_catalog_service)
):
    logger.info(f"Listing versions for code: {code}")
    return service.list_versions(code)

@router.get("/{code}/versions/{version}", response_model=VersionDetailResponse, status_code=status.HTTP_200_OK)
def get_version_detail(
    code: str,
    version: str,
    service: CatalogService = Depends(get_catalog_service)
):
    logger.info(f"Getting version detail for {code}:{version}")
    return service.get_version_detail(code, version)

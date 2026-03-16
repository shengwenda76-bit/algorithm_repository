"""算法目录相关接口。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_algorithm_catalog_service
from app.schemas.algorithm import AlgorithmCatalogEntry
from app.services.algorithm_catalog_service import AlgorithmCatalogService

router = APIRouter(prefix="/algorithms", tags=["algorithms"])


@router.get("", response_model=list[AlgorithmCatalogEntry])
def list_algorithms(
    service: AlgorithmCatalogService = Depends(get_algorithm_catalog_service),
) -> list[AlgorithmCatalogEntry]:
    """返回当前内存目录中可用的算法列表。"""

    return service.list_algorithms()

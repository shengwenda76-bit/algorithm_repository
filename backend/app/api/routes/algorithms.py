from fastapi import APIRouter, HTTPException

from app.schemas.algorithm import AlgorithmVersionResponse
from app.services.algorithm_registry import AlgorithmRegistry

router = APIRouter()
registry = AlgorithmRegistry()


@router.get("/v1/algorithms")
def list_algorithms() -> dict:
    return registry.list_algorithms()


@router.get(
    "/v1/algorithms/{algo_code}/versions/{version}",
    response_model=AlgorithmVersionResponse,
)
def get_algorithm_version_schema(algo_code: str, version: str) -> AlgorithmVersionResponse:
    item = registry.get_version(algo_code, version)
    if item is None:
        raise HTTPException(status_code=404, detail="algorithm version not found")
    return AlgorithmVersionResponse(
        algo_code=item.algo_code,
        version=item.version,
        input_schema=item.input_schema,
        output_schema=item.output_schema,
        default_timeout_sec=item.default_timeout_sec,
    )

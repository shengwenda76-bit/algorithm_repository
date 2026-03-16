"""执行相关接口。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_execution_service
from app.schemas.execution import ExecutionRequest, ExecutionResult
from app.services.execution_service import ExecutionService

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post("/run", response_model=ExecutionResult)
def run_execution(
    request: ExecutionRequest,
    service: ExecutionService = Depends(get_execution_service),
) -> ExecutionResult:
    """同步执行一个最小流程定义。"""

    return service.submit_execution(request.flow)

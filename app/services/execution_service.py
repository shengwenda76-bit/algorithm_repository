"""执行入口服务。"""

from __future__ import annotations

from uuid import uuid4

from app.engine.orchestrator import orchestrator
from app.schemas.execution import ExecutionResult
from app.schemas.flow_dsl import FlowDSL


class ExecutionService:
    """负责创建执行号并委托编排器执行。"""

    def submit_execution(self, flow: FlowDSL) -> ExecutionResult:
        """提交流程并以同步方式执行。"""

        # 骨架阶段直接生成执行号并同步调用编排器。
        execution_id = str(uuid4())
        return orchestrator.start_execution(execution_id=execution_id, flow=flow)


execution_service = ExecutionService()

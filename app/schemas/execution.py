"""执行请求与执行结果相关的数据模型。"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.flow_dsl import FlowDSL


class NodeExecutionResult(BaseModel):
    """单个节点的执行结果。"""

    node_id: str
    algo_code: str
    algo_version: str
    status: Literal["SUCCEEDED", "FAILED", "SKIPPED"]
    outputs: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    source: Literal["registry", "cache", "downloaded"] | None = None


class ExecutionRequest(BaseModel):
    """提交执行时使用的请求体。"""

    flow: FlowDSL


class ExecutionResult(BaseModel):
    """一次执行的聚合结果。"""

    execution_id: str
    status: Literal["SUCCEEDED", "FAILED"]
    node_results: list[NodeExecutionResult] = Field(default_factory=list)

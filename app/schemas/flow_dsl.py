"""骨架运行时使用的最小 Flow DSL 模型。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FlowNode(BaseModel):
    """流程中一个可执行的算法节点。"""

    node_id: str = Field(..., description="Unique node identifier")
    algo_code: str = Field(..., description="Algorithm code")
    algo_version: str = Field(..., description="Algorithm version")
    params: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class FlowDSL(BaseModel):
    """用于编排执行的最小流程定义。"""

    nodes: list[FlowNode] = Field(default_factory=list)

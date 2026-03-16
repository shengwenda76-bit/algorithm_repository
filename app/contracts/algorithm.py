"""平台与插件算法共享的基础契约。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    """编排器使用的执行模式。"""

    IN_MEMORY = "in_memory"
    REMOTE = "remote"


class AlgorithmMeta(BaseModel):
    """平台运行算法所需的最小元数据。"""

    algo_code: str = Field(..., description="Unique algorithm code")
    name: str = Field(..., description="Display name")
    category: str = Field(..., description="Algorithm category")
    version: str = Field(..., description="Algorithm version")
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.IN_MEMORY,
        description="Execution mode used by the platform runtime",
    )
    description: str = Field(default="", description="Human-readable description")


class BaseAlgorithm(ABC):
    """所有平台可执行算法的基础契约。"""

    meta: ClassVar[AlgorithmMeta]

    @abstractmethod
    def execute(self, inputs: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """执行算法，并返回平台约定格式的输出结果。"""

    @classmethod
    def get_meta(cls) -> AlgorithmMeta:
        """返回算法类上声明的元数据。"""

        return cls.meta

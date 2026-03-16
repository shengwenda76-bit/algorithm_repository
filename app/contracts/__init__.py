"""平台与算法包共享的契约定义包。"""

from app.contracts.algorithm import AlgorithmMeta, BaseAlgorithm, ExecutionMode

__all__ = [
    "AlgorithmMeta",
    "BaseAlgorithm",
    "ExecutionMode",
]

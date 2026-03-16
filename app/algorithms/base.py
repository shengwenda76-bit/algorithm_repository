"""兼容层：对外继续暴露算法基础契约。"""

from app.contracts.algorithm import AlgorithmMeta, BaseAlgorithm, ExecutionMode

__all__ = [
    "AlgorithmMeta",
    "BaseAlgorithm",
    "ExecutionMode",
]

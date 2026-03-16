"""运行时算法注册表。"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Type

from app.algorithms.base import BaseAlgorithm


class AlgorithmRegistry:
    """执行运行时使用的内存注册表。"""

    _algorithms: dict[tuple[str, str], Type[BaseAlgorithm]] = {}

    @classmethod
    def register(cls, algorithm_cls: Type[BaseAlgorithm]) -> None:
        """按 `(algo_code, version)` 注册算法类。"""

        meta = algorithm_cls.get_meta()
        key = (meta.algo_code, meta.version)
        cls._algorithms[key] = algorithm_cls

    @classmethod
    def bulk_register(cls, algorithms: Iterable[Type[BaseAlgorithm]]) -> None:
        """批量注册多个算法类。"""

        for algorithm_cls in algorithms:
            cls.register(algorithm_cls)

    @classmethod
    def get(cls, algo_code: str, version: str) -> Type[BaseAlgorithm]:
        """获取已注册的算法类。"""

        key = (algo_code, version)
        if key not in cls._algorithms:
            raise KeyError(f"Algorithm not found: {algo_code}@{version}")
        return cls._algorithms[key]

    @classmethod
    def contains(cls, algo_code: str, version: str) -> bool:
        """检查指定算法版本是否已经注册。"""

        return (algo_code, version) in cls._algorithms

    @classmethod
    def list_all(cls) -> list[Type[BaseAlgorithm]]:
        """列出当前全部已注册算法类。"""

        return list(cls._algorithms.values())

    @classmethod
    def clear(cls) -> None:
        """清空内存中的注册表内容。"""

        cls._algorithms.clear()

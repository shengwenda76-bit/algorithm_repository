"""标准化算法入口。"""

from __future__ import annotations

from typing import Any

from app.contracts.algorithm import BaseAlgorithm

from .meta import ALGORITHM_META
from .validators import validate_inputs, validate_params


class StandardizeAlgorithm(BaseAlgorithm):
    meta = ALGORITHM_META

    def execute(self, inputs: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """对数值序列执行最小最大归一化。"""

        validate_inputs(inputs)
        validate_params(params)

        dataset = list(inputs["dataset"])
        if not dataset:
            return {"dataset": []}

        low = min(dataset)
        high = max(dataset)
        if high == low:
            return {"dataset": [0 for _ in dataset]}

        normalized = [(item - low) / (high - low) for item in dataset]
        return {"dataset": normalized}

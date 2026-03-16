"""异常值处理算法入口。"""

from __future__ import annotations

from math import sqrt
from typing import Any

from app.contracts.algorithm import BaseAlgorithm

from .meta import ALGORITHM_META
from .validators import validate_inputs, validate_params


class OutliersAlgorithm(BaseAlgorithm):
    meta = ALGORITHM_META

    def execute(self, inputs: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """按 z-score 阈值过滤异常值。"""

        validate_inputs(inputs)
        validate_params(params)

        dataset = list(inputs["dataset"])
        threshold = float(params.get("z_threshold", 3.0))
        if len(dataset) < 2:
            return {"dataset": dataset, "removed_count": 0}

        mean = sum(dataset) / len(dataset)
        variance = sum((item - mean) ** 2 for item in dataset) / len(dataset)
        if variance == 0:
            return {"dataset": dataset, "removed_count": 0}

        std = sqrt(variance)
        filtered = [
            item for item in dataset if abs((item - mean) / std) <= threshold
        ]
        return {"dataset": filtered, "removed_count": len(dataset) - len(filtered)}

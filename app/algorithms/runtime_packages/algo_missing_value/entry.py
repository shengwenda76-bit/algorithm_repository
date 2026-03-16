"""缺失值处理算法入口。"""

from __future__ import annotations

from typing import Any

from app.contracts.algorithm import BaseAlgorithm

from .meta import ALGORITHM_META
from .validators import validate_inputs, validate_params


class MissingValueAlgorithm(BaseAlgorithm):
    meta = ALGORITHM_META

    def execute(self, inputs: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """将输入数据中的空值替换为默认值。"""

        validate_inputs(inputs)
        validate_params(params)

        dataset = list(inputs["dataset"])
        fill_value = params.get("fill_value", 0)
        filled_count = 0
        output = []
        for item in dataset:
            if item is None:
                output.append(fill_value)
                filled_count += 1
            else:
                output.append(item)
        return {"dataset": output, "filled_count": filled_count}

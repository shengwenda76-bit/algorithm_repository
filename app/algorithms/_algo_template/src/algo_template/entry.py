"""模板算法入口。"""

from __future__ import annotations

from typing import Any

from app.contracts.algorithm import BaseAlgorithm

from .meta import ALGORITHM_META
from .validators import validate_inputs, validate_params


class TemplateAlgorithm(BaseAlgorithm):
    meta = ALGORITHM_META

    def execute(self, inputs: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """执行模板算法，并返回原始输入与参数。"""

        validate_inputs(inputs)
        validate_params(params)
        return {"status": "ok", "inputs": inputs, "params": params}

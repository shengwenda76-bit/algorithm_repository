"""模板算法校验函数。"""

from __future__ import annotations

from typing import Any


def validate_inputs(inputs: dict[str, Any]) -> None:
    if "dataset" not in inputs:
        raise ValueError("inputs must include 'dataset'")


def validate_params(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("params must be a dict")

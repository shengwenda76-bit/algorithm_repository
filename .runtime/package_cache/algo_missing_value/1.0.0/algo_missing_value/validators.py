"""缺失值处理算法校验。"""

from __future__ import annotations

from typing import Any


def validate_inputs(inputs: dict[str, Any]) -> None:
    dataset = inputs.get("dataset")
    if dataset is None:
        raise ValueError("inputs must include 'dataset'")
    if not isinstance(dataset, list):
        raise ValueError("'dataset' must be a list")


def validate_params(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("params must be a dict")

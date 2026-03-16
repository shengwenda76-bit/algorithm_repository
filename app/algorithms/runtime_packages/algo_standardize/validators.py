"""标准化算法校验。"""

from __future__ import annotations

from typing import Any


def validate_inputs(inputs: dict[str, Any]) -> None:
    dataset = inputs.get("dataset")
    if dataset is None:
        raise ValueError("inputs must include 'dataset'")
    if not isinstance(dataset, list):
        raise ValueError("'dataset' must be a list")
    if not all(isinstance(item, (int, float)) for item in dataset):
        raise ValueError("'dataset' must contain only numbers")


def validate_params(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("params must be a dict")

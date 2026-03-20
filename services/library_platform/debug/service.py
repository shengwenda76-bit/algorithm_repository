"""本文件用于提供算法调试执行的最小运行时实现。"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

from services.library_platform.registry.service import RegistryService


class DebugExecutionError(Exception):
    """调试执行失败时抛出的异常。"""


class DebugExecutionService:
    """算法调试执行服务。"""

    def __init__(self, registry_service: RegistryService) -> None:
        self._registry_service = registry_service
        self._project_root = Path(__file__).resolve().parents[3]

    def execute(self, code: str, payload: dict[str, Any]) -> dict[str, Any]:
        """执行指定算法的调试请求。"""

        version = payload.get("version")
        record = self._registry_service.get_record(code=code, version=version)
        self._ensure_import_paths(code)
        algorithm_class = self._load_algorithm_class(record.definition.entrypoint)
        algorithm = algorithm_class()
        result = algorithm.execute(
            inputs=payload.get("inputs", {}),
            params=payload.get("params", {}),
        )
        return {
            "code": record.definition.code,
            "version": record.definition.version,
            "result": result,
        }

    def _ensure_import_paths(self, code: str) -> None:
        """补充算法包和 SDK 的导入路径。"""

        sdk_root = self._project_root / "sdk"
        algorithm_root = self._project_root / "algorithms" / f"algo_{code}"
        for path in (sdk_root, algorithm_root):
            path_str = str(path)
            if path.exists() and path_str not in sys.path:
                sys.path.insert(0, path_str)

    @staticmethod
    def _load_algorithm_class(entrypoint: str) -> type:
        """根据 entrypoint 动态加载算法类。"""

        try:
            module_name, class_name = entrypoint.split(":", maxsplit=1)
        except ValueError as exc:
            raise DebugExecutionError("Algorithm entrypoint format is invalid.") from exc

        try:
            module = importlib.import_module(module_name)
            algorithm_class = getattr(module, class_name)
        except (ImportError, AttributeError) as exc:
            raise DebugExecutionError("Algorithm entrypoint could not be loaded.") from exc

        return algorithm_class

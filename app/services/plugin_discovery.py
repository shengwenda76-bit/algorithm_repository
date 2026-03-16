"""插件发现与入口类加载服务。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from app.contracts.algorithm import BaseAlgorithm
from app.core.exceptions import AlgorithmLoadError
from app.schemas.algorithm import ResolvedArtifact


class PluginDiscovery:
    """从缓存目录中加载插件入口类。"""

    def load_algorithm_class(
        self,
        artifact: ResolvedArtifact,
        package_dir: Path | None = None,
    ) -> type[BaseAlgorithm]:
        """加载入口模块并返回算法类对象。"""

        package_dir = package_dir or Path(artifact.source_dir)
        package_alias = f"{artifact.import_package}_v_{artifact.version.replace('.', '_')}"
        package_init = package_dir / "__init__.py"
        entry_path = package_dir / f"{artifact.entry_module}.py"

        self._load_package_module(package_alias, package_init, package_dir)
        entry_module = self._load_entry_module(package_alias, artifact.entry_module, entry_path)

        algorithm_cls = getattr(entry_module, artifact.class_name, None)
        if algorithm_cls is None:
            raise AlgorithmLoadError(
                f"Entry class not found: {artifact.class_name} in {entry_path}"
            )
        if not issubclass(algorithm_cls, BaseAlgorithm):
            raise AlgorithmLoadError(
                f"Entry class must inherit BaseAlgorithm: {artifact.class_name}"
            )
        return algorithm_cls

    def _load_package_module(self, package_alias: str, package_init: Path, package_dir: Path) -> None:
        """先加载包对象，保证后续相对导入能够正常工作。"""

        if package_alias in sys.modules:
            sys.modules.pop(package_alias, None)

        spec = importlib.util.spec_from_file_location(
            package_alias,
            package_init,
            submodule_search_locations=[str(package_dir)],
        )
        if spec is None or spec.loader is None:
            raise AlgorithmLoadError(f"Cannot build package spec for {package_init}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[package_alias] = module
        spec.loader.exec_module(module)

    def _load_entry_module(self, package_alias: str, entry_module: str, entry_path: Path):
        """加载入口模块并返回模块对象。"""

        module_name = f"{package_alias}.{entry_module}"
        if module_name in sys.modules:
            sys.modules.pop(module_name, None)

        spec = importlib.util.spec_from_file_location(module_name, entry_path)
        if spec is None or spec.loader is None:
            raise AlgorithmLoadError(f"Cannot build entry spec for {entry_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


plugin_discovery = PluginDiscovery()

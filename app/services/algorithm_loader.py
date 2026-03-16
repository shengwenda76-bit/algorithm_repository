"""从注册表或模拟私有 PyPI 制品中加载运行时算法。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Type

from app.algorithms.registry import AlgorithmRegistry
from app.contracts.algorithm import BaseAlgorithm
from app.services.algorithm_fetcher import algorithm_fetcher
from app.services.plugin_discovery import plugin_discovery
from app.services.algorithm_resolver import algorithm_resolver


@dataclass(slots=True)
class LoadedAlgorithm:
    """算法加载结果。"""

    algorithm_cls: Type[BaseAlgorithm]
    source: str
    module_path: Path | None = None


class AlgorithmLoader:
    """确保目标算法在执行前已经可用。"""

    def ensure_loaded(self, algo_code: str, version: str) -> LoadedAlgorithm:
        """从注册表、缓存或模拟下载源中加载算法。"""

        if AlgorithmRegistry.contains(algo_code, version):
            # 已注册算法直接返回，避免重复解析和导入。
            return LoadedAlgorithm(
                algorithm_cls=AlgorithmRegistry.get(algo_code, version),
                source="registry",
            )

        # 本地未注册时，先解析制品信息，再拉取到本地缓存。
        artifact = algorithm_resolver.resolve(algo_code, version)
        package_dir, source = algorithm_fetcher.fetch(artifact)
        # 平台主动发现入口类并显式注册，不再依赖算法包导入副作用。
        algorithm_cls = plugin_discovery.load_algorithm_class(artifact, package_dir)
        AlgorithmRegistry.register(algorithm_cls)

        return LoadedAlgorithm(
            algorithm_cls=AlgorithmRegistry.get(algo_code, version),
            source=source,
            module_path=package_dir / f"{artifact.entry_module}.py",
        )


algorithm_loader = AlgorithmLoader()

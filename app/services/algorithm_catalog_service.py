"""运行时骨架使用的内存算法目录服务。"""

from __future__ import annotations

from pathlib import Path

from app.config import settings
from app.core.exceptions import AlgorithmNotFoundError
from app.schemas.algorithm import AlgorithmCatalogEntry, ResolvedArtifact


class AlgorithmCatalogService:
    """提供算法目录元数据，以及模拟制品内容。"""

    def __init__(self) -> None:
        self._runtime_packages_root = Path("app/algorithms/runtime_packages")
        self._catalog = self._build_catalog()

    def list_algorithms(self) -> list[AlgorithmCatalogEntry]:
        """返回当前平台暴露的可用算法列表。"""

        return sorted(self._catalog.values(), key=lambda item: (item.category, item.algo_code))

    def get_catalog_entry(self, algo_code: str, version: str) -> AlgorithmCatalogEntry:
        """返回指定算法版本对应的目录项。"""

        key = self._key(algo_code, version)
        if key not in self._catalog:
            raise AlgorithmNotFoundError(algo_code, version)
        return self._catalog[key]

    def get_resolved_artifact(self, algo_code: str, version: str) -> ResolvedArtifact:
        """将目录项解析为可下载的模拟制品信息。"""

        entry = self.get_catalog_entry(algo_code, version)
        # 当前阶段仍返回模拟地址，但源目录已切换为标准插件包目录。
        artifact_filename = f"{entry.package_name}-{entry.version}.whl"
        artifact_url = (
            f"{settings.private_pypi_url}/{entry.package_name}/{entry.version}/{artifact_filename}"
        )
        return ResolvedArtifact(
            algo_code=entry.algo_code,
            version=entry.version,
            package_name=entry.package_name,
            import_package=entry.import_package,
            entry_module=entry.entry_module,
            class_name=entry.class_name,
            artifact_filename=artifact_filename,
            artifact_url=artifact_url,
            source_dir=str(self._runtime_packages_root / entry.import_package),
        )

    @staticmethod
    def _key(algo_code: str, version: str) -> str:
        return f"{algo_code}@{version}"

    def _build_catalog(self) -> dict[str, AlgorithmCatalogEntry]:
        """构建内存版算法目录，后续可替换为数据库或配置中心。"""

        entries = [
            AlgorithmCatalogEntry(
                algo_code="missing_value",
                name="缺失值处理",
                category="data_cleaning",
                version="1.0.0",
                package_name="algo-missing-value",
                import_package="algo_missing_value",
                entry_module="entry",
                class_name="MissingValueAlgorithm",
                description="将空值替换为指定默认值。",
            ),
            AlgorithmCatalogEntry(
                algo_code="outliers",
                name="异常值处理",
                category="data_cleaning",
                version="1.0.0",
                package_name="algo-outliers",
                import_package="algo_outliers",
                entry_module="entry",
                class_name="OutliersAlgorithm",
                description="按 z-score 阈值移除异常值。",
            ),
            AlgorithmCatalogEntry(
                algo_code="standardize",
                name="数据标准化",
                category="data_processing",
                version="1.0.0",
                package_name="algo-standardize",
                import_package="algo_standardize",
                entry_module="entry",
                class_name="StandardizeAlgorithm",
                description="对数值序列执行最小最大归一化。",
            ),
        ]
        return {self._key(item.algo_code, item.version): item for item in entries}


algorithm_catalog_service = AlgorithmCatalogService()

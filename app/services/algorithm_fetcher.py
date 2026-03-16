"""模拟从私有 PyPI 下载算法制品。"""

from __future__ import annotations

from pathlib import Path
from shutil import copytree, ignore_patterns, rmtree

from app.core.exceptions import ArtifactFetchError
from app.core.package_cache import package_cache
from app.schemas.algorithm import ResolvedArtifact


class AlgorithmFetcher:
    """将算法制品拉取到本地缓存目录。"""

    def fetch(self, artifact: ResolvedArtifact) -> tuple[Path, str]:
        """获取安装后的本地包目录，并返回当前制品来源。"""

        package_dir = package_cache.get_installed_package_dir(
            artifact.package_name,
            artifact.version,
            artifact.import_package,
        )
        source_dir = Path(artifact.source_dir)
        if not source_dir.exists():
            raise ArtifactFetchError(f"Source package directory not found: {source_dir}")

        if (package_dir / "__init__.py").exists():
            return package_dir, "cache"

        # 当前阶段用复制标准插件目录来模拟“下载并安装到本地缓存”。
        package_dir.parent.mkdir(parents=True, exist_ok=True)
        if package_dir.exists():
            rmtree(package_dir)
        copytree(source_dir, package_dir, ignore=ignore_patterns("__pycache__", "*.pyc"))

        if not (package_dir / "__init__.py").exists():
            raise ArtifactFetchError(
                f"Fetched package is invalid: {artifact.package_name}@{artifact.version}"
            )

        return package_dir, "downloaded"


algorithm_fetcher = AlgorithmFetcher()

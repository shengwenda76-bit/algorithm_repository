"""算法制品本地缓存辅助模块。"""

from __future__ import annotations

from pathlib import Path

from app.config import settings


class PackageCache:
    """管理下载后算法制品的本地缓存目录。"""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = Path(root_dir or settings.package_cache_dir)

    def ensure_root(self) -> Path:
        """确保缓存根目录存在。"""

        self.root_dir.mkdir(parents=True, exist_ok=True)
        return self.root_dir

    def get_package_dir(self, package_name: str, version: str) -> Path:
        """返回指定算法包版本对应的缓存目录。"""

        safe_name = package_name.replace("-", "_")
        return self.ensure_root() / safe_name / version

    def get_installed_package_dir(
        self,
        package_name: str,
        version: str,
        import_package: str,
    ) -> Path:
        """返回缓存目录中安装后的包目录。"""

        return self.get_package_dir(package_name, version) / import_package

    def get_module_path(self, package_name: str, version: str, entry_module: str) -> Path:
        """返回入口模块在本地缓存中的完整路径。"""

        return self.get_package_dir(package_name, version) / f"{entry_module}.py"

    def is_cached(self, package_name: str, version: str, entry_module: str) -> bool:
        """判断指定版本的入口模块是否已缓存。"""

        return self.get_module_path(package_name, version, entry_module).exists()


package_cache = PackageCache()

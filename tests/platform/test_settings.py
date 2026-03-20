"""本文件用于验证算法库平台配置解析逻辑。"""

from __future__ import annotations

import unittest
from pathlib import Path

from services.library_platform.settings import (
    LIBRARY_PLATFORM,
    LibraryPlatformSettings,
    build_default_sqlite_database_url,
)


class LibraryPlatformSettingsTests(unittest.TestCase):
    """平台配置测试。"""

    def test_build_default_sqlite_database_url_uses_runtime_directory(self) -> None:
        """本地默认 sqlite 地址应落在仓库内的 runtime 目录。"""

        project_root = Path("D:/demo/project")

        database_url = build_default_sqlite_database_url(project_root)

        self.assertEqual(
            database_url,
            "sqlite:///D:/demo/project/.runtime/library_platform/algorithm_library.db",
        )

    def test_from_sources_defaults_to_repository_config(self) -> None:
        """无显式覆盖时应默认使用 settings.py 中声明的仓储配置。"""

        settings = LibraryPlatformSettings.from_sources()

        self.assertEqual(settings.repository_backend, "sqlite")
        self.assertEqual(
            settings.database_url,
            build_default_sqlite_database_url(),
        )

    def test_from_sources_can_override_to_memory_backend_for_tests(self) -> None:
        """测试或特殊启动时应允许显式覆盖成内存后端。"""

        settings = LibraryPlatformSettings.from_sources(
            repository_backend="memory",
        )

        self.assertEqual(settings.repository_backend, "memory")
        self.assertEqual(settings.database_url, "")

    def test_from_sources_detects_backend_from_explicit_database_url(self) -> None:
        """显式传入数据库地址时应推导出对应的仓储后端。"""

        settings = LibraryPlatformSettings.from_sources(database_url="sqlite:///:memory:")

        self.assertEqual(settings.repository_backend, "sqlite")
        self.assertEqual(settings.database_url, "sqlite:///:memory:")

    def test_repository_config_is_declared_in_settings_module(self) -> None:
        """settings.py 中应直接声明主配置块。"""

        self.assertEqual(LIBRARY_PLATFORM["REPOSITORY_BACKEND"], "sqlite")
        self.assertEqual(LIBRARY_PLATFORM["DATABASE"]["ENGINE"], "sqlite")
        self.assertEqual(
            LIBRARY_PLATFORM["DATABASE"]["NAME"],
            ".runtime/library_platform/algorithm_library.db",
        )


if __name__ == "__main__":
    unittest.main()

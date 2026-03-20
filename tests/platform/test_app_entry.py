"""本文件用于验证算法库平台应用入口的最小可运行能力。"""

import unittest
from pathlib import Path

from services.library_platform.app import (
    create_app,
    create_fastapi_app,
    create_registry_repository,
    create_runtime_settings,
)
from services.library_platform.settings import LibraryPlatformSettings
from services.library_platform.registry.repository import (
    InMemoryRegistryRepository,
    SqliteRegistryRepository,
)


class AppEntryTests(unittest.TestCase):
    """算法库平台应用入口测试。"""

    def test_create_app_collects_expected_modules_and_routes(self) -> None:
        """应用入口应汇总当前一期定义的模块和路由。"""

        app = create_app()

        self.assertEqual(app.name, "python-algorithm-library-platform")
        self.assertEqual(app.modules, ["registry", "catalog", "debug"])
        self.assertEqual(len(app.routes), 7)
        self.assertEqual(app.routes[0]["path"], "/algorithms/register")

    def test_describe_returns_serializable_summary(self) -> None:
        """应用描述结果应包含模块、路由和统计信息。"""

        app = create_app()
        summary = app.describe()

        self.assertEqual(summary["name"], "python-algorithm-library-platform")
        self.assertEqual(summary["route_count"], 7)
        self.assertIn("modules", summary)
        self.assertIn("routes", summary)

    def test_create_registry_repository_defaults_to_settings_config(self) -> None:
        """未显式覆盖时应默认使用 settings.py 中配置的 sqlite 仓储。"""

        repository = create_registry_repository()

        self.assertIsInstance(repository, SqliteRegistryRepository)

    def test_create_registry_repository_uses_sqlite_for_sqlite_url(self) -> None:
        """传入 sqlite URL 时应使用 sqlite 仓储。"""

        repository = create_registry_repository("sqlite:///:memory:")

        self.assertIsInstance(repository, SqliteRegistryRepository)

    def test_create_fastapi_app_accepts_sqlite_database_url(self) -> None:
        """应用入口应支持通过数据库 URL 创建 sqlite 仓储。"""

        app = create_fastapi_app(database_url="sqlite:///:memory:")

        self.assertIsInstance(app.state.registry_service._repository, SqliteRegistryRepository)

    def test_create_fastapi_app_allows_memory_override_for_tests(self) -> None:
        """测试场景应允许通过显式 settings 覆盖成内存仓储。"""

        app = create_fastapi_app(
            settings=LibraryPlatformSettings(repository_backend="memory", database_url="")
        )

        self.assertIsInstance(app.state.registry_service._repository, InMemoryRegistryRepository)

    def test_create_runtime_settings_prefers_file_sqlite_for_local_startup(self) -> None:
        """本地启动配置应默认优先使用文件型 sqlite。"""

        settings = create_runtime_settings(project_root=Path("D:/demo/project"))

        self.assertEqual(settings.repository_backend, "sqlite")
        self.assertEqual(
            settings.database_url,
            "sqlite:///D:/demo/project/.runtime/library_platform/algorithm_library.db",
        )


if __name__ == "__main__":
    unittest.main()

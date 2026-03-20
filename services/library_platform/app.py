"""本文件用于提供算法库平台应用入口的最小可运行定义。"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI

try:
    from services.library_platform.catalog.routes import CATALOG_ROUTES
    from services.library_platform.catalog.routes import build_catalog_router
    from services.library_platform.debug.routes import DEBUG_ROUTES
    from services.library_platform.debug.routes import build_debug_router
    from services.library_platform.debug.service import DebugExecutionService
    from services.library_platform.registry.routes import REGISTRY_ROUTES
    from services.library_platform.registry.routes import build_registry_router
    from services.library_platform.registry.repository import (
        InMemoryRegistryRepository,
        RegistryRepository,
        SqliteRegistryRepository,
    )
    from services.library_platform.settings import LibraryPlatformSettings
    from services.library_platform.registry.service import RegistryService
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from services.library_platform.catalog.routes import CATALOG_ROUTES
    from services.library_platform.catalog.routes import build_catalog_router
    from services.library_platform.debug.routes import DEBUG_ROUTES
    from services.library_platform.debug.routes import build_debug_router
    from services.library_platform.debug.service import DebugExecutionService
    from services.library_platform.registry.routes import REGISTRY_ROUTES
    from services.library_platform.registry.routes import build_registry_router
    from services.library_platform.registry.repository import (
        InMemoryRegistryRepository,
        RegistryRepository,
        SqliteRegistryRepository,
    )
    from services.library_platform.settings import LibraryPlatformSettings
    from services.library_platform.registry.service import RegistryService

APP_NAME = "python-algorithm-library-platform"
APP_VERSION = "0.1.0"
APP_MODULES = ["registry", "catalog", "debug"]


@dataclass(slots=True)
class LibraryPlatformApp:
    """算法库平台应用入口对象。"""

    name: str
    version: str
    modules: list[str]
    routes: list[dict[str, str]]
    repository_backend: str = "memory"
    database_url: str = ""

    def describe(self) -> dict[str, object]:
        """返回应用摘要信息。"""

        return {
            "name": self.name,
            "version": self.version,
            "modules": list(self.modules),
            "repository_backend": self.repository_backend,
            "database_url": self.database_url,
            "route_count": len(self.routes),
            "routes": list(self.routes),
        }

    def to_json(self) -> str:
        """返回可直接输出的 JSON 描述。"""

        return json.dumps(self.describe(), ensure_ascii=False, indent=2)


def collect_routes() -> list[dict[str, str]]:
    """汇总一期平台定义的全部路由。"""

    return [*REGISTRY_ROUTES, *CATALOG_ROUTES, *DEBUG_ROUTES]


def create_app(settings: LibraryPlatformSettings | None = None) -> LibraryPlatformApp:
    """创建算法库平台应用对象。"""

    resolved_settings = settings or LibraryPlatformSettings.from_sources()
    return LibraryPlatformApp(
        name=APP_NAME,
        version=APP_VERSION,
        modules=list(APP_MODULES),
        routes=collect_routes(),
        repository_backend=resolved_settings.repository_backend,
        database_url=resolved_settings.database_url,
    )


def create_runtime_settings(
    database_url: str | None = None,
    *,
    project_root: Path | None = None,
) -> LibraryPlatformSettings:
    """创建本地运行时默认配置。"""

    return LibraryPlatformSettings.from_sources(
        database_url=database_url,
        project_root=project_root,
    )


def create_registry_repository(
    database_url: str | None = None,
    *,
    settings: LibraryPlatformSettings | None = None,
) -> RegistryRepository:
    """根据数据库 URL 选择当前使用的仓储实现。"""

    resolved_settings = settings or LibraryPlatformSettings.from_sources(database_url=database_url)
    if resolved_settings.repository_backend == "memory":
        return InMemoryRegistryRepository()

    if resolved_settings.repository_backend == "sqlite":
        return SqliteRegistryRepository(resolved_settings.database_url)

    raise ValueError(f"Unsupported repository backend: {resolved_settings.repository_backend}")


def create_fastapi_app(
    database_url: str | None = None,
    *,
    settings: LibraryPlatformSettings | None = None,
) -> FastAPI:
    """创建最小可运行的 FastAPI 应用。"""

    resolved_settings = settings or LibraryPlatformSettings.from_sources(database_url=database_url)
    app = FastAPI(title=APP_NAME, version=APP_VERSION)
    app.state.settings = resolved_settings
    app.state.registry_repository = create_registry_repository(settings=resolved_settings)
    app.state.registry_service = RegistryService(app.state.registry_repository)
    app.state.debug_service = DebugExecutionService(app.state.registry_service)
    app.include_router(build_registry_router(app.state.registry_service))
    app.include_router(build_catalog_router(app.state.registry_service))
    app.include_router(build_debug_router(app.state.debug_service))

    @app.get("/")
    def read_root() -> dict[str, object]:
        """返回平台摘要信息。"""

        return create_app(settings=app.state.settings).describe()

    return app


def main() -> None:
    """输出应用摘要，便于快速查看脚手架状态。"""

    settings = create_runtime_settings()
    create_fastapi_app(settings=settings)
    summary = create_app(settings=settings)
    print(summary.to_json())


if __name__ == "__main__":
    main()

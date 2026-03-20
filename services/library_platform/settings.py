"""本文件用于提供算法库平台的仓库级显式配置。"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_SQLITE_NAME = ".runtime/library_platform/algorithm_library.db"

LIBRARY_PLATFORM: dict[str, Any] = {
    "REPOSITORY_BACKEND": "sqlite",
    "DATABASE": {
        "ENGINE": "sqlite",
        "NAME": DEFAULT_SQLITE_NAME,
    },
}


def build_default_sqlite_database_url(project_root: Path | None = None) -> str:
    """根据默认 sqlite 文件名构造数据库地址。"""

    resolved_project_root = (project_root or Path(__file__).resolve().parents[2]).resolve()
    database_path = resolved_project_root / DEFAULT_SQLITE_NAME
    return f"sqlite:///{database_path.as_posix()}"


def detect_repository_backend(database_url: str) -> str:
    """根据数据库 URL 推导仓储后端。"""

    if database_url.startswith("sqlite:///"):
        return "sqlite"
    raise ValueError(f"Unsupported database url: {database_url}")


def build_database_url_from_config(
    config: dict[str, Any] | None = None,
    *,
    project_root: Path | None = None,
) -> str:
    """从配置块构造数据库 URL。"""

    resolved_config = deepcopy(config or LIBRARY_PLATFORM)
    database_config = resolved_config.get("DATABASE", {})
    engine = str(database_config.get("ENGINE", "")).lower()

    if engine == "sqlite":
        database_name = str(database_config.get("NAME", "")).strip()
        if not database_name:
            raise ValueError("DATABASE.NAME must be configured for sqlite engine.")
        if database_name == ":memory:":
            return "sqlite:///:memory:"

        resolved_project_root = (project_root or Path(__file__).resolve().parents[2]).resolve()
        database_path = Path(database_name)
        if not database_path.is_absolute():
            database_path = resolved_project_root / database_name
        return f"sqlite:///{database_path.as_posix()}"

    raise ValueError(f"Unsupported database engine: {engine}")


@dataclass(slots=True)
class LibraryPlatformSettings:
    """算法库平台运行配置。"""

    database_url: str = ""
    repository_backend: str = "memory"

    @classmethod
    def from_sources(
        cls,
        database_url: str | None = None,
        repository_backend: str | None = None,
        *,
        project_root: Path | None = None,
        config: dict[str, Any] | None = None,
    ) -> "LibraryPlatformSettings":
        """从 settings.py 配置块和显式覆盖参数中解析运行配置。"""

        resolved_config = deepcopy(config or LIBRARY_PLATFORM)
        resolved_repository_backend = str(
            repository_backend or resolved_config.get("REPOSITORY_BACKEND", "memory")
        ).lower()

        if resolved_repository_backend == "memory":
            return cls(database_url="", repository_backend="memory")

        resolved_database_url = database_url
        if resolved_database_url is None:
            resolved_database_url = build_database_url_from_config(
                resolved_config,
                project_root=project_root,
            )

        return cls(
            database_url=resolved_database_url,
            repository_backend=detect_repository_backend(resolved_database_url),
        )

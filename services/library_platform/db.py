"""本文件用于放置算法库平台数据库元数据的最小无依赖实现。"""

from __future__ import annotations

import sqlite3
from copy import deepcopy
from pathlib import Path
from typing import Any


DATABASE_URL_ENV = "ALGORITHM_LIBRARY_DATABASE_URL"

metadata: dict[str, dict[str, Any]] = {
    # algorithms:
    # 一条记录代表一个“算法身份”，比如 missing_value。
    # 作用：支撑算法列表页、算法详情页、按 code 查算法。
    "algorithms": {
        "name": "algorithms",
        "primary_key": ["code"],
        "columns": [
            {"name": "code", "type": "string", "nullable": False},
            {"name": "name", "type": "string", "nullable": False},
            {"name": "category", "type": "string", "nullable": True},
            {"name": "description", "type": "text", "nullable": True},
            {"name": "status", "type": "string", "nullable": False},
            {"name": "created_at", "type": "datetime", "nullable": False},
            {"name": "updated_at", "type": "datetime", "nullable": False},
        ],
    },
    # algorithm_versions:
    # 一条记录代表某个算法的一个版本，比如 missing_value:0.1.0。
    # 作用：支撑版本列表、版本详情、调试执行时按 code + version 找到真正该跑哪个类。
    "algorithm_versions": {
        "name": "algorithm_versions",
        "primary_key": ["code", "version"],
        "columns": [
            {"name": "code", "type": "string", "nullable": False},
            {"name": "version", "type": "string", "nullable": False},
            {"name": "entrypoint", "type": "string", "nullable": False},
            {"name": "inputs_json", "type": "json", "nullable": True},
            {"name": "outputs_json", "type": "json", "nullable": True},
            {"name": "params_json", "type": "json", "nullable": True},
            {"name": "resources_json", "type": "json", "nullable": True},
            {"name": "requirements_json", "type": "json", "nullable": True},
            {"name": "tags_json", "type": "json", "nullable": True},
            {"name": "status", "type": "string", "nullable": False},
            {"name": "is_latest", "type": "boolean", "nullable": False},
            {"name": "created_at", "type": "datetime", "nullable": False},
            {"name": "updated_at", "type": "datetime", "nullable": False},
        ],
    },
    # algorithm_artifacts:
    # 一条记录代表某个版本对应的发布制品。
    # 作用：支撑后续安装、下载、校验、发布追踪。现在注册接口里已经有这部分语义了。
    "algorithm_artifacts": {
        "name": "algorithm_artifacts",
        "primary_key": ["code", "version"],
        "columns": [
            {"name": "code", "type": "string", "nullable": False},
            {"name": "version", "type": "string", "nullable": False},
            {"name": "package_name", "type": "string", "nullable": False},
            {"name": "package_version", "type": "string", "nullable": False},
            {"name": "repository_url", "type": "string", "nullable": False},
            {"name": "artifact_type", "type": "string", "nullable": True},
            {"name": "filename", "type": "string", "nullable": True},
            {"name": "sha256", "type": "string", "nullable": True},
            {"name": "created_at", "type": "datetime", "nullable": False},
            {"name": "updated_at", "type": "datetime", "nullable": False},
        ],
    },
}


def get_database_url() -> str:
    """返回数据库环境变量名称占位。"""

    return DATABASE_URL_ENV


def get_table(name: str) -> dict[str, Any]:
    """返回指定表的元数据定义。"""

    if name not in metadata:
        raise KeyError(f"Unknown table: {name}")
    return deepcopy(metadata[name])


def normalize_sqlite_path(database_url: str) -> str:
    """将 sqlite URL 转换为 sqlite3 可识别的数据库路径。"""

    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError(f"Unsupported sqlite database url: {database_url}")

    raw_path = database_url[len(prefix) :]
    if raw_path == ":memory:":
        return raw_path
    return str(Path(raw_path))


def connect_sqlite(database_url: str) -> sqlite3.Connection:
    """创建 sqlite 连接。"""

    database_path = normalize_sqlite_path(database_url)
    if database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def bootstrap_sqlite_schema(connection: sqlite3.Connection) -> None:
    """初始化 sqlite 所需的三张表。"""

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS algorithms (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS algorithm_versions (
            code TEXT NOT NULL,
            version TEXT NOT NULL,
            entrypoint TEXT NOT NULL,
            inputs_json TEXT,
            outputs_json TEXT,
            params_json TEXT,
            resources_json TEXT,
            requirements_json TEXT,
            tags_json TEXT,
            status TEXT NOT NULL,
            is_latest INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (code, version)
        );

        CREATE TABLE IF NOT EXISTS algorithm_artifacts (
            code TEXT NOT NULL,
            version TEXT NOT NULL,
            package_name TEXT NOT NULL,
            package_version TEXT NOT NULL,
            repository_url TEXT NOT NULL,
            artifact_type TEXT,
            filename TEXT,
            sha256 TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (code, version)
        );
        """
    )
    connection.commit()

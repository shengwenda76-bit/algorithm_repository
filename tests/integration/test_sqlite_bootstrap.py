"""本文件用于验证 sqlite 数据库初始化辅助能力。"""

from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from services.library_platform.db import bootstrap_sqlite_schema, connect_sqlite


class SqliteBootstrapTests(unittest.TestCase):
    """sqlite 初始化测试。"""

    def test_connect_sqlite_creates_parent_directory_for_file_database(self) -> None:
        """文件型 sqlite 连接应自动创建父目录。"""

        temp_root = Path(".runtime_sqlite_bootstrap_test")
        temp_root.mkdir(exist_ok=True)
        self.addCleanup(shutil.rmtree, temp_root, True)

        database_path = temp_root / "nested" / "registry.db"
        connection = connect_sqlite(f"sqlite:///{database_path.as_posix()}")
        self.addCleanup(connection.close)

        self.assertTrue(database_path.parent.exists())

    def test_bootstrap_sqlite_schema_creates_expected_tables(self) -> None:
        """sqlite 初始化应创建算法相关三张表。"""

        connection = connect_sqlite("sqlite:///:memory:")
        self.addCleanup(connection.close)

        bootstrap_sqlite_schema(connection)
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()

        self.assertEqual(
            [row["name"] for row in rows],
            ["algorithm_artifacts", "algorithm_versions", "algorithms"],
        )


if __name__ == "__main__":
    unittest.main()

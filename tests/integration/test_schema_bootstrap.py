"""本文件用于放置数据库和平台结构初始化相关测试。"""

from __future__ import annotations

import unittest

from services.library_platform.db import DATABASE_URL_ENV, get_database_url, get_table, metadata


class SchemaBootstrapTests(unittest.TestCase):
    """数据库元数据初始化测试。"""

    def test_database_url_env_name_is_stable(self) -> None:
        """数据库环境变量名称应保持稳定。"""

        self.assertEqual(get_database_url(), DATABASE_URL_ENV)
        self.assertEqual(DATABASE_URL_ENV, "ALGORITHM_LIBRARY_DATABASE_URL")

    def test_metadata_contains_algorithm_tables(self) -> None:
        """元数据中应包含算法主表、版本表和算法包信息表。"""

        self.assertIn("algorithms", metadata)
        self.assertIn("algorithm_versions", metadata)
        self.assertIn("algorithm_artifacts", metadata)

    def test_algorithms_table_contains_identity_columns(self) -> None:
        """算法主表应包含算法身份和展示所需字段。"""

        algorithms_table = get_table("algorithms")
        column_names = [column["name"] for column in algorithms_table["columns"]]

        self.assertEqual(algorithms_table["primary_key"], ["code"])
        self.assertIn("name", column_names)
        self.assertIn("category", column_names)
        self.assertIn("description", column_names)
        self.assertIn("status", column_names)
        self.assertIn("created_at", column_names)
        self.assertIn("updated_at", column_names)

    def test_algorithm_versions_table_contains_runtime_metadata_columns(self) -> None:
        """算法版本表应包含执行和契约相关字段。"""

        versions_table = get_table("algorithm_versions")
        column_names = [column["name"] for column in versions_table["columns"]]

        self.assertEqual(versions_table["primary_key"], ["code", "version"])
        self.assertIn("entrypoint", column_names)
        self.assertIn("inputs_json", column_names)
        self.assertIn("outputs_json", column_names)
        self.assertIn("params_json", column_names)
        self.assertIn("resources_json", column_names)
        self.assertIn("requirements_json", column_names)
        self.assertIn("tags_json", column_names)
        self.assertIn("status", column_names)
        self.assertIn("is_latest", column_names)
        self.assertIn("created_at", column_names)
        self.assertIn("updated_at", column_names)

    def test_artifact_table_contains_distribution_columns(self) -> None:
        """算法包信息表应包含制品定位相关字段。"""

        artifact_table = get_table("algorithm_artifacts")
        column_names = [column["name"] for column in artifact_table["columns"]]

        self.assertEqual(artifact_table["primary_key"], ["code", "version"])
        self.assertIn("artifact_type", column_names)
        self.assertIn("filename", column_names)
        self.assertIn("sha256", column_names)
        self.assertIn("created_at", column_names)
        self.assertIn("updated_at", column_names)


if __name__ == "__main__":
    unittest.main()

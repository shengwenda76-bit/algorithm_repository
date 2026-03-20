"""本文件用于验证 sqlite 仓储接入后的平台接口行为。"""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from services.library_platform.app import create_fastapi_app


def build_valid_payload() -> dict:
    """构造一个可用于注册的合法请求体。"""

    return {
        "definition": {
            "code": "missing_value",
            "name": "缺失值处理",
            "version": "0.1.0",
            "entrypoint": "algo_missing_value.entry:MissingValueAlgorithm",
            "category": "data_cleaning",
            "description": "用于处理缺失值的示例算法。",
        },
        "artifact": {
            "package_name": "algo-missing-value",
            "package_version": "0.1.0",
            "repository_url": "https://pypi.example.local/simple",
        },
    }


class SqliteBackendApiTests(unittest.TestCase):
    """sqlite 仓储下的平台 API 测试。"""

    def test_register_and_catalog_queries_work_with_sqlite_repository(self) -> None:
        """切换到 sqlite 仓储后，注册和目录查询接口仍应可用。"""

        client = TestClient(create_fastapi_app(database_url="sqlite:///:memory:"))

        register_response = client.post("/algorithms/register", json=build_valid_payload())
        list_response = client.get("/algorithms")
        detail_response = client.get("/algorithms/missing_value")

        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(list_response.json()["items"][0]["code"], "missing_value")
        self.assertEqual(detail_response.json()["version"], "0.1.0")


if __name__ == "__main__":
    unittest.main()

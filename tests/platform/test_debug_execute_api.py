"""本文件用于放置算法调试执行接口相关测试。"""

import unittest

from fastapi.testclient import TestClient

from services.library_platform.app import create_fastapi_app
from services.library_platform.settings import LibraryPlatformSettings


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


def build_second_version_payload() -> dict:
    """构造第二个版本的注册请求体。"""

    return {
        "definition": {
            "code": "missing_value",
            "name": "缺失值处理V2",
            "version": "0.2.0",
            "entrypoint": "algo_missing_value.entry:MissingValueAlgorithm",
            "category": "data_prepare",
            "description": "第二个版本的算法定义。",
        },
        "artifact": {
            "package_name": "algo-missing-value",
            "package_version": "0.2.0",
            "repository_url": "https://pypi.example.local/simple",
        },
    }


class DebugExecuteApiTests(unittest.TestCase):
    """调试执行接口测试。"""

    def setUp(self) -> None:
        """初始化测试客户端。"""

        self.client = TestClient(
            create_fastapi_app(
                settings=LibraryPlatformSettings(repository_backend="memory", database_url="")
            )
        )

    def test_execute_returns_result_for_registered_algorithm(self) -> None:
        """已注册算法应可以通过调试接口执行。"""

        self.client.post("/algorithms/register", json=build_valid_payload())

        response = self.client.post(
            "/algorithms/missing_value/execute",
            json={
                "version": "0.1.0",
                "inputs": {"dataset": [1, None, 3]},
                "params": {"fill_value": 9},
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["code"], "missing_value")
        self.assertEqual(body["version"], "0.1.0")
        self.assertEqual(body["result"]["dataset"], [1, 9, 3])

    def test_execute_uses_latest_version_when_version_is_omitted(self) -> None:
        """未传版本时应默认执行最新版本。"""

        self.client.post("/algorithms/register", json=build_valid_payload())
        self.client.post("/algorithms/register", json=build_second_version_payload())

        response = self.client.post(
            "/algorithms/missing_value/execute",
            json={
                "inputs": {"dataset": [1, None, 3]},
                "params": {"fill_value": 8},
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["version"], "0.2.0")
        self.assertEqual(body["result"]["dataset"], [1, 8, 3])

    def test_execute_returns_not_found_for_missing_algorithm(self) -> None:
        """未注册算法执行时应返回 404。"""

        response = self.client.post(
            "/algorithms/missing_value/execute",
            json={"inputs": {"dataset": []}, "params": {}},
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()

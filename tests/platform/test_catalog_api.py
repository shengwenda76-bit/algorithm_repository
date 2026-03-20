"""本文件用于放置算法目录查询接口相关测试。"""

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


class CatalogApiTests(unittest.TestCase):
    """目录查询接口测试。"""

    def setUp(self) -> None:
        """初始化测试客户端并预注册一条算法记录。"""

        self.client = TestClient(
            create_fastapi_app(
                settings=LibraryPlatformSettings(repository_backend="memory", database_url="")
            )
        )
        self.client.post("/algorithms/register", json=build_valid_payload())

    def build_second_version_payload(self) -> dict:
        """构造用于注册第二个版本的请求体。"""

        return {
            "definition": {
                "code": "missing_value",
                "name": "缺失值处理V2",
                "version": "0.2.0",
                "entrypoint": "algo_missing_value.entry:MissingValueAlgorithm",
                "category": "data_prepare",
                "description": "更新后的算法主信息。",
            },
            "artifact": {
                "package_name": "algo-missing-value",
                "package_version": "0.2.0",
                "repository_url": "https://pypi.example.local/simple",
            },
        }

    def test_get_algorithms_returns_registered_algorithm(self) -> None:
        """算法列表接口应返回已注册算法。"""

        response = self.client.get("/algorithms")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total"], 1)
        self.assertEqual(body["items"][0]["code"], "missing_value")

    def test_get_algorithm_returns_detail(self) -> None:
        """算法详情接口应返回指定算法信息。"""

        response = self.client.get("/algorithms/missing_value")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["code"], "missing_value")
        self.assertEqual(body["name"], "缺失值处理")

    def test_get_versions_returns_version_list(self) -> None:
        """版本列表接口应返回指定算法的全部版本。"""

        response = self.client.get("/algorithms/missing_value/versions")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["code"], "missing_value")
        self.assertEqual(len(body["items"]), 1)
        self.assertEqual(body["items"][0]["version"], "0.1.0")

    def test_registering_new_version_updates_algorithm_summary_and_latest_flag(self) -> None:
        """注册新版本后应更新算法主信息，并切换最新版本标记。"""

        register_response = self.client.post(
            "/algorithms/register",
            json=self.build_second_version_payload(),
        )
        algorithm_response = self.client.get("/algorithms/missing_value")
        versions_response = self.client.get("/algorithms/missing_value/versions")

        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(algorithm_response.status_code, 200)
        self.assertEqual(versions_response.status_code, 200)

        algorithm_body = algorithm_response.json()
        versions_body = versions_response.json()

        self.assertEqual(algorithm_body["name"], "缺失值处理V2")
        self.assertEqual(algorithm_body["category"], "data_prepare")
        self.assertEqual(algorithm_body["description"], "更新后的算法主信息。")
        self.assertEqual(algorithm_body["version"], "0.2.0")

        latest_flags = {
            item["version"]: item["is_latest"] for item in versions_body["items"]
        }
        self.assertEqual(latest_flags["0.1.0"], False)
        self.assertEqual(latest_flags["0.2.0"], True)

        old_version_detail_response = self.client.get("/algorithms/missing_value/versions/0.1.0")
        self.assertEqual(old_version_detail_response.status_code, 200)
        old_version_detail_body = old_version_detail_response.json()
        self.assertEqual(old_version_detail_body["name"], "缺失值处理V2")
        self.assertEqual(old_version_detail_body["definition"]["category"], "data_prepare")
        self.assertEqual(
            old_version_detail_body["definition"]["description"],
            "更新后的算法主信息。",
        )

    def test_get_version_detail_returns_definition_and_artifact(self) -> None:
        """版本详情接口应返回算法定义和算法包信息。"""

        response = self.client.get("/algorithms/missing_value/versions/0.1.0")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["definition"]["code"], "missing_value")
        self.assertEqual(body["artifact"]["package_name"], "algo-missing-value")


if __name__ == "__main__":
    unittest.main()

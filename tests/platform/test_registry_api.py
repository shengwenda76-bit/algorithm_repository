"""本文件用于放置算法注册和校验接口相关测试。"""

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
            "inputs": [{"name": "dataset", "data_type": "list", "description": "输入数据"}],
            "outputs": [{"name": "dataset", "data_type": "list", "description": "输出数据"}],
            "params": [
                {
                    "name": "fill_value",
                    "data_type": "any",
                    "description": "填充值",
                    "required": False,
                    "default": 0,
                }
            ],
            "resources": {"cpu": "1", "memory": "256Mi", "timeout": "30s"},
            "requirements": ["algorithm-sdk>=0.1.0"],
            "tags": ["cleaning", "demo"],
        },
        "artifact": {
            "package_name": "algo-missing-value",
            "package_version": "0.1.0",
            "repository_url": "https://pypi.example.local/simple",
            "artifact_type": "wheel",
            "filename": "algo_missing_value-0.1.0-py3-none-any.whl",
            "sha256": "abc123",
        },
    }


class RegistryApiTests(unittest.TestCase):
    """注册和校验接口测试。"""

    def setUp(self) -> None:
        """初始化测试客户端。"""

        self.client = TestClient(
            create_fastapi_app(
                settings=LibraryPlatformSettings(repository_backend="memory", database_url="")
            )
        )

    def test_validate_returns_missing_fields(self) -> None:
        """校验接口应返回缺失的元数据字段。"""

        response = self.client.post(
            "/algorithms/validate",
            json={
                "definition": {"code": "demo", "name": "Demo", "version": "1.0.0"},
                "artifact": {"package_name": "demo"},
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertFalse(body["valid"])
        self.assertIn("entrypoint", body["errors"]["definition"])
        self.assertIn("package_version", body["errors"]["artifact"])

    def test_register_returns_created_for_valid_payload(self) -> None:
        """注册接口应在请求合法时返回创建成功。"""

        response = self.client.post("/algorithms/register", json=build_valid_payload())

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["code"], "missing_value")
        self.assertEqual(body["version"], "0.1.0")
        self.assertEqual(body["status"], "registered")
        self.assertEqual(body["definition"]["inputs"][0]["name"], "dataset")
        self.assertEqual(body["artifact"]["artifact_type"], "wheel")

    def test_register_returns_conflict_for_duplicate_version(self) -> None:
        """同一算法版本重复注册时应返回冲突。"""

        payload = build_valid_payload()

        first_response = self.client.post("/algorithms/register", json=payload)
        second_response = self.client.post("/algorithms/register", json=payload)

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 409)
        self.assertIn("already registered", second_response.json()["detail"])

    def test_register_persists_rich_metadata_for_version_lookup(self) -> None:
        """注册后的版本详情应包含结构化元数据和制品信息。"""

        payload = build_valid_payload()

        register_response = self.client.post("/algorithms/register", json=payload)
        detail_response = self.client.get("/algorithms/missing_value/versions/0.1.0")

        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(detail_response.status_code, 200)
        body = detail_response.json()
        self.assertEqual(body["definition"]["resources"]["timeout"], "30s")
        self.assertEqual(body["definition"]["tags"], ["cleaning", "demo"])
        self.assertEqual(body["artifact"]["sha256"], "abc123")


if __name__ == "__main__":
    unittest.main()

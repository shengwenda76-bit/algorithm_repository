"""本文件用于放置算法库平台接口 schema 相关测试。"""

from __future__ import annotations

import unittest

from services.library_platform.schemas import (
    AlgorithmVersionDetailResponseSchema,
    DebugExecuteRequestSchema,
    RegistrationRequestSchema,
)


class PlatformSchemasTests(unittest.TestCase):
    """平台接口 schema 测试。"""

    def test_registration_request_accepts_rich_metadata_payload(self) -> None:
        """注册请求 schema 应能承载丰富的算法元数据和制品信息。"""

        payload = RegistrationRequestSchema(
            definition={
                "code": "missing_value",
                "name": "缺失值处理",
                "version": "0.1.0",
                "entrypoint": "algo_missing_value.entry:MissingValueAlgorithm",
                "inputs": [{"name": "dataset", "data_type": "list"}],
                "outputs": [{"name": "dataset", "data_type": "list"}],
                "params": [{"name": "fill_value", "data_type": "any", "required": False}],
                "resources": {"cpu": "1", "memory": "256Mi", "timeout": "30s"},
                "requirements": ["algorithm-sdk>=0.1.0"],
                "tags": ["cleaning", "demo"],
            },
            artifact={
                "package_name": "algo-missing-value",
                "package_version": "0.1.0",
                "repository_url": "https://pypi.example.local/simple",
                "artifact_type": "wheel",
                "filename": "algo_missing_value-0.1.0-py3-none-any.whl",
                "sha256": "abc123",
            },
        )

        dumped = payload.model_dump()

        self.assertEqual(dumped["definition"]["entrypoint"], "algo_missing_value.entry:MissingValueAlgorithm")
        self.assertEqual(dumped["definition"]["resources"]["timeout"], "30s")
        self.assertEqual(dumped["artifact"]["artifact_type"], "wheel")

    def test_version_detail_response_preserves_nested_fields(self) -> None:
        """版本详情响应 schema 应保留嵌套 definition 和 artifact 结构。"""

        response = AlgorithmVersionDetailResponseSchema(
            code="missing_value",
            name="缺失值处理",
            version="0.1.0",
            status="registered",
            definition={
                "code": "missing_value",
                "name": "缺失值处理",
                "version": "0.1.0",
                "entrypoint": "algo_missing_value.entry:MissingValueAlgorithm",
                "inputs": [{"name": "dataset", "data_type": "list"}],
                "outputs": [{"name": "dataset", "data_type": "list"}],
                "params": [{"name": "fill_value", "data_type": "any"}],
                "resources": {"cpu": "1", "memory": "256Mi", "timeout": "30s"},
                "requirements": ["algorithm-sdk>=0.1.0"],
                "tags": ["cleaning", "demo"],
                "status": "registered",
            },
            artifact={
                "code": "missing_value",
                "version": "0.1.0",
                "package_name": "algo-missing-value",
                "package_version": "0.1.0",
                "repository_url": "https://pypi.example.local/simple",
                "artifact_type": "wheel",
                "filename": "algo_missing_value-0.1.0-py3-none-any.whl",
                "sha256": "abc123",
            },
        )

        dumped = response.model_dump()

        self.assertEqual(dumped["definition"]["inputs"][0]["name"], "dataset")
        self.assertEqual(dumped["artifact"]["sha256"], "abc123")

    def test_debug_execute_request_defaults_to_empty_payloads(self) -> None:
        """调试执行请求 schema 应允许省略 inputs 和 params。"""

        request = DebugExecuteRequestSchema()

        self.assertEqual(request.model_dump(), {"version": None, "inputs": {}, "params": {}})


if __name__ == "__main__":
    unittest.main()

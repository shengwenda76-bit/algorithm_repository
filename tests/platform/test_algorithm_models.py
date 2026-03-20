"""本文件用于放置算法库平台模型层相关测试。"""

from __future__ import annotations

import unittest

from sdk.algorithm_sdk.contracts import FieldSpec, ResourceSpec
from services.library_platform.models import AlgorithmDefinition, PackageArtifact


class AlgorithmModelsTests(unittest.TestCase):
    """平台注册模型测试。"""

    def test_algorithm_definition_contains_rich_metadata_fields(self) -> None:
        """算法定义应能承载结构化元数据字段。"""

        definition = AlgorithmDefinition(
            code="missing_value",
            name="缺失值处理",
            version="0.1.0",
            entrypoint="algo_missing_value.entry:MissingValueAlgorithm",
            category="data_cleaning",
            description="用于处理缺失值的示例算法。",
            inputs=[FieldSpec(name="dataset", data_type="list")],
            outputs=[FieldSpec(name="dataset", data_type="list")],
            params=[FieldSpec(name="fill_value", data_type="any", required=False, default=0)],
            resources=ResourceSpec(cpu="1", memory="256Mi", timeout="30s"),
            requirements=["algorithm-sdk>=0.1.0"],
            tags=["cleaning", "demo"],
            status="registered",
        )

        payload = definition.to_dict()

        self.assertEqual(payload["entrypoint"], "algo_missing_value.entry:MissingValueAlgorithm")
        self.assertEqual(payload["inputs"][0]["name"], "dataset")
        self.assertEqual(payload["params"][0]["default"], 0)
        self.assertEqual(payload["resources"]["timeout"], "30s")
        self.assertEqual(payload["requirements"], ["algorithm-sdk>=0.1.0"])
        self.assertEqual(payload["tags"], ["cleaning", "demo"])
        self.assertEqual(payload["status"], "registered")

    def test_package_artifact_contains_distribution_fields(self) -> None:
        """算法包信息应包含制品定位相关字段。"""

        artifact = PackageArtifact(
            code="missing_value",
            version="0.1.0",
            package_name="algo-missing-value",
            package_version="0.1.0",
            repository_url="https://pypi.example.local/simple",
            artifact_type="wheel",
            filename="algo_missing_value-0.1.0-py3-none-any.whl",
            sha256="abc123",
        )

        payload = artifact.to_dict()

        self.assertEqual(payload["artifact_type"], "wheel")
        self.assertEqual(payload["filename"], "algo_missing_value-0.1.0-py3-none-any.whl")
        self.assertEqual(payload["sha256"], "abc123")


if __name__ == "__main__":
    unittest.main()

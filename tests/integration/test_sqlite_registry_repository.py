"""本文件用于验证 sqlite 注册中心仓储的最小持久化行为。"""

from __future__ import annotations

import unittest

from sdk.algorithm_sdk.contracts import FieldSpec, ResourceSpec
from services.library_platform.models import AlgorithmDefinition, PackageArtifact
from services.library_platform.registry.repository import SqliteRegistryRepository


def build_definition(
    version: str,
    *,
    name: str = "缺失值处理",
    category: str = "data_cleaning",
    description: str = "用于处理缺失值的示例算法。",
) -> AlgorithmDefinition:
    """构造算法定义对象。"""

    return AlgorithmDefinition(
        code="missing_value",
        name=name,
        version=version,
        entrypoint="algo_missing_value.entry:MissingValueAlgorithm",
        category=category,
        description=description,
        inputs=[FieldSpec(name="dataset", data_type="list")],
        outputs=[FieldSpec(name="dataset", data_type="list")],
        params=[FieldSpec(name="fill_value", data_type="any", required=False, default=0)],
        resources=ResourceSpec(cpu="1", memory="256Mi", timeout="30s"),
        requirements=["algorithm-sdk>=0.1.0"],
        tags=["cleaning", "demo"],
        status="registered",
    )


def build_artifact(version: str) -> PackageArtifact:
    """构造算法制品对象。"""

    return PackageArtifact(
        code="missing_value",
        version=version,
        package_name="algo-missing-value",
        package_version=version,
        repository_url="https://pypi.example.local/simple",
        artifact_type="wheel",
        filename=f"algo_missing_value-{version}-py3-none-any.whl",
        sha256=f"sha256-{version}",
    )


class SqliteRegistryRepositoryTests(unittest.TestCase):
    """sqlite 仓储测试。"""

    def setUp(self) -> None:
        """创建测试仓储。"""

        self.repository = SqliteRegistryRepository(database_url="sqlite:///:memory:")
        self.addCleanup(self.repository.close)

    def test_save_registration_marks_only_latest_version(self) -> None:
        """注册多个版本后应只保留一个最新版本。"""

        self.repository.save_registration(build_definition("0.1.0"), build_artifact("0.1.0"))
        self.repository.save_registration(
            build_definition("0.2.0", name="缺失值处理V2"),
            build_artifact("0.2.0"),
        )

        versions = self.repository.list_versions("missing_value")

        self.assertEqual(
            {item["version"]: item["is_latest"] for item in versions},
            {"0.1.0": False, "0.2.0": True},
        )

    def test_save_registration_updates_algorithm_summary(self) -> None:
        """同 code 注册新版本时应更新主表摘要信息。"""

        self.repository.save_registration(build_definition("0.1.0"), build_artifact("0.1.0"))
        self.repository.save_registration(
            build_definition(
                "0.2.0",
                name="缺失值处理V2",
                category="data_prepare",
                description="更新后的算法主信息。",
            ),
            build_artifact("0.2.0"),
        )

        algorithm = self.repository.get_algorithm("missing_value")
        version_detail = self.repository.get_version_detail("missing_value", "0.1.0")

        self.assertIsNotNone(algorithm)
        self.assertEqual(algorithm["name"], "缺失值处理V2")
        self.assertEqual(algorithm["version"], "0.2.0")
        self.assertEqual(version_detail["definition"]["category"], "data_prepare")
        self.assertEqual(version_detail["definition"]["description"], "更新后的算法主信息。")

    def test_get_execution_target_defaults_to_latest_version(self) -> None:
        """未传版本时应返回最新版本的执行目标。"""

        self.repository.save_registration(build_definition("0.1.0"), build_artifact("0.1.0"))
        self.repository.save_registration(
            build_definition("0.2.0", name="缺失值处理V2"),
            build_artifact("0.2.0"),
        )

        target = self.repository.get_execution_target("missing_value")

        self.assertIsNotNone(target)
        self.assertEqual(target["version"], "0.2.0")
        self.assertEqual(
            target["entrypoint"],
            "algo_missing_value.entry:MissingValueAlgorithm",
        )


if __name__ == "__main__":
    unittest.main()

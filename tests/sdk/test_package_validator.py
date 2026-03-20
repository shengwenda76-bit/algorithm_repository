"""本文件用于放置算法元数据和算法包校验相关测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SDK_ROOT = PROJECT_ROOT / "sdk"
if str(SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(SDK_ROOT))

from algorithm_sdk.validators import validate_algorithm_meta, validate_package_artifact


class PackageValidatorTests(unittest.TestCase):
    """算法元数据和算法包校验测试。"""

    def test_validate_algorithm_meta_requires_entrypoint(self) -> None:
        """缺少入口定义时应返回缺失字段。"""

        payload = {"code": "demo", "name": "演示算法", "version": "1.0.0"}

        errors = validate_algorithm_meta(payload)

        self.assertIn("entrypoint", errors)

    def test_validate_algorithm_meta_accepts_rich_payload(self) -> None:
        """完整元数据应通过基础校验。"""

        payload = {
            "code": "demo",
            "name": "演示算法",
            "version": "1.0.0",
            "entrypoint": "demo.entry:DemoAlgorithm",
            "inputs": [{"name": "dataset", "data_type": "list"}],
            "outputs": [{"name": "result", "data_type": "list"}],
            "params": [{"name": "fill_value", "data_type": "int"}],
            "resources": {"cpu": "1", "memory": "256Mi", "timeout": "30s"},
            "requirements": ["pandas>=2.0"],
            "tags": ["cleaning"],
        }

        errors = validate_algorithm_meta(payload)

        self.assertEqual(errors, [])

    def test_validate_package_artifact_requires_core_fields(self) -> None:
        """算法包信息应校验包名、版本和仓库地址。"""

        payload = {"package_name": "demo"}

        errors = validate_package_artifact(payload)

        self.assertIn("package_version", errors)
        self.assertIn("repository_url", errors)


if __name__ == "__main__":
    unittest.main()

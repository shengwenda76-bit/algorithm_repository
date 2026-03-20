"""本文件用于放置算法 SDK 契约相关测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SDK_ROOT = PROJECT_ROOT / "sdk"
if str(SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(SDK_ROOT))

from algorithm_sdk.contracts import FieldSpec, ResourceSpec
from algorithm_sdk.meta import AlgorithmMeta


class AlgorithmContractsTests(unittest.TestCase):
    """算法 SDK 契约测试。"""

    def test_algorithm_meta_contains_structured_contract_fields(self) -> None:
        """算法元数据应能承载 inputs、outputs、params 和 resources。"""

        meta = AlgorithmMeta(
            code="demo",
            name="演示算法",
            version="1.0.0",
            entrypoint="demo.entry:DemoAlgorithm",
            inputs=[FieldSpec(name="dataset", data_type="list", description="输入数据")],
            outputs=[FieldSpec(name="result", data_type="list", description="输出数据")],
            params=[FieldSpec(name="fill_value", data_type="int", description="填充值")],
            resources=ResourceSpec(cpu="1", memory="256Mi", timeout="30s"),
            requirements=["pandas>=2.0"],
            tags=["cleaning", "demo"],
        )

        self.assertEqual(meta.entrypoint, "demo.entry:DemoAlgorithm")
        self.assertEqual(meta.inputs[0].name, "dataset")
        self.assertEqual(meta.outputs[0].name, "result")
        self.assertEqual(meta.params[0].name, "fill_value")
        self.assertEqual(meta.resources.timeout, "30s")
        self.assertEqual(meta.requirements, ["pandas>=2.0"])
        self.assertEqual(meta.tags, ["cleaning", "demo"])

    def test_algorithm_meta_to_dict_contains_nested_contracts(self) -> None:
        """算法元数据转字典时应保留嵌套契约结构。"""

        meta = AlgorithmMeta(
            code="demo",
            name="演示算法",
            version="1.0.0",
            entrypoint="demo.entry:DemoAlgorithm",
            inputs=[FieldSpec(name="dataset", data_type="list")],
            resources=ResourceSpec(cpu="1"),
        )

        payload = meta.to_dict()

        self.assertEqual(payload["code"], "demo")
        self.assertEqual(payload["inputs"][0]["name"], "dataset")
        self.assertEqual(payload["resources"]["cpu"], "1")


if __name__ == "__main__":
    unittest.main()

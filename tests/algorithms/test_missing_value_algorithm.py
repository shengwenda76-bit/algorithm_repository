"""本文件用于放置缺失值处理示例算法的行为测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SDK_ROOT = PROJECT_ROOT / "sdk"
ALGORITHM_ROOT = PROJECT_ROOT / "algorithms" / "algo_missing_value"
for path in (SDK_ROOT, ALGORITHM_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from algo_missing_value.entry import MissingValueAlgorithm
from algo_missing_value.meta import ALGORITHM_META


class MissingValueAlgorithmTests(unittest.TestCase):
    """缺失值处理示例算法测试。"""

    def test_missing_value_algorithm_replaces_none(self) -> None:
        """算法执行时应将空值替换为指定默认值。"""

        result = MissingValueAlgorithm().execute(
            {"dataset": [1, None, 3]},
            {"fill_value": 0},
        )

        self.assertEqual(result["dataset"], [1, 0, 3])

    def test_missing_value_meta_contains_rich_contract_information(self) -> None:
        """示例算法元数据应包含输入输出、参数和资源定义。"""

        self.assertEqual(ALGORITHM_META.entrypoint, "algo_missing_value.entry:MissingValueAlgorithm")
        self.assertEqual(ALGORITHM_META.inputs[0].name, "dataset")
        self.assertEqual(ALGORITHM_META.outputs[0].name, "dataset")
        self.assertEqual(ALGORITHM_META.params[0].name, "fill_value")
        self.assertEqual(ALGORITHM_META.resources.timeout, "30s")
        self.assertEqual(ALGORITHM_META.tags, ["cleaning", "demo"])


if __name__ == "__main__":
    unittest.main()

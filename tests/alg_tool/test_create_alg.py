"""本文件用于验证可移植 alg_tool 的算法脚手架生成功能。"""

from __future__ import annotations

import unittest
from contextlib import contextmanager
from pathlib import Path
import shutil
import uuid

from alg_tool.common import clear_package_modules
from alg_tool.create_alg import scaffold_algorithm


@contextmanager
def temporary_workspace() -> Path:
    """Create a temporary writable workspace inside the repository."""

    base_dir = Path.cwd() / ".tmp_alg_tool_tests"
    base_dir.mkdir(parents=True, exist_ok=True)
    workspace = base_dir / f"workspace_{uuid.uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=True)
    try:
        yield workspace
    finally:
        clear_package_modules("algo_missing_value")
        shutil.rmtree(workspace, ignore_errors=True)


class CreateAlgTests(unittest.TestCase):
    """算法脚手架生成测试。"""

    def test_scaffold_algorithm_creates_expected_files(self) -> None:
        """在空目录中应生成完整算法模板。"""

        with temporary_workspace() as workspace:

            scaffold_algorithm(workspace=workspace, name="algo_missing_value")

            algorithm_root = workspace / "algorithms" / "algo_missing_value"
            self.assertTrue((algorithm_root / "pyproject.toml").exists())
            self.assertTrue((algorithm_root / "README.md").exists())
            self.assertTrue((algorithm_root / "algo_missing_value" / "__init__.py").exists())
            self.assertTrue((algorithm_root / "algo_missing_value" / "entry.py").exists())
            self.assertTrue((algorithm_root / "algo_missing_value" / "meta.py").exists())
            self.assertTrue((algorithm_root / "algo_missing_value" / "schema.py").exists())
            self.assertTrue((algorithm_root / "tests" / "test_algo_missing_value.py").exists())

    def test_scaffold_algorithm_renders_portable_readme_and_test_template(self) -> None:
        """生成的 README 和测试模板应包含可移植使用说明。"""

        with temporary_workspace() as workspace:

            scaffold_algorithm(workspace=workspace, name="algo_missing_value")

            algorithm_root = workspace / "algorithms" / "algo_missing_value"
            readme = (algorithm_root / "README.md").read_text(encoding="utf-8")
            test_content = (
                algorithm_root / "tests" / "test_algo_missing_value.py"
            ).read_text(encoding="utf-8")

            self.assertIn("这个算法做什么", readme)
            self.assertIn("怎么本地测试", readme)
            self.assertIn("怎么发布", readme)
            self.assertIn("alg_tool", test_content)
            self.assertIn("vendor", test_content)


if __name__ == "__main__":
    unittest.main()

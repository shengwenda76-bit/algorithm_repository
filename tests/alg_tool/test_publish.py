"""本文件用于验证可移植 alg_tool 的发布前校验和本地发布流程。"""

from __future__ import annotations

from contextlib import contextmanager
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
import shutil
import uuid

from alg_tool.common import clear_package_modules
from alg_tool.create_alg import scaffold_algorithm
from alg_tool.publish import (
    build_register_payload,
    load_algorithm_context,
    probe_remote_endpoint,
    publish_algorithm,
)
from alg_tool.settings import load_publish_settings


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


class FakeCommandRunner:
    """用于测试的命令执行器。"""

    def __init__(self) -> None:
        self.calls: list[tuple[list[str], Path]] = []

    def __call__(self, command: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
        self.calls.append((command, cwd))
        if command[1:3] == ["-m", "pytest"]:
            return "pytest ok"

        if command[1:3] == ["-m", "build"]:
            dist_dir = cwd / "dist"
            dist_dir.mkdir(parents=True, exist_ok=True)
            (dist_dir / "algo_missing_value-0.1.0-py3-none-any.whl").write_bytes(b"wheel")
            (dist_dir / "algo_missing_value-0.1.0.tar.gz").write_bytes(b"sdist")
            return "build ok"

        return "ok"


class PublishAlgTests(unittest.TestCase):
    """发布工具测试。"""

    def test_load_publish_settings_reads_defaults_from_settings_module(self) -> None:
        """settings 模块应提供默认发布配置。"""

        settings = load_publish_settings(env={})

        self.assertEqual(settings.pypi.repository_url, "")
        self.assertEqual(settings.pypi.username, "")
        self.assertEqual(settings.pypi.password, "")
        self.assertEqual(settings.platform.register_url, "")
        self.assertEqual(settings.platform.token, "")
        self.assertEqual(settings.pypi.timeout_seconds, 10)
        self.assertEqual(settings.platform.timeout_seconds, 10)
        self.assertTrue(settings.validation.check_remote_connectivity)

    def test_load_publish_settings_allows_environment_overrides(self) -> None:
        """环境变量应能覆盖 settings.py 默认值。"""

        settings = load_publish_settings(
            env={
                "ALG_TOOL_PYPI_REPOSITORY_URL": "https://pypi.example.local/simple",
                "ALG_TOOL_PYPI_USERNAME": "alice",
                "ALG_TOOL_PYPI_PASSWORD": "secret",
                "ALG_TOOL_PLATFORM_REGISTER_URL": "https://platform.example.local/algorithms/register",
                "ALG_TOOL_PLATFORM_TOKEN": "token-123",
                "ALG_TOOL_PYPI_TIMEOUT_SECONDS": "25",
                "ALG_TOOL_PLATFORM_TIMEOUT_SECONDS": "15",
                "ALG_TOOL_VALIDATION_CHECK_REMOTE_CONNECTIVITY": "false",
            }
        )

        self.assertEqual(settings.pypi.repository_url, "https://pypi.example.local/simple")
        self.assertEqual(settings.pypi.username, "alice")
        self.assertEqual(settings.pypi.password, "secret")
        self.assertEqual(settings.platform.register_url, "https://platform.example.local/algorithms/register")
        self.assertEqual(settings.platform.token, "token-123")
        self.assertEqual(settings.pypi.timeout_seconds, 25)
        self.assertEqual(settings.platform.timeout_seconds, 15)
        self.assertFalse(settings.validation.check_remote_connectivity)

    def test_load_algorithm_context_reads_generated_algorithm_metadata(self) -> None:
        """应能从生成的算法包中读取元数据上下文。"""

        with temporary_workspace() as workspace:
            scaffold_algorithm(workspace=workspace, name="algo_missing_value")

            context = load_algorithm_context(workspace=workspace, name="algo_missing_value")

            self.assertEqual(context.algorithm_name, "algo_missing_value")
            self.assertEqual(context.algorithm_code, "missing_value")
            self.assertEqual(context.version, "0.1.0")
            self.assertEqual(context.entrypoint, "algo_missing_value.entry:Algorithm")

    def test_build_register_payload_contains_definition_and_artifact_sections(self) -> None:
        """注册载荷应包含 definition 和 artifact 两部分。"""

        with temporary_workspace() as workspace:
            scaffold_algorithm(workspace=workspace, name="algo_missing_value")
            context = load_algorithm_context(workspace=workspace, name="algo_missing_value")

            payload = build_register_payload(
                context=context,
                sha256="abc123",
                repository_url="https://pypi.example.local/simple",
                artifact_type="wheel",
                filename="algo_missing_value-0.1.0-py3-none-any.whl",
            )

            self.assertIn("definition", payload)
            self.assertIn("artifact", payload)
            self.assertEqual(payload["definition"]["code"], "missing_value")
            self.assertEqual(payload["artifact"]["sha256"], "abc123")

    def test_publish_algorithm_rejects_partial_upload_configuration(self) -> None:
        """上传配置只配了一部分时应明确报错。"""

        with temporary_workspace() as workspace:
            scaffold_algorithm(workspace=workspace, name="algo_missing_value")

            with self.assertRaisesRegex(ValueError, "PyPI upload configuration is incomplete"):
                publish_algorithm(
                    workspace=workspace,
                    name="algo_missing_value",
                    env={
                        "ALG_TOOL_PYPI_REPOSITORY_URL": "https://pypi.example.local/simple",
                        "ALG_TOOL_PYPI_USERNAME": "alice",
                    },
                    runner=FakeCommandRunner(),
                )

    def test_publish_algorithm_rejects_registration_without_repository_url(self) -> None:
        """平台注册启用时如果缺少 artifact 仓库地址应失败。"""

        with temporary_workspace() as workspace:
            scaffold_algorithm(workspace=workspace, name="algo_missing_value")

            with self.assertRaisesRegex(ValueError, "PyPI repository_url must be configured"):
                publish_algorithm(
                    workspace=workspace,
                    name="algo_missing_value",
                    env={
                        "ALG_TOOL_PLATFORM_REGISTER_URL": "https://platform.example.local/algorithms/register",
                    },
                    runner=FakeCommandRunner(),
                )

    def test_publish_algorithm_runs_local_flow_without_network_configuration(self) -> None:
        """未配置上传和注册时应只执行本地校验、测试和构建。"""

        with temporary_workspace() as workspace:
            scaffold_algorithm(workspace=workspace, name="algo_missing_value")
            runner = FakeCommandRunner()

            summary = publish_algorithm(
                workspace=workspace,
                name="algo_missing_value",
                env={},
                runner=runner,
            )

            self.assertEqual(summary["validation_status"], "passed")
            self.assertEqual(summary["test_status"], "passed")
            self.assertEqual(summary["build_status"], "passed")
            self.assertEqual(summary["upload_status"], "skipped")
            self.assertEqual(summary["registration_status"], "skipped")
            self.assertEqual(summary["version"], "0.1.0")
            self.assertTrue(summary["wheel_filename"].endswith(".whl"))
            self.assertEqual(len(runner.calls), 2)
            self.assertEqual(runner.calls[0][0][:3], [sys.executable, "-m", "pytest"])
            self.assertEqual(runner.calls[1][0][:3], [sys.executable, "-m", "build"])

    def test_publish_algorithm_probes_remote_endpoints_when_enabled(self) -> None:
        """配置完整且启用远端检查时，应先探测仓库和平台注册地址。"""

        with temporary_workspace() as workspace:
            scaffold_algorithm(workspace=workspace, name="algo_missing_value")
            runner = FakeCommandRunner()

            with patch("alg_tool.publish.probe_remote_endpoint") as probe_mock, patch(
                "alg_tool.publish._register_algorithm"
            ) as register_mock:
                summary = publish_algorithm(
                    workspace=workspace,
                    name="algo_missing_value",
                    env={
                        "ALG_TOOL_PYPI_REPOSITORY_URL": "https://pypi.example.local/simple",
                        "ALG_TOOL_PYPI_USERNAME": "alice",
                        "ALG_TOOL_PYPI_PASSWORD": "secret",
                        "ALG_TOOL_PLATFORM_REGISTER_URL": "https://platform.example.local/algorithms/register",
                        "ALG_TOOL_PLATFORM_TOKEN": "token-123",
                    },
                    runner=runner,
                )

            self.assertEqual(summary["upload_status"], "passed")
            self.assertEqual(summary["registration_status"], "passed")
            self.assertEqual(probe_mock.call_count, 2)
            self.assertEqual(probe_mock.call_args_list[0].args[0], "https://pypi.example.local/simple")
            self.assertEqual(
                probe_mock.call_args_list[1].args[0],
                "https://platform.example.local/algorithms/register",
            )
            register_mock.assert_called_once()

    def test_publish_algorithm_skips_remote_probe_when_disabled(self) -> None:
        """显式关闭远端检查时，不应探测远端地址。"""

        with temporary_workspace() as workspace:
            scaffold_algorithm(workspace=workspace, name="algo_missing_value")
            runner = FakeCommandRunner()

            with patch("alg_tool.publish.probe_remote_endpoint") as probe_mock, patch(
                "alg_tool.publish._register_algorithm"
            ):
                summary = publish_algorithm(
                    workspace=workspace,
                    name="algo_missing_value",
                    env={
                        "ALG_TOOL_PYPI_REPOSITORY_URL": "https://pypi.example.local/simple",
                        "ALG_TOOL_PYPI_USERNAME": "alice",
                        "ALG_TOOL_PYPI_PASSWORD": "secret",
                        "ALG_TOOL_PLATFORM_REGISTER_URL": "https://platform.example.local/algorithms/register",
                        "ALG_TOOL_VALIDATION_CHECK_REMOTE_CONNECTIVITY": "false",
                    },
                    runner=runner,
                )

            self.assertEqual(summary["upload_status"], "passed")
            self.assertEqual(summary["registration_status"], "passed")
            probe_mock.assert_not_called()

    def test_probe_remote_endpoint_raises_clear_error_for_unreachable_url(self) -> None:
        """远端地址不可达时应抛出清晰错误。"""

        with patch("alg_tool.publish.request.urlopen", side_effect=OSError("network down")):
            with self.assertRaisesRegex(RuntimeError, "Remote endpoint check failed"):
                probe_remote_endpoint("https://pypi.example.local/simple", timeout_seconds=5)


if __name__ == "__main__":
    unittest.main()

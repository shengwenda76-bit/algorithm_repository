from pathlib import Path


def test_template_declares_plugin_entrypoint() -> None:
    content = Path("app/algorithms/_algo_template/pyproject.toml.example").read_text(
        encoding="utf-8"
    )
    assert '[project.entry-points."algorithm_platform.algorithms"]' in content

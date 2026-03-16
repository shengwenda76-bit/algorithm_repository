from pathlib import Path


def test_runtime_package_layout_exists() -> None:
    assert Path("app/algorithms/runtime_packages/algo_missing_value").exists()
    assert Path("app/algorithms/_algo_template/src/algo_template/entry.py").exists()

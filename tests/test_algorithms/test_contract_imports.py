from pathlib import Path


def test_runtime_packages_do_not_import_platform_internal_base() -> None:
    files = [
        "app/algorithms/runtime_packages/algo_missing_value/entry.py",
        "app/algorithms/runtime_packages/algo_missing_value/meta.py",
        "app/algorithms/runtime_packages/algo_outliers/entry.py",
        "app/algorithms/runtime_packages/algo_outliers/meta.py",
        "app/algorithms/runtime_packages/algo_standardize/entry.py",
        "app/algorithms/runtime_packages/algo_standardize/meta.py",
        "app/algorithms/_algo_template/src/algo_template/entry.py",
        "app/algorithms/_algo_template/src/algo_template/meta.py",
    ]
    for path in files:
        content = Path(path).read_text(encoding="utf-8")
        assert "from app.algorithms.base import" not in content

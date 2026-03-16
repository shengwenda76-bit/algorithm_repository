from app.algorithms.runtime_packages.algo_missing_value.entry import MissingValueAlgorithm
from app.algorithms.runtime_packages.algo_standardize.entry import StandardizeAlgorithm


def test_runtime_packages_expose_algorithm_classes() -> None:
    assert MissingValueAlgorithm.get_meta().algo_code == "missing_value"
    assert StandardizeAlgorithm.get_meta().algo_code == "standardize"

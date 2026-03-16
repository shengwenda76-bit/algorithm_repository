from app.algorithms.registry import AlgorithmRegistry
from app.algorithms.runtime_packages.algo_missing_value.entry import MissingValueAlgorithm


def test_registry_requires_explicit_platform_registration() -> None:
    AlgorithmRegistry.clear()
    assert not AlgorithmRegistry.contains("missing_value", "1.0.0")
    AlgorithmRegistry.register(MissingValueAlgorithm)
    assert AlgorithmRegistry.contains("missing_value", "1.0.0")

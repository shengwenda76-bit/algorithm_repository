from app.algorithms.registry import AlgorithmRegistry
from app.services.algorithm_catalog_service import algorithm_catalog_service
from app.services.plugin_discovery import plugin_discovery


def test_plugin_discovery_loads_runtime_package_entry() -> None:
    AlgorithmRegistry.clear()
    artifact = algorithm_catalog_service.get_resolved_artifact("missing_value", "1.0.0")
    algorithm_cls = plugin_discovery.load_algorithm_class(artifact)
    assert algorithm_cls.get_meta().algo_code == "missing_value"

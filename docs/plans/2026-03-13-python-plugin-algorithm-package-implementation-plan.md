# Python 插件化算法包改造 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将当前 `app/algorithms` 下的示例算法改造成标准 Python 插件包形态，并将平台运行时改为“平台显式注册”的插件发现链路。

**Architecture:** 运行时目录改为 `runtime_packages/` 模拟“已安装算法包”，算法开发模板改为 `_algo_template/` 目录模板，`AlgorithmRegistry` 保持纯运行时索引，`AlgorithmLoader` 从“导入副作用注册”切换到“平台发现入口类并显式注册”。当前阶段先用本地包目录模拟已安装插件，后续再替换为真实私有 PyPI wheel 下载与 `entry_points` 发现。

**Tech Stack:** FastAPI, Pydantic, Python importlib, importlib.metadata（后续真实接入）, pytest

---

### Task 1: 重构 `app/algorithms` 目录骨架

**Files:**
- Delete: `app/algorithms/_algo_template.py`
- Delete: `app/algorithms/data_cleaning/`
- Delete: `app/algorithms/data_processing/`
- Create: `app/algorithms/runtime_packages/__init__.py`
- Create: `app/algorithms/runtime_packages/algo_missing_value/__init__.py`
- Create: `app/algorithms/runtime_packages/algo_outliers/__init__.py`
- Create: `app/algorithms/runtime_packages/algo_standardize/__init__.py`
- Create: `app/algorithms/_algo_template/README.md`
- Create: `app/algorithms/_algo_template/pyproject.toml.example`
- Create: `app/algorithms/_algo_template/src/algo_template/__init__.py`
- Create: `app/algorithms/_algo_template/src/algo_template/entry.py`
- Create: `app/algorithms/_algo_template/src/algo_template/meta.py`
- Create: `app/algorithms/_algo_template/src/algo_template/validators.py`
- Create: `app/algorithms/_algo_template/tests/test_entry.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_runtime_package_layout_exists():
    assert Path("app/algorithms/runtime_packages/algo_missing_value").exists()
    assert Path("app/algorithms/_algo_template/src/algo_template/entry.py").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_algorithms/test_algorithm_package_layout.py::test_runtime_package_layout_exists -v`

Expected: FAIL because the new directories do not exist yet.

**Step 3: Write minimal implementation**

Create the new directories and remove the old category-based runtime layout.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_algorithms/test_algorithm_package_layout.py::test_runtime_package_layout_exists -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/algorithms tests/test_algorithms/test_algorithm_package_layout.py
git commit -m "refactor: reshape algorithms as runtime plugin packages"
```

### Task 2: 定义标准算法包模板

**Files:**
- Modify: `app/algorithms/_algo_template/README.md`
- Modify: `app/algorithms/_algo_template/pyproject.toml.example`
- Modify: `app/algorithms/_algo_template/src/algo_template/entry.py`
- Modify: `app/algorithms/_algo_template/src/algo_template/meta.py`
- Modify: `app/algorithms/_algo_template/src/algo_template/validators.py`
- Test: `app/algorithms/_algo_template/tests/test_entry.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_template_declares_plugin_entrypoint():
    content = Path("app/algorithms/_algo_template/pyproject.toml.example").read_text(encoding="utf-8")
    assert '[project.entry-points."algorithm_platform.algorithms"]' in content
```

**Step 2: Run test to verify it fails**

Run: `pytest app/algorithms/_algo_template/tests/test_entry.py::test_template_declares_plugin_entrypoint -v`

Expected: FAIL because the template file is empty.

**Step 3: Write minimal implementation**

Add:

```toml
[project.entry-points."algorithm_platform.algorithms"]
algo_template = "algo_template.entry:TemplateAlgorithm"
```

and create a minimal `entry.py` / `meta.py` / `validators.py` template.

**Step 4: Run test to verify it passes**

Run: `pytest app/algorithms/_algo_template/tests/test_entry.py::test_template_declares_plugin_entrypoint -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/algorithms/_algo_template
git commit -m "docs: add standard plugin algorithm package template"
```

### Task 3: 将三个示例算法改造成标准包形态

**Files:**
- Create: `app/algorithms/runtime_packages/algo_missing_value/entry.py`
- Create: `app/algorithms/runtime_packages/algo_missing_value/meta.py`
- Create: `app/algorithms/runtime_packages/algo_missing_value/validators.py`
- Create: `app/algorithms/runtime_packages/algo_outliers/entry.py`
- Create: `app/algorithms/runtime_packages/algo_outliers/meta.py`
- Create: `app/algorithms/runtime_packages/algo_outliers/validators.py`
- Create: `app/algorithms/runtime_packages/algo_standardize/entry.py`
- Create: `app/algorithms/runtime_packages/algo_standardize/meta.py`
- Create: `app/algorithms/runtime_packages/algo_standardize/validators.py`
- Test: `tests/test_algorithms/test_runtime_packages.py`

**Step 1: Write the failing test**

```python
from app.algorithms.runtime_packages.algo_missing_value.entry import MissingValueAlgorithm
from app.algorithms.runtime_packages.algo_standardize.entry import StandardizeAlgorithm


def test_runtime_packages_expose_algorithm_classes():
    assert MissingValueAlgorithm.get_meta().algo_code == "missing_value"
    assert StandardizeAlgorithm.get_meta().algo_code == "standardize"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_algorithms/test_runtime_packages.py::test_runtime_packages_expose_algorithm_classes -v`

Expected: FAIL because the runtime package modules do not exist.

**Step 3: Write minimal implementation**

For each package:

```python
# meta.py
from app.algorithms.base import AlgorithmMeta, ExecutionMode

ALGORITHM_META = AlgorithmMeta(
    algo_code="missing_value",
    name="缺失值处理",
    category="data_cleaning",
    version="1.0.0",
    execution_mode=ExecutionMode.IN_MEMORY,
    description="将空值替换为指定默认值。",
)
```

```python
# entry.py
from app.algorithms.base import BaseAlgorithm
from .meta import ALGORITHM_META
from .validators import validate_inputs, validate_params


class MissingValueAlgorithm(BaseAlgorithm):
    meta = ALGORITHM_META

    def execute(self, inputs: dict, params: dict) -> dict:
        validate_inputs(inputs)
        validate_params(params)
        ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_algorithms/test_runtime_packages.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/algorithms/runtime_packages tests/test_algorithms/test_runtime_packages.py
git commit -m "feat: convert sample algorithms to plugin package layout"
```

### Task 4: 提取独立契约包并替换平台内部导入

**Files:**
- Create: `app/contracts/__init__.py`
- Create: `app/contracts/algorithm.py`
- Modify: `app/algorithms/base.py`
- Modify: `app/algorithms/runtime_packages/algo_missing_value/entry.py`
- Modify: `app/algorithms/runtime_packages/algo_missing_value/meta.py`
- Modify: `app/algorithms/runtime_packages/algo_outliers/entry.py`
- Modify: `app/algorithms/runtime_packages/algo_outliers/meta.py`
- Modify: `app/algorithms/runtime_packages/algo_standardize/entry.py`
- Modify: `app/algorithms/runtime_packages/algo_standardize/meta.py`
- Modify: `app/algorithms/_algo_template/src/algo_template/entry.py`
- Modify: `app/algorithms/_algo_template/src/algo_template/meta.py`
- Test: `tests/test_algorithms/test_contract_imports.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_runtime_packages_do_not_import_platform_internal_base():
    files = [
        "app/algorithms/runtime_packages/algo_missing_value/entry.py",
        "app/algorithms/_algo_template/src/algo_template/entry.py",
    ]
    for path in files:
        content = Path(path).read_text(encoding="utf-8")
        assert "from app.algorithms.base import" not in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_algorithms/test_contract_imports.py::test_runtime_packages_do_not_import_platform_internal_base -v`

Expected: FAIL because runtime packages still import `app.algorithms.base`.

**Step 3: Write minimal implementation**

Create a shared contract module:

```python
# app/contracts/algorithm.py
from app.algorithms.base import BaseAlgorithm, AlgorithmMeta, ExecutionMode
```

Then update runtime packages and template files to import from the shared contract module instead of `app.algorithms.base`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_algorithms/test_contract_imports.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/contracts app/algorithms/runtime_packages app/algorithms/_algo_template tests/test_algorithms/test_contract_imports.py
git commit -m "refactor: decouple plugin packages from platform internal imports"
```

### Task 5: 移除算法包内的自动注册假设

**Files:**
- Modify: `app/services/algorithm_catalog_service.py`
- Modify: `app/algorithms/registry.py`
- Test: `tests/test_algorithms/test_registry_behavior.py`

**Step 1: Write the failing test**

```python
from app.algorithms.registry import AlgorithmRegistry
from app.algorithms.runtime_packages.algo_missing_value.entry import MissingValueAlgorithm


def test_registry_requires_explicit_platform_registration():
    AlgorithmRegistry.clear()
    assert not AlgorithmRegistry.contains("missing_value", "1.0.0")
    AlgorithmRegistry.register(MissingValueAlgorithm)
    assert AlgorithmRegistry.contains("missing_value", "1.0.0")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_algorithms/test_registry_behavior.py::test_registry_requires_explicit_platform_registration -v`

Expected: FAIL if runtime packages still rely on import-side registration.

**Step 3: Write minimal implementation**

Remove any `AlgorithmRegistry.register(...)` calls from simulated algorithm package contents and keep registration only in platform code.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_algorithms/test_registry_behavior.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/services/algorithm_catalog_service.py app/algorithms/registry.py tests/test_algorithms/test_registry_behavior.py
git commit -m "refactor: make algorithm registration platform-driven"
```

### Task 6: 为平台添加插件发现与显式注册逻辑

**Files:**
- Modify: `app/services/algorithm_loader.py`
- Create: `app/services/plugin_discovery.py`
- Modify: `app/services/algorithm_resolver.py`
- Test: `tests/test_services/test_plugin_discovery.py`

**Step 1: Write the failing test**

```python
from app.algorithms.registry import AlgorithmRegistry
from app.services.algorithm_loader import algorithm_loader


def test_loader_discovers_plugin_and_registers_it():
    AlgorithmRegistry.clear()
    loaded = algorithm_loader.ensure_loaded("missing_value", "1.0.0")
    assert loaded.algorithm_cls.get_meta().algo_code == "missing_value"
    assert AlgorithmRegistry.contains("missing_value", "1.0.0")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_plugin_discovery.py::test_loader_discovers_plugin_and_registers_it -v`

Expected: FAIL because the loader still depends on import side effects.

**Step 3: Write minimal implementation**

Implement a discovery adapter:

```python
class PluginDiscovery:
    def load_algorithm_class(self, artifact) -> type[BaseAlgorithm]:
        module = import_module("app.algorithms.runtime_packages.algo_missing_value.entry")
        return getattr(module, "MissingValueAlgorithm")
```

Then update the loader to:

```python
algorithm_cls = plugin_discovery.load_algorithm_class(artifact)
AlgorithmRegistry.register(algorithm_cls)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_plugin_discovery.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/services/algorithm_loader.py app/services/plugin_discovery.py tests/test_services/test_plugin_discovery.py
git commit -m "feat: add explicit plugin discovery and registration"
```

### Task 7: 为真实私有 PyPI 接入预留安装与 entry_points 适配层

**Files:**
- Create: `app/services/algorithm_installer.py`
- Modify: `app/services/algorithm_fetcher.py`
- Modify: `app/schemas/algorithm.py`
- Test: `tests/test_services/test_algorithm_installer.py`

**Step 1: Write the failing test**

```python
from app.services.algorithm_installer import AlgorithmInstaller


def test_installer_builds_no_deps_install_command():
    installer = AlgorithmInstaller()
    cmd = installer.build_install_command("cached/example.whl", "runtime/site-packages")
    assert "--no-deps" in cmd
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_algorithm_installer.py::test_installer_builds_no_deps_install_command -v`

Expected: FAIL because the installer service does not exist yet.

**Step 3: Write minimal implementation**

```python
class AlgorithmInstaller:
    def build_install_command(self, wheel_path: str, target_dir: str) -> list[str]:
        return ["python", "-m", "pip", "install", wheel_path, "--target", target_dir, "--no-deps"]
```

Current phase only builds and documents the install command; actual execution can remain deferred.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_algorithm_installer.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/services/algorithm_installer.py app/services/algorithm_fetcher.py app/schemas/algorithm.py tests/test_services/test_algorithm_installer.py
git commit -m "feat: add no-deps installer adapter for plugin packages"
```

### Task 8: 补齐目录解析并纳入 `outliers`

**Files:**
- Modify: `app/services/algorithm_catalog_service.py`
- Test: `tests/test_services/test_algorithm_catalog_service.py`

**Step 1: Write the failing test**

```python
from app.services.algorithm_catalog_service import algorithm_catalog_service


def test_catalog_contains_outliers_package():
    entry = algorithm_catalog_service.get_catalog_entry("outliers", "1.0.0")
    assert entry.package_name == "algo-outliers"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_algorithm_catalog_service.py::test_catalog_contains_outliers_package -v`

Expected: FAIL because `outliers` is not present in the catalog yet.

**Step 3: Write minimal implementation**

Add the `outliers` entry into the in-memory catalog so that the runtime package is reachable from the execution chain.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_algorithm_catalog_service.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/services/algorithm_catalog_service.py tests/test_services/test_algorithm_catalog_service.py
git commit -m "feat: register outliers package in algorithm catalog"
```

### Task 9: 串通执行链路并补文档

**Files:**
- Modify: `app/engine/tasks.py`
- Modify: `app/engine/orchestrator.py`
- Modify: `app/services/execution_service.py`
- Modify: `docs/plans/2026-03-09-algorithm-platform-architecture-design.md`
- Test: `tests/test_engine/test_plugin_execution_flow.py`

**Step 1: Write the failing test**

```python
from app.algorithms.registry import AlgorithmRegistry
from app.schemas.flow_dsl import FlowDSL, FlowNode
from app.services.execution_service import execution_service


def test_execution_flow_uses_platform_registration_chain():
    AlgorithmRegistry.clear()
    flow = FlowDSL(nodes=[
        FlowNode(
            node_id="n1",
            algo_code="missing_value",
            algo_version="1.0.0",
            params={"fill_value": 99},
            inputs={"dataset": [1, None]},
        )
    ])
    result = execution_service.submit_execution(flow)
    assert result.status == "SUCCEEDED"
    assert result.node_results[0].source in {"downloaded", "cache", "registry"}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_engine/test_plugin_execution_flow.py::test_execution_flow_uses_platform_registration_chain -v`

Expected: FAIL until the loader and runtime packages are fully wired.

**Step 3: Write minimal implementation**

Update execution flow to call the new discovery/register path and update the main architecture doc to explain:

1. 标准 wheel
2. `entry_points`
3. 平台显式注册
4. `--no-deps` 安装策略

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_engine/test_plugin_execution_flow.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add app/engine app/services/execution_service.py docs/plans/2026-03-09-algorithm-platform-architecture-design.md tests/test_engine/test_plugin_execution_flow.py
git commit -m "feat: wire execution flow to plugin registration chain"
```

### Task 10: 清理运行产物并补忽略规则

**Files:**
- Modify: `.gitignore`
- Delete: `app/algorithms/runtime_packages/__pycache__/`
- Delete: `app/algorithms/_algo_template/tests/__pycache__/`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_runtime_package_tree_has_no_pycache_dirs():
    assert not Path("app/algorithms/runtime_packages/__pycache__").exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_algorithms/test_runtime_artifact_cleanup.py::test_runtime_package_tree_has_no_pycache_dirs -v`

Expected: FAIL because cached bytecode directories currently exist.

**Step 3: Write minimal implementation**

Delete generated `__pycache__` directories and add ignore rules:

```gitignore
__pycache__/
*.pyc
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_algorithms/test_runtime_artifact_cleanup.py -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .gitignore tests/test_algorithms/test_runtime_artifact_cleanup.py
git commit -m "chore: remove runtime cache artifacts from source tree"
```

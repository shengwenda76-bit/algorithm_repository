# Python Algorithm Library Platform Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a first-phase Python algorithm library platform that standardizes algorithm packages, publishes them to private PyPI, registers algorithm metadata, exposes H4-facing catalog APIs, and supports validation and debug execution.

**Architecture:** Implement the first phase as one Python monorepo with clear module boundaries: `sdk`, `algorithms`, `services/library_platform`, and `tools`. Keep registry, catalog, and debug execution as modules inside one backend project so the platform stays simple while matching the approved一期设计.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy, Alembic, PostgreSQL, pytest

---

### Task 1: Initialize repository structure

**Files:**
- Create: `README.md`
- Create: `sdk/algorithm_sdk/__init__.py`
- Create: `algorithms/.gitkeep`
- Create: `services/library_platform/__init__.py`
- Create: `services/library_platform/registry/__init__.py`
- Create: `services/library_platform/catalog/__init__.py`
- Create: `services/library_platform/debug/__init__.py`
- Create: `tools/.gitkeep`
- Modify: `pytest.ini`
- Test: `tests/test_repo_layout.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_repo_layout_exists():
    assert Path("sdk/algorithm_sdk").is_dir()
    assert Path("algorithms").is_dir()
    assert Path("services/library_platform/registry").is_dir()
    assert Path("services/library_platform/catalog").is_dir()
    assert Path("services/library_platform/debug").is_dir()
    assert Path("tools").is_dir()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_repo_layout.py -v`
Expected: FAIL because the library platform directories do not exist.

**Step 3: Write minimal implementation**

```python
# sdk/algorithm_sdk/__init__.py
"""Shared SDK for Python algorithm packages."""
```

```ini
# pytest.ini
[pytest]
testpaths = tests
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_repo_layout.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md pytest.ini sdk algorithms services tools tests/test_repo_layout.py
git commit -m "chore: initialize python algorithm library platform layout"
```

### Task 2: Create SDK core contract

**Files:**
- Create: `sdk/algorithm_sdk/base.py`
- Create: `sdk/algorithm_sdk/meta.py`
- Create: `sdk/algorithm_sdk/contracts.py`
- Create: `tests/sdk/test_algorithm_contracts.py`

**Step 1: Write the failing test**

```python
from algorithm_sdk.base import BaseAlgorithm
from algorithm_sdk.meta import AlgorithmMeta


def test_algorithm_subclass_exposes_meta():
    class DemoAlgorithm(BaseAlgorithm):
        meta = AlgorithmMeta(code="demo", name="Demo", version="1.0.0")

        def execute(self, inputs, params):
            return {"ok": True}

    assert DemoAlgorithm.meta.code == "demo"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/sdk/test_algorithm_contracts.py -v`
Expected: FAIL with import or attribute errors.

**Step 3: Write minimal implementation**

```python
from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    meta = None

    @abstractmethod
    def execute(self, inputs, params):
        raise NotImplementedError
```

```python
from pydantic import BaseModel


class AlgorithmMeta(BaseModel):
    code: str
    name: str
    version: str
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/sdk/test_algorithm_contracts.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add sdk/algorithm_sdk tests/sdk/test_algorithm_contracts.py
git commit -m "feat: add sdk core algorithm contracts"
```

### Task 3: Add metadata validator and package validator

**Files:**
- Create: `sdk/algorithm_sdk/validators.py`
- Create: `tools/validate_package.py`
- Create: `tests/sdk/test_package_validator.py`

**Step 1: Write the failing test**

```python
from algorithm_sdk.validators import validate_algorithm_meta


def test_validate_algorithm_meta_requires_entrypoint():
    payload = {"code": "demo", "name": "Demo", "version": "1.0.0"}
    errors = validate_algorithm_meta(payload)
    assert "entrypoint" in errors
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/sdk/test_package_validator.py -v`
Expected: FAIL because the validator is missing.

**Step 3: Write minimal implementation**

```python
def validate_algorithm_meta(payload):
    errors = []
    if "entrypoint" not in payload:
        errors.append("entrypoint")
    return errors
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/sdk/test_package_validator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add sdk/algorithm_sdk/validators.py tools/validate_package.py tests/sdk/test_package_validator.py
git commit -m "feat: add algorithm metadata validator"
```

### Task 4: Create sample algorithm package template

**Files:**
- Create: `algorithms/algo_missing_value/pyproject.toml`
- Create: `algorithms/algo_missing_value/algo_missing_value/__init__.py`
- Create: `algorithms/algo_missing_value/algo_missing_value/entry.py`
- Create: `algorithms/algo_missing_value/algo_missing_value/meta.py`
- Create: `tests/algorithms/test_missing_value_algorithm.py`

**Step 1: Write the failing test**

```python
from algo_missing_value.entry import MissingValueAlgorithm


def test_missing_value_algorithm_replaces_none():
    result = MissingValueAlgorithm().execute({"dataset": [1, None]}, {"fill_value": 0})
    assert result["dataset"] == [1, 0]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/algorithms/test_missing_value_algorithm.py -v`
Expected: FAIL because the algorithm package is not implemented.

**Step 3: Write minimal implementation**

```python
from algorithm_sdk.base import BaseAlgorithm
from .meta import ALGORITHM_META


class MissingValueAlgorithm(BaseAlgorithm):
    meta = ALGORITHM_META

    def execute(self, inputs, params):
        fill_value = params.get("fill_value", 0)
        return {
            "dataset": [fill_value if item is None else item for item in inputs["dataset"]]
        }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/algorithms/test_missing_value_algorithm.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add algorithms/algo_missing_value tests/algorithms/test_missing_value_algorithm.py
git commit -m "feat: add sample algorithm package"
```

### Task 5: Define library platform domain models

**Files:**
- Create: `services/library_platform/models.py`
- Create: `services/library_platform/schemas.py`
- Create: `tests/platform/test_algorithm_models.py`

**Step 1: Write the failing test**

```python
from services.library_platform.models import AlgorithmDefinition, PackageArtifact


def test_algorithm_definition_and_package_artifact_share_code_and_version():
    definition = AlgorithmDefinition(code="missing_value", name="Missing Value", version="1.0.0")
    artifact = PackageArtifact(code="missing_value", version="1.0.0", package_name="algo-missing-value")
    assert definition.code == artifact.code
    assert definition.version == artifact.version
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/platform/test_algorithm_models.py -v`
Expected: FAIL because the models do not exist.

**Step 3: Write minimal implementation**

```python
from pydantic import BaseModel


class AlgorithmDefinition(BaseModel):
    code: str
    name: str
    version: str


class PackageArtifact(BaseModel):
    code: str
    version: str
    package_name: str
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/platform/test_algorithm_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform tests/platform/test_algorithm_models.py
git commit -m "feat: add library platform core models"
```

### Task 6: Add register and validate APIs

**Files:**
- Create: `services/library_platform/app.py`
- Create: `services/library_platform/registry/routes.py`
- Create: `tests/platform/test_registry_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from services.library_platform.app import app


def test_register_algorithm_returns_201():
    client = TestClient(app)
    payload = {"code": "missing_value", "name": "Missing Value", "version": "1.0.0"}
    response = client.post("/algorithms/register", json=payload)
    assert response.status_code == 201
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/platform/test_registry_api.py -v`
Expected: FAIL because the routes are missing.

**Step 3: Write minimal implementation**

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/algorithms/register", status_code=status.HTTP_201_CREATED)
def register_algorithm(payload: dict):
    return payload


@app.post("/algorithms/validate")
def validate_algorithm(payload: dict):
    return {"valid": True, "errors": []}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/platform/test_registry_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform tests/platform/test_registry_api.py
git commit -m "feat: add algorithm register and validate apis"
```

### Task 7: Add catalog query APIs

**Files:**
- Create: `services/library_platform/catalog/routes.py`
- Create: `tests/platform/test_catalog_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from services.library_platform.app import app


def test_get_algorithms_returns_200():
    client = TestClient(app)
    response = client.get("/algorithms")
    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/platform/test_catalog_api.py -v`
Expected: FAIL because the catalog routes are missing.

**Step 3: Write minimal implementation**

```python
@app.get("/algorithms")
def list_algorithms():
    return {"items": []}


@app.get("/algorithms/{code}")
def get_algorithm(code: str):
    return {"code": code}


@app.get("/algorithms/{code}/versions")
def list_versions(code: str):
    return {"code": code, "items": []}


@app.get("/algorithms/{code}/versions/{version}")
def get_version(code: str, version: str):
    return {"code": code, "version": version}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/platform/test_catalog_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform tests/platform/test_catalog_api.py
git commit -m "feat: add algorithm catalog query apis"
```

### Task 8: Add debug execute API

**Files:**
- Create: `services/library_platform/debug/routes.py`
- Create: `tests/platform/test_debug_execute_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from services.library_platform.app import app


def test_execute_debug_api_returns_200():
    client = TestClient(app)
    response = client.post("/algorithms/missing_value/execute", json={"inputs": {}, "params": {}})
    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/platform/test_debug_execute_api.py -v`
Expected: FAIL because the debug execute route is missing.

**Step 3: Write minimal implementation**

```python
@app.post("/algorithms/{code}/execute")
def execute_algorithm(code: str, payload: dict):
    return {"code": code, "result": {}, "message": "debug only"}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/platform/test_debug_execute_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform tests/platform/test_debug_execute_api.py
git commit -m "feat: add debug execute api"
```

### Task 9: Add persistence and migrations

**Files:**
- Create: `services/library_platform/db.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/0001_create_algorithm_library_tables.py`
- Create: `tests/integration/test_schema_bootstrap.py`

**Step 1: Write the failing test**

```python
from services.library_platform.db import metadata


def test_metadata_contains_algorithm_tables():
    assert "algorithms" in metadata.tables
    assert "algorithm_artifacts" in metadata.tables
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_schema_bootstrap.py -v`
Expected: FAIL because database metadata is not defined.

**Step 3: Write minimal implementation**

```python
from sqlalchemy import Column, MetaData, String, Table

metadata = MetaData()

Table("algorithms", metadata, Column("code", String, primary_key=True))
Table("algorithm_artifacts", metadata, Column("id", String, primary_key=True))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_schema_bootstrap.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform alembic.ini alembic tests/integration/test_schema_bootstrap.py
git commit -m "feat: add algorithm library platform persistence baseline"
```

### Task 10: Add publish workflow CLI

**Files:**
- Create: `tools/publish_cli.py`
- Create: `tests/tools/test_publish_cli.py`

**Step 1: Write the failing test**

```python
from tools.publish_cli import build_register_payload


def test_build_register_payload_contains_package_hash():
    payload = build_register_payload(
        code="missing_value",
        version="1.0.0",
        sha256="abc123",
    )
    assert payload["artifact"]["sha256"] == "abc123"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/tools/test_publish_cli.py -v`
Expected: FAIL because the helper does not exist.

**Step 3: Write minimal implementation**

```python
def build_register_payload(code, version, sha256):
    return {
        "code": code,
        "version": version,
        "artifact": {"sha256": sha256},
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/tools/test_publish_cli.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tools/publish_cli.py tests/tools/test_publish_cli.py
git commit -m "feat: add publish cli payload builder"
```

### Task 11: Add documentation and onboarding

**Files:**
- Modify: `README.md`
- Create: `docs/architecture/python-algorithm-library-platform.md`
- Create: `docs/algorithm-package-spec.md`
- Test: `tests/docs/test_readme_mentions_platform_modules.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_readme_mentions_registry_catalog_and_debug():
    content = Path("README.md").read_text(encoding="utf-8")
    assert "registry" in content
    assert "catalog" in content
    assert "debug" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/docs/test_readme_mentions_platform_modules.py -v`
Expected: FAIL because README is empty.

**Step 3: Write minimal implementation**

```markdown
# Python Algorithm Library Platform

This repository contains the SDK, algorithm packages, registry module, catalog module, and debug module.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/docs/test_readme_mentions_platform_modules.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md docs/architecture/python-algorithm-library-platform.md docs/algorithm-package-spec.md tests/docs/test_readme_mentions_platform_modules.py
git commit -m "docs: add algorithm library platform onboarding docs"
```

### Task 12: Run final verification

**Files:**
- Modify: `docs/plans/2026-03-17-python-operator-asset-platform-implementation.md`

**Step 1: Run focused test suites**

Run: `pytest tests -v`
Expected: PASS for repository, SDK, algorithm package, API, persistence, tool, and docs tests.

**Step 2: Run service smoke checks**

Run: `python -m py_compile services/library_platform/app.py services/library_platform/models.py services/library_platform/db.py`
Expected: PASS with no syntax errors.

**Step 3: Update the plan with actual deviations**

```markdown
- If actual file paths differ, record the final paths here before handing off.
- If extra shared modules were needed, list them here.
```

**Step 4: Create the final commit**

```bash
git add .
git commit -m "feat: deliver phase-one python algorithm library platform baseline"
```

# Python Operator Asset Platform Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a first-phase Python operator asset platform that standardizes algorithm packages, registers metadata, exposes a catalog, and provides an engine resolve API backed by private PyPI artifacts.

**Architecture:** Implement the platform as one Python monorepo with clear module boundaries: `sdk`, `algorithms`, `services`, and `tools`. Keep registry, catalog, and resolve capabilities in separate service modules with shared domain models so they can be deployed together first and split later.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy, Alembic, PostgreSQL, pytest

---

### Task 1: Initialize repository structure

**Files:**
- Create: `README.md`
- Create: `sdk/algorithm_sdk/__init__.py`
- Create: `algorithms/.gitkeep`
- Create: `services/.gitkeep`
- Create: `tools/.gitkeep`
- Modify: `pytest.ini`
- Test: `tests/test_repo_layout.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_repo_layout_exists():
    assert Path("sdk/algorithm_sdk").is_dir()
    assert Path("algorithms").is_dir()
    assert Path("services").is_dir()
    assert Path("tools").is_dir()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_repo_layout.py -v`
Expected: FAIL because directories and placeholder files do not exist.

**Step 3: Write minimal implementation**

```python
# sdk/algorithm_sdk/__init__.py
"""Shared SDK for Python operator packages."""
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
git commit -m "chore: initialize operator platform repository layout"
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
        meta = AlgorithmMeta(algo_code="demo", name="Demo", version="1.0.0")

        def execute(self, inputs, params):
            return {"ok": True}

    assert DemoAlgorithm.meta.algo_code == "demo"
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
    algo_code: str
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

### Task 3: Add package metadata and entry-point validator

**Files:**
- Create: `sdk/algorithm_sdk/validators.py`
- Create: `tools/validate_package.py`
- Create: `tests/sdk/test_package_validator.py`

**Step 1: Write the failing test**

```python
from algorithm_sdk.validators import validate_runtime_contract


def test_validate_runtime_contract_requires_entry_point():
    payload = {"entry_point_group": "algorithm_platform.algorithms"}
    errors = validate_runtime_contract(payload)
    assert "entry_point_target" in errors
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/sdk/test_package_validator.py -v`
Expected: FAIL because validator is missing.

**Step 3: Write minimal implementation**

```python
def validate_runtime_contract(payload):
    errors = []
    if "entry_point_target" not in payload:
        errors.append("entry_point_target")
    return errors
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/sdk/test_package_validator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add sdk/algorithm_sdk/validators.py tools/validate_package.py tests/sdk/test_package_validator.py
git commit -m "feat: add runtime contract validator"
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
Expected: FAIL because package is not implemented.

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
git commit -m "feat: add sample operator package"
```

### Task 5: Scaffold registry service domain models

**Files:**
- Create: `services/registry_service/app/models.py`
- Create: `services/registry_service/app/schemas.py`
- Create: `services/registry_service/tests/test_version_state_machine.py`

**Step 1: Write the failing test**

```python
from services.registry_service.app.models import AlgorithmVersion


def test_published_is_only_default_executable_state():
    version = AlgorithmVersion(version="1.0.0", lifecycle_state="Published")
    assert version.is_resolvable() is True
```

**Step 2: Run test to verify it fails**

Run: `pytest services/registry_service/tests/test_version_state_machine.py -v`
Expected: FAIL because model does not exist.

**Step 3: Write minimal implementation**

```python
from pydantic import BaseModel


class AlgorithmVersion(BaseModel):
    version: str
    lifecycle_state: str

    def is_resolvable(self) -> bool:
        return self.lifecycle_state == "Published"
```

**Step 4: Run test to verify it passes**

Run: `pytest services/registry_service/tests/test_version_state_machine.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/registry_service
git commit -m "feat: add registry domain models"
```

### Task 6: Add registry write API

**Files:**
- Create: `services/registry_service/app/main.py`
- Create: `services/registry_service/app/routes/algorithms.py`
- Create: `services/registry_service/tests/test_register_version_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from services.registry_service.app.main import app


def test_register_version_returns_201():
    client = TestClient(app)
    payload = {"algo_code": "missing_value", "version": "1.0.0"}
    response = client.post("/algorithms/missing_value/versions", json=payload)
    assert response.status_code == 201
```

**Step 2: Run test to verify it fails**

Run: `pytest services/registry_service/tests/test_register_version_api.py -v`
Expected: FAIL because API route is missing.

**Step 3: Write minimal implementation**

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/algorithms/{algo_code}/versions", status_code=status.HTTP_201_CREATED)
def register_version(algo_code: str, payload: dict):
    return {"algo_code": algo_code, "version": payload["version"]}
```

**Step 4: Run test to verify it passes**

Run: `pytest services/registry_service/tests/test_register_version_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/registry_service
git commit -m "feat: add registry version registration api"
```

### Task 7: Add catalog read API

**Files:**
- Create: `services/catalog_service/app/main.py`
- Create: `services/catalog_service/app/routes/catalog.py`
- Create: `services/catalog_service/tests/test_catalog_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from services.catalog_service.app.main import app


def test_catalog_lists_published_algorithms():
    client = TestClient(app)
    response = client.get("/catalog/algorithms")
    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest services/catalog_service/tests/test_catalog_api.py -v`
Expected: FAIL because API route is missing.

**Step 3: Write minimal implementation**

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/catalog/algorithms")
def list_algorithms():
    return {"items": []}
```

**Step 4: Run test to verify it passes**

Run: `pytest services/catalog_service/tests/test_catalog_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/catalog_service
git commit -m "feat: add catalog read api"
```

### Task 8: Add engine resolve API

**Files:**
- Create: `services/resolve_service/app/main.py`
- Create: `services/resolve_service/app/routes/resolve.py`
- Create: `services/resolve_service/tests/test_resolve_api.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from services.resolve_service.app.main import app


def test_resolve_returns_package_coordinates():
    client = TestClient(app)
    payload = {"algo_code": "missing_value", "engine_type": "ekuiper"}
    response = client.post("/engine/resolve", json=payload)
    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest services/resolve_service/tests/test_resolve_api.py -v`
Expected: FAIL because API route is missing.

**Step 3: Write minimal implementation**

```python
from fastapi import FastAPI

app = FastAPI()


@app.post("/engine/resolve")
def resolve_algorithm(payload: dict):
    return {
        "algo_code": payload["algo_code"],
        "package_name": "algo-missing-value",
        "package_version": "1.0.0",
        "entry_point_target": "algo_missing_value.entry:MissingValueAlgorithm",
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest services/resolve_service/tests/test_resolve_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/resolve_service
git commit -m "feat: add engine resolve api"
```

### Task 9: Add persistence and migrations

**Files:**
- Create: `services/shared/db.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/0001_create_operator_tables.py`
- Create: `tests/integration/test_schema_bootstrap.py`

**Step 1: Write the failing test**

```python
from services.shared.db import metadata


def test_metadata_contains_algorithm_tables():
    assert "algorithms" in metadata.tables
    assert "algorithm_versions" in metadata.tables
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_schema_bootstrap.py -v`
Expected: FAIL because database metadata is not defined.

**Step 3: Write minimal implementation**

```python
from sqlalchemy import MetaData, Table, Column, String

metadata = MetaData()

Table("algorithms", metadata, Column("algo_code", String, primary_key=True))
Table("algorithm_versions", metadata, Column("id", String, primary_key=True))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_schema_bootstrap.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/shared alembic.ini alembic tests/integration/test_schema_bootstrap.py
git commit -m "feat: add operator platform persistence baseline"
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
        algo_code="missing_value",
        version="1.0.0",
        sha256="abc123",
    )
    assert payload["artifact"]["sha256"] == "abc123"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/tools/test_publish_cli.py -v`
Expected: FAIL because helper does not exist.

**Step 3: Write minimal implementation**

```python
def build_register_payload(algo_code, version, sha256):
    return {
        "algo_code": algo_code,
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
- Create: `docs/architecture/python-operator-asset-platform.md`
- Create: `docs/operator-package-spec.md`
- Test: `tests/docs/test_readme_mentions_services.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_readme_mentions_registry_catalog_and_resolve():
    content = Path("README.md").read_text(encoding="utf-8")
    assert "registry" in content
    assert "catalog" in content
    assert "resolve" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/docs/test_readme_mentions_services.py -v`
Expected: FAIL because README is empty.

**Step 3: Write minimal implementation**

```markdown
# Python Operator Asset Platform

This repository contains the SDK, operator packages, registry service, catalog service, and resolve service.
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/docs/test_readme_mentions_services.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md docs/architecture/python-operator-asset-platform.md docs/operator-package-spec.md tests/docs/test_readme_mentions_services.py
git commit -m "docs: add operator platform onboarding docs"
```

### Task 12: Run final verification

**Files:**
- Modify: `docs/plans/2026-03-17-python-operator-asset-platform-implementation.md`

**Step 1: Run focused test suites**

Run: `pytest tests services -v`
Expected: PASS for repository, SDK, algorithm package, API, persistence, tool, and docs tests.

**Step 2: Run service smoke checks**

Run: `python -m py_compile services/registry_service/app/main.py services/catalog_service/app/main.py services/resolve_service/app/main.py`
Expected: PASS with no syntax errors.

**Step 3: Update the plan with actual deviations**

```markdown
- If actual file paths differ, record the final paths here before handing off.
- If extra migrations or shared modules were needed, list them here.
```

**Step 4: Create the final commit**

```bash
git add .
git commit -m "feat: deliver phase-one python operator asset platform baseline"
```

# Registry Repository Persistence Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a replaceable persistence layer for the registry module by introducing a repository protocol, a sqlite-backed repository, and application-level repository selection without changing the external API behavior.

**Architecture:** Keep `RegistryService` dependent on a stable repository interface only. Preserve the current `InMemoryRegistryRepository`, add `SqliteRegistryRepository`, and move database connection/bootstrap concerns into `services/library_platform/db.py`. Application startup decides which repository to use based on configuration.

**Tech Stack:** Python 3.12, standard library `sqlite3`, FastAPI, Pydantic v2, unittest

---

### Task 1: Add failing tests for repository selection and sqlite persistence

**Files:**
- Modify: `tests/platform/test_app_entry.py`
- Create: `tests/platform/test_repository_factory.py`
- Create: `tests/integration/test_sqlite_registry_repository.py`

**Step 1: Write the failing tests**

```python
def test_create_registry_repository_defaults_to_in_memory():
    repository = create_registry_repository(database_url=None)
    assert repository.__class__.__name__ == "InMemoryRegistryRepository"
```

```python
def test_create_registry_repository_uses_sqlite_for_sqlite_url():
    repository = create_registry_repository(database_url="sqlite:///tmp/test.db")
    assert repository.__class__.__name__ == "SqliteRegistryRepository"
```

```python
def test_sqlite_repository_marks_latest_version():
    repository = SqliteRegistryRepository(database_url="sqlite:///:memory:")
    repository.save_registration(definition, artifact)
    repository.save_registration(definition_v2, artifact_v2)
    versions = repository.list_versions("missing_value")
    assert {item["version"]: item["is_latest"] for item in versions} == {
        "0.1.0": False,
        "0.2.0": True,
    }
```

**Step 2: Run tests to verify they fail**

Run:
- `python -m unittest discover -s tests/platform -p "test_repository_factory.py" -v`
- `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`

Expected:
- FAIL because the repository factory and sqlite repository do not exist yet.

**Step 3: Write minimal implementation**

- Add repository factory placeholders in `services/library_platform/app.py`
- Add empty sqlite repository skeleton in `services/library_platform/registry/repository.py`

**Step 4: Run tests to verify progress**

Run the same commands above and confirm failures move from import errors to behavior failures.

**Step 5: Commit**

```bash
git add tests/platform/test_app_entry.py tests/platform/test_repository_factory.py tests/integration/test_sqlite_registry_repository.py services/library_platform/app.py services/library_platform/registry/repository.py
git commit -m "test: add failing tests for repository persistence selection"
```

### Task 2: Introduce a stable repository protocol

**Files:**
- Modify: `services/library_platform/registry/repository.py`
- Modify: `services/library_platform/registry/service.py`
- Test: `tests/integration/test_sqlite_registry_repository.py`

**Step 1: Write the failing test**

```python
def test_registry_service_uses_repository_protocol_methods():
    repository = FakeRepository()
    service = RegistryService(repository=repository)
    service.list_algorithms()
    assert repository.list_algorithms_called is True
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`
Expected: FAIL because protocol usage is not yet explicit enough for the fake implementation.

**Step 3: Write minimal implementation**

- Add `RegistryRepository` protocol or abstract base
- Make `InMemoryRegistryRepository` implement it
- Type `RegistryService` against the protocol rather than the concrete in-memory class

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`
Expected: PASS for the protocol-oriented behavior.

**Step 5: Commit**

```bash
git add services/library_platform/registry/repository.py services/library_platform/registry/service.py tests/integration/test_sqlite_registry_repository.py
git commit -m "refactor: introduce registry repository protocol"
```

### Task 3: Add sqlite connection and bootstrap helpers

**Files:**
- Modify: `services/library_platform/db.py`
- Create: `tests/integration/test_sqlite_bootstrap.py`

**Step 1: Write the failing test**

```python
def test_bootstrap_sqlite_creates_expected_tables():
    connection = connect_sqlite(":memory:")
    bootstrap_sqlite_schema(connection)
    table_names = fetch_table_names(connection)
    assert "algorithms" in table_names
    assert "algorithm_versions" in table_names
    assert "algorithm_artifacts" in table_names
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_bootstrap.py" -v`
Expected: FAIL because sqlite helper functions do not exist yet.

**Step 3: Write minimal implementation**

- Add `connect_sqlite(...)`
- Add `bootstrap_sqlite_schema(...)`
- Add database URL parsing helper for `sqlite:///...`
- Create the three tables with current stable column names

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_bootstrap.py" -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform/db.py tests/integration/test_sqlite_bootstrap.py
git commit -m "feat: add sqlite bootstrap helpers"
```

### Task 4: Implement sqlite-backed repository registration flow

**Files:**
- Modify: `services/library_platform/registry/repository.py`
- Test: `tests/integration/test_sqlite_registry_repository.py`

**Step 1: Write the failing test**

```python
def test_sqlite_repository_save_registration_inserts_three_tables():
    repository.save_registration(definition, artifact)
    assert repository.get_algorithm("missing_value")["code"] == "missing_value"
    assert repository.get_version_detail("missing_value", "0.1.0")["artifact"]["package_name"] == "algo-missing-value"
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`
Expected: FAIL because sqlite repository save logic is incomplete.

**Step 3: Write minimal implementation**

- Implement single-transaction registration flow:
  - upsert `algorithms`
  - insert `algorithm_versions`
  - insert `algorithm_artifacts`
  - clear previous `is_latest`
  - mark current version as latest

**Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform/registry/repository.py tests/integration/test_sqlite_registry_repository.py
git commit -m "feat: add sqlite registry repository save flow"
```

### Task 5: Implement sqlite-backed query methods

**Files:**
- Modify: `services/library_platform/registry/repository.py`
- Test: `tests/integration/test_sqlite_registry_repository.py`

**Step 1: Write the failing tests**

```python
def test_sqlite_repository_list_algorithms_returns_latest_version_summary():
    items = repository.list_algorithms()
    assert items[0]["version"] == "0.2.0"
```

```python
def test_sqlite_repository_get_version_detail_returns_joined_view():
    detail = repository.get_version_detail("missing_value", "0.1.0")
    assert detail["definition"]["category"] == "data_cleaning"
    assert detail["artifact"]["package_name"] == "algo-missing-value"
```

```python
def test_sqlite_repository_get_execution_target_defaults_to_latest_version():
    target = repository.get_execution_target("missing_value")
    assert target["version"] == "0.2.0"
```

**Step 2: Run tests to verify they fail**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`
Expected: FAIL because sqlite query methods are incomplete.

**Step 3: Write minimal implementation**

- Implement:
  - `list_algorithms`
  - `get_algorithm`
  - `list_versions`
  - `get_version_detail`
  - `get_execution_target`
- Keep return structures aligned with the in-memory repository

**Step 4: Run tests to verify they pass**

Run: `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform/registry/repository.py tests/integration/test_sqlite_registry_repository.py
git commit -m "feat: add sqlite registry repository query methods"
```

### Task 6: Add application-level repository factory and wiring

**Files:**
- Modify: `services/library_platform/app.py`
- Modify: `tests/platform/test_app_entry.py`
- Test: `tests/platform/test_repository_factory.py`

**Step 1: Write the failing test**

```python
def test_create_fastapi_app_uses_repository_factory():
    app = create_fastapi_app(database_url="sqlite:///:memory:")
    assert app.state.registry_service is not None
```

**Step 2: Run test to verify it fails**

Run:
- `python -m unittest discover -s tests/platform -p "test_app_entry.py" -v`
- `python -m unittest discover -s tests/platform -p "test_repository_factory.py" -v`

Expected: FAIL because app creation cannot yet choose repository backend.

**Step 3: Write minimal implementation**

- Add `create_registry_repository(...)`
- Allow `create_fastapi_app(...)` to accept `database_url`
- Default to in-memory when `database_url` is missing
- Use sqlite repository when `database_url` starts with `sqlite:///`

**Step 4: Run tests to verify they pass**

Run the same commands above.
Expected: PASS

**Step 5: Commit**

```bash
git add services/library_platform/app.py tests/platform/test_app_entry.py tests/platform/test_repository_factory.py
git commit -m "feat: add repository backend selection in app"
```

### Task 7: Run regression verification

**Files:**
- Verify only

**Step 1: Run repository and integration tests**

Run:
- `python -m unittest discover -s tests/integration -p "test_sqlite_registry_repository.py" -v`
- `python -m unittest discover -s tests/integration -p "test_sqlite_bootstrap.py" -v`
- `python -m unittest discover -s tests/integration -p "test_schema_bootstrap.py" -v`

Expected: PASS

**Step 2: Run platform API tests**

Run:
- `python -m unittest discover -s tests/platform -p "test_registry_api.py" -v`
- `python -m unittest discover -s tests/platform -p "test_catalog_api.py" -v`
- `python -m unittest discover -s tests/platform -p "test_debug_execute_api.py" -v`
- `python -m unittest discover -s tests/platform -p "test_schemas.py" -v`
- `python -m unittest discover -s tests/platform -p "test_app_entry.py" -v`
- `python -m unittest discover -s tests/platform -p "test_repository_factory.py" -v`

Expected: PASS

**Step 3: Run SDK sanity checks**

Run:
- `python -m unittest discover -s tests/sdk -p "test_algorithm_contracts.py" -v`
- `python -m unittest discover -s tests/sdk -p "test_package_validator.py" -v`
- `python -m unittest discover -s tests/algorithms -p "test_missing_value_algorithm.py" -v`

Expected: PASS

**Step 4: Run syntax verification**

Run:
- `python -m py_compile services/library_platform/app.py services/library_platform/db.py services/library_platform/registry/repository.py services/library_platform/registry/service.py`

Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "feat: add replaceable sqlite-backed registry persistence layer"
```

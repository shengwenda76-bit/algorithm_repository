# alg_tool Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a portable `alg_tool/` folder that can be copied into a new empty directory and used to scaffold and publish algorithm packages without depending on this repository's internal modules.

**Architecture:** `alg_tool` will be implemented as a self-contained Python tool bundle with CLI entry scripts, reusable helper functions, file templates, and a vendored minimal `algorithm_sdk`. Tests will exercise the tool in temporary directories so we verify portability rather than only local repository coupling.

**Tech Stack:** Python standard library, `pytest`, `build`, `twine`, vendored `algorithm_sdk` dataclasses and validators.

---

### Task 1: Add failing scaffold generation test

**Files:**
- Create: `tests/alg_tool/test_create_alg.py`

**Step 1: Write the failing test**

Create a test that runs the scaffold API in a temporary directory and asserts these files exist:

- `algorithms/algo_missing_value/pyproject.toml`
- `algorithms/algo_missing_value/README.md`
- `algorithms/algo_missing_value/algo_missing_value/entry.py`
- `algorithms/algo_missing_value/algo_missing_value/meta.py`
- `algorithms/algo_missing_value/algo_missing_value/schema.py`
- `algorithms/algo_missing_value/tests/test_algo_missing_value.py`

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/alg_tool/test_create_alg.py -q`
Expected: FAIL because `alg_tool.create_alg` and scaffold helpers do not exist yet.

**Step 3: Write minimal implementation**

Create `alg_tool/__init__.py`, `alg_tool/create_alg.py`, `alg_tool/common.py`, template files, and vendored SDK files needed to make the scaffold test pass.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/alg_tool/test_create_alg.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add alg_tool tests/alg_tool/test_create_alg.py
git commit -m "feat: add portable algorithm scaffold tool"
```

### Task 2: Add failing publish validation test

**Files:**
- Create: `tests/alg_tool/test_publish.py`

**Step 1: Write the failing test**

Create tests that:

- scaffold a temporary algorithm package
- load metadata through publish helpers
- verify register payload shape
- verify local validation returns version, entrypoint, and required file information

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: FAIL because `alg_tool.publish` helpers do not exist yet.

**Step 3: Write minimal implementation**

Implement:

- metadata loading
- entrypoint import checks
- pyproject parsing
- payload building
- SHA256 helper
- local validation report

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add alg_tool tests/alg_tool/test_publish.py
git commit -m "feat: add portable publish validation tool"
```

### Task 3: Add publish CLI end-to-end local build behavior

**Files:**
- Modify: `alg_tool/publish.py`
- Modify: `tests/alg_tool/test_publish.py`

**Step 1: Write the failing test**

Add a test that runs publish in local-only mode and asserts:

- tests command is executed
- build output is detected
- wheel hash is reported
- no upload or registration is attempted when environment variables are absent

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: FAIL because the local build workflow is incomplete.

**Step 3: Write minimal implementation**

Implement publish orchestration:

- run `pytest`
- run `python -m build`
- inspect `dist/`
- produce a status summary

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add alg_tool tests/alg_tool/test_publish.py
git commit -m "feat: add local build flow to portable publish tool"
```

### Task 4: Add tool documentation and verify portability

**Files:**
- Create: `alg_tool/README.md`
- Modify: `alg_tool/create_alg.py`
- Modify: `alg_tool/publish.py`
- Modify: `tests/alg_tool/test_create_alg.py`
- Modify: `tests/alg_tool/test_publish.py`

**Step 1: Write the failing test**

Add assertions that generated README content and tool README content mention:

- how to scaffold
- how to test locally
- how to publish
- required environment variables

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/alg_tool/test_create_alg.py tests/alg_tool/test_publish.py -q`
Expected: FAIL because documentation content is missing or incomplete.

**Step 3: Write minimal implementation**

Add README templates and CLI help text that explain portable usage.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/alg_tool/test_create_alg.py tests/alg_tool/test_publish.py -q`
Expected: PASS

**Step 5: Commit**

```bash
git add alg_tool tests/alg_tool
git commit -m "docs: document portable alg tool usage"
```

### Task 5: Run focused verification

**Files:**
- Verify only

**Step 1: Run focused tests**

Run: `python -m pytest tests/alg_tool -q`
Expected: PASS

**Step 2: Run adjacent regression tests**

Run: `python -m pytest tests/sdk/test_algorithm_contracts.py tests/tools/test_publish_cli.py -q`
Expected: PASS

**Step 3: Review resulting tree**

Confirm `alg_tool/` contains:

- CLI scripts
- templates
- vendored SDK
- README

**Step 4: Commit**

```bash
git add alg_tool docs/plans tests/alg_tool
git commit -m "feat: add portable alg tool bundle"
```

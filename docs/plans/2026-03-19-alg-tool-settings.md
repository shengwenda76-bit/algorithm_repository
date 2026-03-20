# alg_tool Settings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a portable `settings.py` configuration module to `alg_tool` and enforce configuration plus remote connectivity validation in `publish.py` before upload and registration.

**Architecture:** `alg_tool/settings.py` will define defaults and expose a small typed loader that merges defaults with environment overrides. `publish.py` will consume that runtime settings object, perform explicit configuration completeness checks, optionally probe remote endpoints, and then continue with local test/build/upload/register steps.

**Tech Stack:** Python 3 standard library, `urllib.request`, `unittest`, existing `alg_tool` helpers

---

### Task 1: Add failing tests for settings loading

**Files:**
- Modify: `tests/alg_tool/test_publish.py`
- Create: `alg_tool/settings.py`

**Step 1: Write the failing test**

Add tests that expect:

- `load_publish_settings()` returns default values from `alg_tool/settings.py`
- environment variables override `settings.py`

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: FAIL because `load_publish_settings` and `alg_tool.settings` do not exist yet.

**Step 3: Write minimal implementation**

Create `alg_tool/settings.py` and add a lightweight loader in `publish.py`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: PASS for the new settings-loading tests.

### Task 2: Add failing tests for configuration completeness validation

**Files:**
- Modify: `tests/alg_tool/test_publish.py`
- Modify: `alg_tool/publish.py`

**Step 1: Write the failing test**

Add tests that expect:

- upload configuration missing required fields raises `ValueError`
- registration configuration missing required fields raises `ValueError`

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: FAIL because validation does not yet enforce settings completeness.

**Step 3: Write minimal implementation**

Add explicit validation helpers in `publish.py` that inspect the resolved settings object before upload or register steps.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: PASS for completeness-validation tests.

### Task 3: Add failing tests for remote connectivity checks

**Files:**
- Modify: `tests/alg_tool/test_publish.py`
- Modify: `alg_tool/publish.py`

**Step 1: Write the failing test**

Add tests that expect:

- when remote checking is enabled, repository and platform probe functions are invoked
- unreachable endpoints raise a clear runtime error
- when remote checking is disabled, probing is skipped

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: FAIL because `publish.py` does not yet perform remote probing.

**Step 3: Write minimal implementation**

Add lightweight probe helpers around `urllib.request` with `HEAD` first and `GET` fallback, and call them conditionally from `publish_algorithm`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: PASS for connectivity tests.

### Task 4: Update documentation for portable settings usage

**Files:**
- Modify: `alg_tool/README.md`
- Modify: `docs/plans/2026-03-19-alg-tool-design.md`

**Step 1: Write the failing doc check**

No automated doc test required. Re-read existing README and design notes, then note the missing sections:

- `settings.py` first workflow
- environment overrides
- remote validation behavior

**Step 2: Write minimal documentation updates**

Update the README to show:

- where to edit `settings.py`
- what each setting does
- the validation order inside `publish.py`

Update the design note so it no longer implies environment variables are the only configuration path.

**Step 3: Verify documentation**

Manually read the updated sections and confirm they match implementation behavior.

### Task 5: Run final verification

**Files:**
- Modify: `tests/alg_tool/test_publish.py`
- Modify: `alg_tool/publish.py`
- Modify: `alg_tool/README.md`
- Create: `alg_tool/settings.py`

**Step 1: Run focused tests**

Run: `python -m pytest tests/alg_tool/test_publish.py -q`
Expected: PASS

**Step 2: Run broader regression tests**

Run: `python -m pytest tests/alg_tool -q tests/tools/test_publish_cli.py tests/sdk/test_algorithm_contracts.py -q`
Expected: PASS

**Step 3: Smoke-check CLI entrypoint**

Run: `python alg_tool/publish.py --help`
Expected: exit code 0 with usage text

**Step 4: Re-read changed files**

Confirm the implementation matches the design and README.

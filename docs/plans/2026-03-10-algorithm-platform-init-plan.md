# Algorithm Repository API & Celery Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Initialize the FastAPI gateway, Celery worker configuration, and the endpoint for retrieving algorithm schemas from the registry based on the new architecture design.

**Architecture:** Create a FastAPI application backend with routers to expose the `/schemas` and `/execute` endpoints. Configure the Celery application to connect to Redis as the broker/backend for asynchronous task execution.

**Tech Stack:** FastAPI, Celery, Redis, pytest, Pydantic.

---

### Task 1: Setup Core Configuration

**Files:**
- Create: `app/core/config.py`
- Create: `tests/core/test_config.py`

**Step 1: Write the failing test**

```python
# tests/core/test_config.py
import os
from app.core.config import settings

def test_settings_load_defaults():
    assert settings.PROJECT_NAME == "Algorithm Repository"
    assert "redis://" in settings.REDIS_URL
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/core/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'app.core.config'"

**Step 3: Write minimal implementation**

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Algorithm Repository"
    API_V1_STR: str = "/api/v1"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "localhost:9000"
    
settings = Settings()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/core/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/core/config.py tests/core/test_config.py
git commit -m "feat(core): add application settings"
```

### Task 2: Implement FastAPI App and Schema Endpoint

**Files:**
- Create: `app/api/main.py`
- Create: `tests/api/test_algorithms.py`

**Step 1: Write the failing test**

```python
# tests/api/test_algorithms.py
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_get_schemas():
    response = client.get("/api/v1/algorithms/schemas")
    assert response.status_code == 200
    data = response.json()
    assert "algorithms" in data
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/api/test_algorithms.py -v`
Expected: FAIL with "ModuleNotFoundError" or "404 Not Found"

**Step 3: Write minimal implementation**

```python
# app/api/main.py
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get(f"{settings.API_V1_STR}/algorithms/schemas")
def get_schemas():
    # TODO: integrate with app.algorithms.registry 
    return {"algorithms": []}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/api/test_algorithms.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/api/main.py tests/api/test_algorithms.py
git commit -m "feat(api): add algorithms schemas endpoint"
```

### Task 3: Initialize Celery App

**Files:**
- Create: `app/core/celery_app.py`
- Create: `tests/core/test_celery.py`

**Step 1: Write the failing test**

```python
# tests/core/test_celery.py
from app.core.celery_app import celery_app

def test_celery_configured():
    assert celery_app.conf.broker_url is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/core/test_celery.py -v`
Expected: FAIL 

**Step 3: Write minimal implementation**

```python
# app/core/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {"app.worker.tasks.*": "main-queue"}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/core/test_celery.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/core/celery_app.py tests/core/test_celery.py
git commit -m "feat(core): initialize celery app"
```

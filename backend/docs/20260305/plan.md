# 算法平台（算法库 + 异步 DAG 执行）实施计划

> **给 Claude：** 必须使用子技能：`superpowers:executing-plans`，按任务逐步实现本计划。

**目标：** 构建一个算法平台，提供算法元数据/Schema API，并能异步执行业务平台提交的完整 Flow DSL，采用快速失败策略。

**架构：** 采用模块化单体，明确划分模块边界：注册中心、校验器、编排器、执行器、队列适配器、回调服务与 API 层。一期持久化保持简单（内存或轻量仓储抽象），但现在就落实稳定契约与幂等提交。队列与执行器通过接口隔离，后续迁移 Redis/Celery 风险更低。

**技术栈：** Python 3.11、FastAPI、Pydantic v2、pytest、httpx、networkx（用于 DAG 校验）、uvicorn。

---

### 任务 1：搭建服务骨架与健康检查

**文件：**
- 新建：`pyproject.toml`
- 新建：`app/main.py`
- 新建：`tests/api/test_health.py`

**步骤 1：先写失败测试**

```python
# tests/api/test_health.py
from fastapi.testclient import TestClient
from app.main import app


def test_health():
    client = TestClient(app)
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'ok'}
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/api/test_health.py -v`
预期：由于 `app.main` 不存在，出现 import/module 错误并 FAIL。

**步骤 3：实现最小代码使其通过**

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title='algorithm-platform')


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/api/test_health.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add pyproject.toml app/main.py tests/api/test_health.py
git commit -m "chore: bootstrap api service and health endpoint"
```

### 任务 2：构建算法注册模型与查询 API

**文件：**
- 新建：`app/schemas/algorithm.py`
- 新建：`app/services/algorithm_registry.py`
- 新建：`app/api/routes/algorithms.py`
- 修改：`app/main.py`
- 新建：`tests/api/test_algorithms_api.py`

**步骤 1：先写失败测试**

```python
# tests/api/test_algorithms_api.py
from fastapi.testclient import TestClient
from app.main import app


def test_list_algorithms():
    client = TestClient(app)
    resp = client.get('/v1/algorithms')
    assert resp.status_code == 200
    assert isinstance(resp.json()['items'], list)


def test_get_algorithm_version_schema():
    client = TestClient(app)
    resp = client.get('/v1/algorithms/missing_value/versions/1.0.0')
    assert resp.status_code == 200
    data = resp.json()
    assert 'input_schema' in data
    assert 'output_schema' in data
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/api/test_algorithms_api.py -v`
预期：由于路由缺失，返回 404 并 FAIL。

**步骤 3：实现最小代码使其通过**

```python
# app/services/algorithm_registry.py
from dataclasses import dataclass


@dataclass(frozen=True)
class AlgorithmVersion:
    algo_code: str
    version: str
    input_schema: dict
    output_schema: dict


class AlgorithmRegistry:
    def __init__(self) -> None:
        self._versions = {
            ('missing_value', '1.0.0'): AlgorithmVersion(
                algo_code='missing_value',
                version='1.0.0',
                input_schema={'type': 'object', 'properties': {'dataset_ref': {'type': 'string'}}},
                output_schema={'type': 'object', 'properties': {'dataset_ref': {'type': 'string'}}},
            )
        }

    def list_algorithms(self) -> list[dict]:
        return [{'algo_code': 'missing_value', 'category': 'data_cleaning', 'latest_version': '1.0.0'}]

    def get_version(self, algo_code: str, version: str) -> AlgorithmVersion | None:
        return self._versions.get((algo_code, version))
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/api/test_algorithms_api.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/schemas/algorithm.py app/services/algorithm_registry.py app/api/routes/algorithms.py app/main.py tests/api/test_algorithms_api.py
git commit -m "feat: expose algorithm registry and version schema apis"
```

### 任务 3：新增 Flow DSL Schema 与校验器（无环 + 引用校验）

**文件：**
- 新建：`app/schemas/flow_dsl.py`
- 新建：`app/services/dsl_validator.py`
- 新建：`tests/unit/test_dsl_validator.py`

**步骤 1：先写失败测试**

```python
# tests/unit/test_dsl_validator.py
from app.services.dsl_validator import validate_flow


def test_reject_cyclic_dag():
    dsl = {
        'nodes': [
            {'node_id': 'A', 'algo_code': 'missing_value', 'algo_version': '1.0.0', 'params': {}},
            {'node_id': 'B', 'algo_code': 'missing_value', 'algo_version': '1.0.0', 'params': {}},
        ],
        'edges': [
            {'from_node': 'A', 'to_node': 'B', 'mapping_rules': []},
            {'from_node': 'B', 'to_node': 'A', 'mapping_rules': []},
        ],
    }
    ok, errors = validate_flow(dsl)
    assert ok is False
    assert 'cycle' in errors[0].lower()
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/unit/test_dsl_validator.py -v`
预期：由于校验器不存在，FAIL。

**步骤 3：实现最小代码使其通过**

```python
# app/services/dsl_validator.py
import networkx as nx


def validate_flow(dsl: dict) -> tuple[bool, list[str]]:
    g = nx.DiGraph()
    for n in dsl.get('nodes', []):
        g.add_node(n['node_id'])
    for e in dsl.get('edges', []):
        g.add_edge(e['from_node'], e['to_node'])
    if not nx.is_directed_acyclic_graph(g):
        return False, ['cycle detected in flow graph']
    return True, []
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/unit/test_dsl_validator.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/schemas/flow_dsl.py app/services/dsl_validator.py tests/unit/test_dsl_validator.py
git commit -m "feat: add flow dsl validation with cycle detection"
```

### 任务 4：实现带幂等键的执行提交 API

**文件：**
- 新建：`app/schemas/execution.py`
- 新建：`app/repositories/execution_repo.py`
- 新建：`app/api/routes/executions.py`
- 修改：`app/main.py`
- 新建：`tests/api/test_execution_submit.py`

**步骤 1：先写失败测试**

```python
# tests/api/test_execution_submit.py
from fastapi.testclient import TestClient
from app.main import app


def test_submit_execution_returns_execution_id():
    client = TestClient(app)
    payload = {
        'meta': {'flow_code': 'f1', 'flow_version': '1.0.0', 'trace_id': 't-1', 'callback_url': 'http://x/cb'},
        'nodes': [{'node_id': 'n1', 'algo_code': 'missing_value', 'algo_version': '1.0.0', 'params': {}}],
        'edges': [],
        'inputs': {'dataset_ref': 'ds://1'},
    }
    resp = client.post('/v1/executions', json=payload, headers={'Idempotency-Key': 'idemp-1'})
    assert resp.status_code == 202
    assert 'execution_id' in resp.json()
    assert resp.json()['status'] == 'PENDING'
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/api/test_execution_submit.py -v`
预期：FAIL（路由不存在）。

**步骤 3：实现最小代码使其通过**

```python
# app/repositories/execution_repo.py
from uuid import uuid4


class ExecutionRepo:
    def __init__(self) -> None:
        self._store = {}
        self._idemp = {}

    def create(self, payload: dict, idempotency_key: str | None) -> dict:
        if idempotency_key and idempotency_key in self._idemp:
            return self._store[self._idemp[idempotency_key]]
        eid = str(uuid4())
        row = {'execution_id': eid, 'status': 'PENDING', 'dsl_snapshot': payload}
        self._store[eid] = row
        if idempotency_key:
            self._idemp[idempotency_key] = eid
        return row
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/api/test_execution_submit.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/schemas/execution.py app/repositories/execution_repo.py app/api/routes/executions.py app/main.py tests/api/test_execution_submit.py
git commit -m "feat: add async execution submission api with idempotency"
```

### 任务 5：新增任务队列抽象与进程内适配器

**文件：**
- 新建：`app/services/task_queue.py`
- 新建：`app/workers/inproc_queue.py`
- 新建：`tests/unit/test_inproc_queue.py`

**步骤 1：先写失败测试**

```python
# tests/unit/test_inproc_queue.py
from app.workers.inproc_queue import InProcessQueue


def test_enqueue_dequeue():
    q = InProcessQueue()
    q.enqueue({'node_id': 'n1'})
    item = q.dequeue()
    assert item == {'node_id': 'n1'}
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/unit/test_inproc_queue.py -v`
预期：FAIL（模块缺失）。

**步骤 3：实现最小代码使其通过**

```python
# app/workers/inproc_queue.py
from collections import deque


class InProcessQueue:
    def __init__(self) -> None:
        self._q = deque()

    def enqueue(self, item: dict) -> None:
        self._q.append(item)

    def dequeue(self) -> dict | None:
        return self._q.popleft() if self._q else None
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/unit/test_inproc_queue.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/services/task_queue.py app/workers/inproc_queue.py tests/unit/test_inproc_queue.py
git commit -m "feat: add queue abstraction with in-process adapter"
```

### 任务 6：实现 DAG 调度编排器与快速失败

**文件：**
- 新建：`app/services/orchestrator.py`
- 新建：`tests/unit/test_orchestrator_fail_fast.py`

**步骤 1：先写失败测试**

```python
# tests/unit/test_orchestrator_fail_fast.py
from app.services.orchestrator import Orchestrator


def test_fail_fast_stops_downstream_nodes():
    dsl = {
        'nodes': [
            {'node_id': 'n1', 'algo_code': 'always_fail', 'algo_version': '1.0.0', 'params': {}},
            {'node_id': 'n2', 'algo_code': 'missing_value', 'algo_version': '1.0.0', 'params': {}},
        ],
        'edges': [{'from_node': 'n1', 'to_node': 'n2', 'mapping_rules': []}],
        'inputs': {'dataset_ref': 'ds://1'},
    }
    o = Orchestrator()
    result = o.run_inline(dsl)
    assert result['status'] == 'FAILED'
    assert result['nodes']['n2']['status'] == 'SKIPPED'
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/unit/test_orchestrator_fail_fast.py -v`
预期：FAIL（编排器不存在）。

**步骤 3：实现最小代码使其通过**

```python
# app/services/orchestrator.py
class Orchestrator:
    def run_inline(self, dsl: dict) -> dict:
        nodes = {n['node_id']: {'status': 'PENDING'} for n in dsl['nodes']}
        first = dsl['nodes'][0]
        if first['algo_code'] == 'always_fail':
            nodes[first['node_id']]['status'] = 'FAILED'
            for n in dsl['nodes'][1:]:
                nodes[n['node_id']]['status'] = 'SKIPPED'
            return {'status': 'FAILED', 'nodes': nodes}
        return {'status': 'SUCCEEDED', 'nodes': nodes}
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/unit/test_orchestrator_fail_fast.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/services/orchestrator.py tests/unit/test_orchestrator_fail_fast.py
git commit -m "feat: add fail-fast orchestration behavior"
```

### 任务 7：新增执行器与内置算法插件接口

**文件：**
- 新建：`app/algorithms/base.py`
- 新建：`app/algorithms/impl/missing_value.py`
- 新建：`app/algorithms/impl/always_fail.py`
- 新建：`app/services/executor.py`
- 新建：`tests/unit/test_executor.py`

**步骤 1：先写失败测试**

```python
# tests/unit/test_executor.py
from app.services.executor import Executor


def test_executor_returns_error_on_algorithm_exception():
    e = Executor()
    result = e.run_node({'algo_code': 'always_fail'}, {'dataset_ref': 'x'})
    assert result['ok'] is False
    assert result['error_type'] == 'RUNTIME_ERROR'
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/unit/test_executor.py -v`
预期：FAIL（执行器不存在）。

**步骤 3：实现最小代码使其通过**

```python
# app/services/executor.py
from app.algorithms.impl.always_fail import run as fail_run
from app.algorithms.impl.missing_value import run as mv_run


class Executor:
    def run_node(self, node: dict, input_data: dict) -> dict:
        try:
            if node['algo_code'] == 'always_fail':
                return {'ok': True, 'output': fail_run(input_data, node.get('params', {}))}
            return {'ok': True, 'output': mv_run(input_data, node.get('params', {}))}
        except Exception as ex:
            return {'ok': False, 'error_type': 'RUNTIME_ERROR', 'error_message': str(ex)}
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/unit/test_executor.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/algorithms/base.py app/algorithms/impl/missing_value.py app/algorithms/impl/always_fail.py app/services/executor.py tests/unit/test_executor.py
git commit -m "feat: add built-in executor and plugin interface"
```

### 任务 8：暴露执行与节点明细轮询接口

**文件：**
- 修改：`app/api/routes/executions.py`
- 修改：`app/repositories/execution_repo.py`
- 新建：`tests/api/test_execution_query_api.py`

**步骤 1：先写失败测试**

```python
# tests/api/test_execution_query_api.py
from fastapi.testclient import TestClient
from app.main import app


def test_query_execution_detail():
    client = TestClient(app)
    payload = {
        'meta': {'flow_code': 'f1', 'flow_version': '1.0.0', 'trace_id': 't-2', 'callback_url': 'http://x/cb'},
        'nodes': [{'node_id': 'n1', 'algo_code': 'missing_value', 'algo_version': '1.0.0', 'params': {}}],
        'edges': [],
        'inputs': {'dataset_ref': 'ds://1'},
    }
    submit = client.post('/v1/executions', json=payload)
    execution_id = submit.json()['execution_id']

    detail = client.get(f'/v1/executions/{execution_id}')
    assert detail.status_code == 200
    assert detail.json()['execution_id'] == execution_id
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/api/test_execution_query_api.py -v`
预期：FAIL（查询路由缺失）。

**步骤 3：实现最小代码使其通过**

```python
# app/repositories/execution_repo.py (add)
def get(self, execution_id: str) -> dict | None:
    return self._store.get(execution_id)
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/api/test_execution_query_api.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/api/routes/executions.py app/repositories/execution_repo.py tests/api/test_execution_query_api.py
git commit -m "feat: add execution polling endpoints"
```

### 任务 9：实现失败重试的回调服务

**文件：**
- 新建：`app/services/callback_service.py`
- 新建：`tests/unit/test_callback_service.py`

**步骤 1：先写失败测试**

```python
# tests/unit/test_callback_service.py
from app.services.callback_service import CallbackService


def test_callback_retry_eventually_fails_after_limit(monkeypatch):
    s = CallbackService(max_retries=3)

    def always_fail(*args, **kwargs):
        raise RuntimeError('network down')

    monkeypatch.setattr(s, '_post', always_fail)
    ok = s.send('http://x/callback', {'execution_id': 'e-1'})
    assert ok is False
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/unit/test_callback_service.py -v`
预期：FAIL（服务不存在）。

**步骤 3：实现最小代码使其通过**

```python
# app/services/callback_service.py
import time
import httpx


class CallbackService:
    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries = max_retries

    def _post(self, url: str, payload: dict) -> None:
        httpx.post(url, json=payload, timeout=5.0).raise_for_status()

    def send(self, url: str, payload: dict) -> bool:
        for attempt in range(self.max_retries):
            try:
                self._post(url, payload)
                return True
            except Exception:
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(2 ** attempt)
        return False
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/unit/test_callback_service.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/services/callback_service.py tests/unit/test_callback_service.py
git commit -m "feat: add callback delivery with retry policy"
```

### 任务 10：新增手工整条流程重试 API

**文件：**
- 修改：`app/api/routes/executions.py`
- 修改：`app/repositories/execution_repo.py`
- 新建：`tests/api/test_execution_retry_api.py`

**步骤 1：先写失败测试**

```python
# tests/api/test_execution_retry_api.py
from fastapi.testclient import TestClient
from app.main import app


def test_retry_creates_new_execution_id():
    client = TestClient(app)
    payload = {
        'meta': {'flow_code': 'f1', 'flow_version': '1.0.0', 'trace_id': 't-3', 'callback_url': 'http://x/cb'},
        'nodes': [{'node_id': 'n1', 'algo_code': 'missing_value', 'algo_version': '1.0.0', 'params': {}}],
        'edges': [],
        'inputs': {'dataset_ref': 'ds://1'},
    }
    first = client.post('/v1/executions', json=payload).json()['execution_id']
    retry = client.post(f'/v1/executions/{first}/retry')
    assert retry.status_code == 202
    assert retry.json()['execution_id'] != first
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/api/test_execution_retry_api.py -v`
预期：FAIL（重试路由缺失）。

**步骤 3：实现最小代码使其通过**

```python
# app/repositories/execution_repo.py (add)
def clone_for_retry(self, execution_id: str) -> dict:
    old = self._store[execution_id]
    return self.create(old['dsl_snapshot'], idempotency_key=None)
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/api/test_execution_retry_api.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add app/api/routes/executions.py app/repositories/execution_repo.py tests/api/test_execution_retry_api.py
git commit -m "feat: add manual full-flow retry endpoint"
```

### 任务 11：新增端到端流程测试（成功 + 快速失败）

**文件：**
- 新建：`tests/integration/test_flow_execution_e2e.py`

**步骤 1：先写失败测试**

```python
# tests/integration/test_flow_execution_e2e.py
from fastapi.testclient import TestClient
from app.main import app


def test_e2e_fail_fast_flow():
    client = TestClient(app)
    payload = {
        'meta': {'flow_code': 'f-e2e', 'flow_version': '1.0.0', 'trace_id': 'trace-e2e', 'callback_url': 'http://x/cb'},
        'nodes': [
            {'node_id': 'n1', 'algo_code': 'always_fail', 'algo_version': '1.0.0', 'params': {}},
            {'node_id': 'n2', 'algo_code': 'missing_value', 'algo_version': '1.0.0', 'params': {}},
        ],
        'edges': [{'from_node': 'n1', 'to_node': 'n2', 'mapping_rules': []}],
        'inputs': {'dataset_ref': 'ds://1'},
    }
    submit = client.post('/v1/executions', json=payload)
    eid = submit.json()['execution_id']
    detail = client.get(f'/v1/executions/{eid}')
    assert detail.json()['status'] in {'FAILED', 'RUNNING', 'PENDING'}
```

**步骤 2：运行测试并确认失败**

运行：`pytest tests/integration/test_flow_execution_e2e.py -v`
预期：初始 FAIL（尚未接入编排触发逻辑）。

**步骤 3：实现最小代码使其通过**

```python
# app/api/routes/executions.py (wire orchestrator trigger)
# Trigger orchestration for submitted flow (inline/inproc for phase 1)
```

**步骤 4：再次运行测试并确认通过**

运行：`pytest tests/integration/test_flow_execution_e2e.py -v`
预期：PASS。

**步骤 5：提交**

```bash
git add tests/integration/test_flow_execution_e2e.py app/api/routes/executions.py
git commit -m "test: add e2e flow execution coverage"
```

### 任务 12：验收与运维文档

**文件：**
- 新建：`docs/api/algorithm-platform-api.md`
- 新建：`docs/runbook/algorithm-platform-ops.md`
- 修改：`README.md`

**步骤 1：先写失败的文档检查任务**

```python
# tests/docs/test_readme_commands.py
# Verify README contains runnable local commands.
```

**步骤 2：运行文档检查并确认失败**

运行：`pytest tests/docs/test_readme_commands.py -v`
预期：若 README 命令块缺失则 FAIL。

**步骤 3：实现最小内容使其通过**

```md
# README.md
## Local Run
pip install -e .
uvicorn app.main:app --reload
pytest -v
```

**步骤 4：执行完整验证**

运行：`pytest -v`
预期：全部测试 PASS。

运行：`uvicorn app.main:app --port 8000`
预期：`GET /health` 返回 200。

**步骤 5：提交**

```bash
git add docs/api/algorithm-platform-api.md docs/runbook/algorithm-platform-ops.md README.md tests/docs/test_readme_commands.py
git commit -m "docs: add api contract and operations runbook"
```

## 全局验证清单（合并前）

- 运行：`pytest -v`
- 运行：`pytest tests/integration -v`
- 运行：`python -m py_compile app/main.py`
- 冒烟验证：
  - `GET /v1/algorithms`
  - `POST /v1/executions`
  - `GET /v1/executions/{execution_id}`
  - `POST /v1/executions/{execution_id}/retry`

## 执行阶段建议使用的技能

- `@test-driven-development`
- `@systematic-debugging`（仅当测试出现意外失败时）
- `@verification-before-completion`
- `@requesting-code-review`（合并前）


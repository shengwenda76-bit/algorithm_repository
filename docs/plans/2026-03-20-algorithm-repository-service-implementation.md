# 算法仓库服务系统 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个基于 FastAPI 和 SQLAlchemy 的算法仓库服务，提供算法元数据注册、校验、持久化及目录查询能力。

**Architecture:** Router(路由层) -> Service(业务逻辑层) -> Repository(数据库操作层) 的三层架构，底层使用 SQLite。引入全局 logging。

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Python `logging`, SQLite.

---

### Task 1: 基础配置与依赖准备

**Files:**
- Create: `services/library_platform/settings.py` (修改现有的)
- Create: `services/library_platform/logging/setup.py`

**Step 1: 编写基础配置**
在 `services/library_platform/settings.py` 中定义包含 DB_URL 和 LOG_DIR 的 `Settings` 类。

**Step 2: 编写日志配置**
在 `services/library_platform/logging/setup.py` 中编写 `setup_logging` 函数，配置 `TimedRotatingFileHandler`。

**Step 3: Commit**
```bash
git add services/library_platform/settings.py services/library_platform/logging/setup.py
git commit -m "feat: setup configuration and logging"
```

---

### Task 2: 数据库引擎与基础架构

**Files:**
- Create: `services/library_platform/database/base.py`
- Create: `services/library_platform/database/migrations.py`

**Step 1: 编写 base.py**
定义 `engine`, `SessionLocal`, `Base = declarative_base()`。

**Step 2: 编写 migrations.py**
定义 `init_db` 函数，调用 `Base.metadata.create_all(bind=engine)`。

**Step 3: Commit**
```bash
git add services/library_platform/database/
git commit -m "feat: database connection and base models"
```

---

### Task 3: ORM 模型开发

**Files:**
- Create: `services/library_platform/models/algorithm.py`
- Create: `services/library_platform/models/algorithm_version.py`
- Create: `services/library_platform/models/algorithm_artifact.py`
- Create: `services/library_platform/models/__init__.py`

**Step 1: 编写 Algorithm 模型**
主键、代码、名称、类别、描述、状态、时间。

**Step 2: 编写 AlgorithmVersion 模型**
外键、版本、入口、相关 JSON 字段、is_latest。

**Step 3: 编写 AlgorithmArtifact 模型**
外键、版本、包名、链接等。

**Step 4: 暴露模型**
在 `models/__init__.py` 导入这三个模型以供 Base 识别。

**Step 5: Commit**
```bash
git add services/library_platform/models/
git commit -m "feat: sqlalchemy orm models for algorithms"
```

---

### Task 4: Pydantic Schemas 开发

**Files:**
- Create: `services/library_platform/schemas/registry.py`
- Create: `services/library_platform/schemas/catalog.py`
- Create: `services/library_platform/schemas/common.py`

**Step 1: 编写 Common Schema**
提取可复用的 ErrorResponse。

**Step 2: 编写 Registry Schema**
定义 `RegisterRequest`, `RegisterResponse`, `ValidateResponse`。注意必须能够反序列化 `definition` 和 `artifact`，可借用 `sdk` 里的部分字段。

**Step 3: 编写 Catalog Schema**
定义查询相关的响应模型。

**Step 4: Commit**
```bash
git add services/library_platform/schemas/
git commit -m "feat: pydantic schemas for registry and catalog"
```

---

### Task 5: Repository 层封装

**Files:**
- Create: `services/library_platform/repositories/algorithm_repository.py`

**Step 1: 编写 AlgorithmRepository**
封装通过 SQLAlchemy 读取和写入 `Algorithm`, `AlgorithmVersion`, `AlgorithmArtifact` 的操作，包含如 `create_or_update_algorithm`, `add_version`, `get_algorithm_by_code` 等方法。

**Step 2: Commit**
```bash
git add services/library_platform/repositories/
git commit -m "feat: database repository layer"
```

---

### Task 6: Service 层封装

**Files:**
- Create: `services/library_platform/services/registry_service.py`
- Create: `services/library_platform/services/catalog_service.py`

**Step 1: 编写 RegistryService**
基于 `AlgorithmRepository` 实现 `register`, `validate`（调用 SDK 的 validators）。包含版本重复校验及将前序版本 is_latest 设为 false 的逻辑。

**Step 2: 编写 CatalogService**
封装列表、详情、多版本查询逻辑。

**Step 3: Commit**
```bash
git add services/library_platform/services/
git commit -m "feat: business logic services"
```

---

### Task 7: 依赖注入与 API 路由

**Files:**
- Create: `services/library_platform/dependencies.py`
- Create: `services/library_platform/routers/registry.py`
- Create: `services/library_platform/routers/catalog.py`

**Step 1: 编写 Dependencies**
提供 `get_db`，`get_registry_service`, `get_catalog_service`。

**Step 2: 编写 Registry Router**
使用 `APIRouter`，注册 `POST /algorithms/register` 和 `/validate`。

**Step 3: 编写 Catalog Router**
注册各个 `GET /algorithms/` 的端点。

**Step 4: Commit**
```bash
git add services/library_platform/dependencies.py services/library_platform/routers/
git commit -m "feat: api routes and dependencies"
```

---

### Task 8: FastAPI App 组装与中间件

**Files:**
- Modify: `services/library_platform/app.py`
- Create: `services/library_platform/main.py`

**Step 1: 编写 app.py**
创建 FastAPI 实例，初始化数据库，配置路由。添加一个简单的请求日志 Middleware。

**Step 2: 编写 main.py**
uvicorn 启动脚本入口。

**Step 3: Commit**
```bash
git add services/library_platform/app.py services/library_platform/main.py
git commit -m "feat: fastapi application assembly and main entry"
```

---

### Task 9: 测试补齐

**Files:**
- Create: `tests/platform/test_registry_api.py` (覆盖或修改)
- Create: `tests/platform/test_catalog_api.py` (覆盖或修改)

**Step 1: 编写 API 测试**
使用 `TestClient` 测试 `/validate`, `/register`, 以及 `/algorithms/` 查询接口。

**Step 2: 运行测试并验证**
`pytest tests/platform/ -v`

**Step 3: Commit**
```bash
git add tests/platform/
git commit -m "test: api endpoints testing"
```

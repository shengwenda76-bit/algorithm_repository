# 算法仓库服务系统设计文档

**日期：** 2026-03-20  
**版本：** v1.0  
**状态：** 已确认

---

## 1. 背景与目标

当前系统由两个子系统构成：

- **算法开发系统（系统 A，已完成）**：提供算法开发环境，开发者完成算法后提交到私有 PyPI，完成后自动调用算法仓库服务的注册接口。
- **算法仓库服务（系统 B，本文档描述）**：接收算法注册、进行校验、持久化存储，并向 H4 平台提供统一的算法查询接口。

**系统 B 的核心目标：**

1. 接收系统 A 的注册请求，校验算法元数据和制品信息，持久化写入数据库
2. 向 H4 平台提供算法列表、详情、版本等查询接口
3. 记录系统运行日志，便于排查问题

---

## 2. 技术选型

| 维度 | 选型 | 理由 |
|---|---|---|
| Web 框架 | FastAPI | 异步、自动 OpenAPI 文档、Pydantic 内置校验 |
| 持久化 | SQLite + SQLAlchemy ORM | 轻量无依赖、ORM 易维护、未来可平滑迁移 PostgreSQL |
| 日志 | Python logging + TimedRotatingFileHandler | 标准库、按天归档、无额外依赖 |
| 校验 | 复用 `sdk/algorithm_sdk/validators.py` | 统一校验逻辑，避免重复 |
| 鉴权 | 一期不加，预留 Middleware 扩展点 | 内网部署，先跑通功能 |

---

## 3. 架构设计

### 3.1 整体分层

```
HTTP 请求
    ↓
FastAPI Router（路由层）     ← 接收请求、Pydantic 校验入参、返回响应
    ↓
Service（业务逻辑层）        ← 重复检查、版本管理、业务规则
    ↓
Repository（数据库操作层）   ← SQLAlchemy ORM 增删改查
    ↓
SQLite 数据库
```

### 3.2 目录结构

```
algorithm_repository/
│
├── services/
│   └── library_platform/
│       ├── main.py                  ← uvicorn 启动入口
│       ├── app.py                   ← create_fastapi_app() 工厂函数
│       ├── settings.py              ← 配置管理（支持环境变量覆盖）
│       ├── dependencies.py          ← FastAPI 依赖注入（DB Session、Service）
│       │
│       ├── database/
│       │   ├── __init__.py
│       │   ├── base.py              ← SQLAlchemy engine、SessionLocal、Base
│       │   └── migrations.py        ← create_all() 建表
│       │
│       ├── models/                  ← SQLAlchemy ORM 模型
│       │   ├── __init__.py
│       │   ├── algorithm.py         ← Algorithm 主表
│       │   ├── algorithm_version.py ← AlgorithmVersion 版本表
│       │   └── algorithm_artifact.py← AlgorithmArtifact 制品表
│       │
│       ├── schemas/                 ← Pydantic Schema（请求体/响应体）
│       │   ├── __init__.py
│       │   ├── registry.py          ← RegisterRequest、RegisterResponse、ValidateResponse
│       │   └── catalog.py           ← AlgorithmListResponse、AlgorithmDetail、VersionDetail
│       │
│       ├── repositories/            ← 数据库操作封装
│       │   ├── __init__.py
│       │   └── algorithm_repository.py
│       │
│       ├── services/                ← 业务逻辑
│       │   ├── __init__.py
│       │   ├── registry_service.py  ← 注册、校验
│       │   └── catalog_service.py   ← 查询
│       │
│       ├── routers/                 ← FastAPI 路由
│       │   ├── __init__.py
│       │   ├── registry.py          ← POST /algorithms/register、/validate
│       │   └── catalog.py           ← GET /algorithms/* 系列
│       │
│       └── logging/
│           ├── __init__.py
│           └── setup.py             ← 日志初始化
│
├── sdk/algorithm_sdk/               ← 保持不变，复用校验器
│
├── .runtime/
│   ├── library_platform/
│   │   └── algorithm_library.db    ← SQLite 数据库文件
│   └── logs/
│       └── library_platform.log    ← 系统运行日志
│
├── tests/
│   └── platform/
│       ├── test_registry_api.py
│       ├── test_catalog_api.py
│       └── test_algorithm_repository.py
│
└── docs/plans/
    ├── 2026-03-20-algorithm-repository-service-design.md   ← 本文档
    └── 2026-03-20-algorithm-repository-service-implementation.md
```

---

## 4. 数据库模型设计

### 4.1 三张表关系

```
algorithms (主表，1条记录 = 1个算法)
    ↑ 1:N
algorithm_versions (版本表，1条记录 = 1个算法的某个版本)
    ↑ 1:1
algorithm_artifacts (制品表，1条记录 = 1个版本对应的 PyPI 包信息)
```

### 4.2 algorithms — 算法主表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTO | 自增主键 |
| code | VARCHAR(128) | UNIQUE, NOT NULL | 算法标识码，全局唯一 |
| name | VARCHAR(256) | NOT NULL | 算法名称 |
| category | VARCHAR(128) | | 算法分类 |
| description | TEXT | | 算法描述 |
| status | VARCHAR(32) | DEFAULT 'active' | active / deprecated |
| created_at | DATETIME | NOT NULL | 创建时间（UTC） |
| updated_at | DATETIME | NOT NULL | 最后更新时间（UTC） |

### 4.3 algorithm_versions — 版本表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTO | 自增主键 |
| algorithm_code | VARCHAR(128) | FK→algorithms.code | 关联算法 |
| version | VARCHAR(64) | NOT NULL | 版本号（如 0.1.0） |
| entrypoint | VARCHAR(512) | NOT NULL | 执行入口 |
| inputs_json | TEXT | | 输入字段定义（JSON 数组） |
| outputs_json | TEXT | | 输出字段定义（JSON 数组） |
| params_json | TEXT | | 参数定义（JSON 数组） |
| resources_json | TEXT | | 资源需求（JSON 对象） |
| requirements_json | TEXT | | pip 依赖列表（JSON 数组） |
| tags_json | TEXT | | 标签列表（JSON 数组） |
| status | VARCHAR(32) | DEFAULT 'registered' | registered / deprecated |
| is_latest | BOOLEAN | DEFAULT False | 是否为最新版本 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |
| UNIQUE | | (algorithm_code, version) | 同版本不可重复注册 |

### 4.4 algorithm_artifacts — 制品表

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | PK, AUTO | 自增主键 |
| algorithm_code | VARCHAR(128) | FK→algorithms.code | 关联算法 |
| version | VARCHAR(64) | NOT NULL | 对应版本号 |
| package_name | VARCHAR(256) | NOT NULL | PyPI 包名 |
| package_version | VARCHAR(64) | | PyPI 包版本 |
| repository_url | VARCHAR(512) | | 私有 PyPI 地址 |
| artifact_type | VARCHAR(64) | | wheel / sdist |
| filename | VARCHAR(256) | | 包文件名 |
| sha256 | VARCHAR(64) | | SHA256 校验值 |
| created_at | DATETIME | NOT NULL | |
| updated_at | DATETIME | NOT NULL | |

---

## 5. API 接口设计

### 5.1 接口总览

| 方法 | 路径 | HTTP 状态 | 说明 | 调用方 |
|---|---|---|---|---|
| GET | `/` | 200 | 服务健康检查 & 基本信息 | 运维 |
| POST | `/algorithms/register` | 201 / 409 / 422 | 注册算法 | 系统 A |
| POST | `/algorithms/validate` | 200 / 422 | 仅校验不写库 | 系统 A |
| GET | `/algorithms/` | 200 | 算法列表（分页/筛选） | H4 平台 |
| GET | `/algorithms/{code}` | 200 / 404 | 算法详情（含最新版本） | H4 平台 |
| GET | `/algorithms/{code}/versions` | 200 / 404 | 版本列表 | H4 平台 |
| GET | `/algorithms/{code}/versions/{version}` | 200 / 404 | 版本详情（含制品信息） | H4 平台 |

### 5.2 注册请求体格式（POST /algorithms/register）

```json
{
  "definition": {
    "code": "algo_missing_value",
    "name": "缺失值处理",
    "version": "0.1.0",
    "entrypoint": "algo_missing_value.entry:MissingValueAlgorithm",
    "category": "数据预处理",
    "description": "处理数据集中的缺失值",
    "inputs": [{"name": "data", "data_type": "DataFrame", "required": true}],
    "outputs": [{"name": "result", "data_type": "DataFrame"}],
    "params": [{"name": "strategy", "data_type": "str", "default": "mean"}],
    "resources": {"cpu": "1", "memory": "512M", "timeout": "60s"},
    "requirements": ["pandas>=1.0.0"],
    "tags": ["数据清洗"]
  },
  "artifact": {
    "package_name": "algo-missing-value",
    "package_version": "0.1.0",
    "repository_url": "http://your-private-pypi/simple",
    "artifact_type": "wheel",
    "filename": "algo_missing_value-0.1.0-py3-none-any.whl",
    "sha256": "abc123..."
  }
}
```

### 5.3 统一错误格式

```json
{
  "error": "DUPLICATE_VERSION",
  "message": "算法 algo_missing_value 版本 0.1.0 已注册",
  "detail": {}
}
```

| 错误码 | HTTP 状态 | 场景 |
|---|---|---|
| DUPLICATE_VERSION | 409 | 重复注册同版本 |
| ALGORITHM_NOT_FOUND | 404 | 算法不存在 |
| VERSION_NOT_FOUND | 404 | 版本不存在 |
| VALIDATION_FAILED | 422 | 请求体字段校验失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 5.4 查询接口参数（GET /algorithms/）

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| category | string | - | 按分类筛选（可选） |
| status | string | active | 按状态筛选 |
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量，最大 100 |

---

## 6. 日志设计

### 6.1 日志格式

```
2026-03-20 14:48:30,123 | INFO  | registry | POST /algorithms/register | algo_missing_value:0.1.0 | 注册成功
2026-03-20 14:48:31,456 | ERROR | catalog  | GET /algorithms/xxx | 算法不存在: xxx
```

### 6.2 日志文件归档

- 文件路径：`.runtime/logs/library_platform.log`
- 按天滚动：`TimedRotatingFileHandler(when='midnight', backupCount=30)`
- 保留最近 30 天归档

### 6.3 请求日志（Middleware）

每次 HTTP 请求自动记录：方法、路径、响应状态码、耗时。

---

## 7. 配置管理

```python
# settings.py
DATABASE_URL = "sqlite:///.runtime/library_platform/algorithm_library.db"
LOG_LEVEL    = "INFO"
LOG_DIR      = ".runtime/logs"
LOG_FILENAME = "library_platform.log"
LOG_BACKUP_DAYS = 30
APP_NAME     = "python-algorithm-library-platform"
APP_VERSION  = "0.1.0"
DEBUG        = False
```

所有配置支持环境变量覆盖，例如：
```bash
DATABASE_URL=sqlite:///data/alg.db uvicorn services.library_platform.main:app
```

---

## 8. 启动方式

```bash
# 开发模式
uvicorn services.library_platform.main:app --reload --port 8000

# 生产模式
uvicorn services.library_platform.main:app --host 0.0.0.0 --port 8000
```

启动后自动完成：初始化日志目录、创建数据库文件、自动建表、挂载所有路由。

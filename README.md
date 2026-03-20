# Python 算法库平台

本仓库用于承载 Python 算法库平台的一期实现脚手架。

当前平台的定位不是“直接执行算法的计算平台”，而是一个面向 H4 平台的 Python 算法库管理平台，负责统一算法开发规范、算法包发布、算法元数据注册、算法目录查询、版本管理、基础校验和调试验证。

## 1. 总体目标

当前架构的总体目标如下：

- 统一 Python 算法开发规范，降低新增算法的接入成本
- 以“多算法包仓库 + 私有 PyPI”的方式管理源码与发布物
- 建立注册中心，统一维护算法元数据和算法包信息
- 建立目录服务，向 H4 平台提供算法列表、版本、参数和详情查询能力
- 预留调试执行能力，便于开发阶段联调和验证
- 为后续补充数据库、FastAPI 接口、测试体系和发布流程提供稳定骨架

## 2. 当前架构概览

当前仓库采用单仓多模块结构，对应设计文档中的一期方案：

```text
algorithm_repository/
|-- README.md
|-- pytest.ini
|-- .gitignore
|-- algorithms/
|   `-- algo_missing_value/
|       |-- pyproject.toml
|       `-- algo_missing_value/
|           |-- __init__.py
|           |-- entry.py
|           |-- meta.py
|           `-- schema.py
|-- sdk/
|   `-- algorithm_sdk/
|       |-- __init__.py
|       |-- base.py
|       |-- contracts.py
|       |-- meta.py
|       `-- validators.py
|-- services/
|   `-- library_platform/
|       |-- __init__.py
|       |-- app.py
|       |-- db.py
|       |-- models.py
|       |-- schemas.py
|       |-- registry/
|       |   |-- __init__.py
|       |   `-- routes.py
|       |-- catalog/
|       |   |-- __init__.py
|       |   `-- routes.py
|       `-- debug/
|           |-- __init__.py
|           `-- routes.py
|-- tools/
|   |-- publish_cli.py
|   |-- validate_package.py
|   `-- scaffold/
|       |-- __init__.py
|       `-- create_algorithm.py
|-- tests/
|   |-- test_repo_layout.py
|   |-- algorithms/
|   |   `-- test_missing_value_algorithm.py
|   |-- docs/
|   |   `-- test_readme_mentions_platform_modules.py
|   |-- integration/
|   |   `-- test_schema_bootstrap.py
|   |-- platform/
|   |   |-- test_algorithm_models.py
|   |   |-- test_catalog_api.py
|   |   |-- test_debug_execute_api.py
|   |   `-- test_registry_api.py
|   |-- sdk/
|   |   |-- test_algorithm_contracts.py
|   |   `-- test_package_validator.py
|   `-- tools/
|       `-- test_publish_cli.py
`-- docs/
    |-- algorithm-package-spec.md
    |-- architecture/
    |   `-- python-algorithm-library-platform.md
    `-- plans/
        |-- 2026-03-17-python-operator-asset-platform-design.md
        `-- 2026-03-17-python-operator-asset-platform-implementation.md
```

## 3. 模块职责

### 3.1 `algorithms/`

用于存放多个独立的 Python 算法包源码。

- 每个算法包独立维护自己的 `pyproject.toml`
- 每个算法包内部包含算法入口、元数据和参数说明
- 当前示例算法为 `algo_missing_value`

### 3.2 `sdk/algorithm_sdk/`

用于定义算法开发时共享的基础契约。

- 统一算法基类
- 统一元数据结构
- 输入输出和参数契约
- 元数据和制品校验工具

### 3.3 `services/library_platform/`

用于承载算法库平台自身的服务模块。

- `registry/`：算法注册和校验相关模块
- `catalog/`：算法目录和详情查询相关模块
- `debug/`：算法调试执行相关模块
- 根目录下的 `app.py / models.py / schemas.py / db.py` 用于放置应用入口、核心模型、接口 schema 和数据库接入占位

### 3.4 `tools/`

用于存放发布、校验和脚手架工具。

- 发布工具
- 校验工具
- 新算法包生成工具

### 3.5 `tests/`

用于为 SDK、算法包、平台模块、工具脚本和文档提供测试入口。

当前测试文件主要用于固定目录结构和后续功能落位点，便于下一步补充真正可运行的测试逻辑。

### 3.6 `docs/`

用于沉淀算法包规范、架构说明和历史设计文档。

## 4. 关键文件说明

下面按当前文件逐个说明其用途。

### 4.1 根目录文件

- `.gitignore`
  - 当前用于忽略本地 worktree 和 Python 缓存文件，避免污染仓库状态。
- `README.md`
  - 当前项目总说明文档，用于介绍架构目标、目录结构和文件职责。
- `pytest.ini`
  - pytest 基础配置文件，当前用于指定测试目录和测试文件命名模式。

### 4.2 SDK 文件

- `sdk/algorithm_sdk/__init__.py`
  - 暴露 SDK 的公共入口。
- `sdk/algorithm_sdk/base.py`
  - 定义算法统一基类 `BaseAlgorithm`。
- `sdk/algorithm_sdk/meta.py`
  - 定义算法元数据结构 `AlgorithmMeta`。
- `sdk/algorithm_sdk/contracts.py`
  - 定义输入输出、参数和资源需求等契约占位模型。
- `sdk/algorithm_sdk/validators.py`
  - 提供算法元数据和算法包信息的基础校验函数。

### 4.3 示例算法包文件

- `algorithms/algo_missing_value/pyproject.toml`
  - 缺失值处理算法包的打包配置示例。
- `algorithms/algo_missing_value/algo_missing_value/__init__.py`
  - 示例算法包声明文件。
- `algorithms/algo_missing_value/algo_missing_value/entry.py`
  - 示例算法的执行入口，演示 `BaseAlgorithm` 的最小实现方式。
- `algorithms/algo_missing_value/algo_missing_value/meta.py`
  - 示例算法的元数据定义。
- `algorithms/algo_missing_value/algo_missing_value/schema.py`
  - 示例算法的输入、输出和参数说明。

### 4.4 平台服务文件

- `services/library_platform/__init__.py`
  - 平台服务包声明文件。
- `services/library_platform/app.py`
  - 平台应用入口占位文件，后续可扩展为 FastAPI 应用入口。
- `services/library_platform/models.py`
  - 平台核心模型占位文件，当前包含算法定义和算法包信息模型。
- `services/library_platform/schemas.py`
  - 平台接口 schema 占位文件。
- `services/library_platform/db.py`
  - 数据库接入占位文件，后续用于放置数据库配置和元数据定义。

### 4.5 注册中心模块文件

- `services/library_platform/registry/__init__.py`
  - 注册中心模块声明文件。
- `services/library_platform/registry/routes.py`
  - 注册和校验接口路径常量占位文件。

### 4.6 目录服务模块文件

- `services/library_platform/catalog/__init__.py`
  - 目录服务模块声明文件。
- `services/library_platform/catalog/routes.py`
  - 算法列表、详情和版本查询接口路径常量占位文件。

### 4.7 调试模块文件

- `services/library_platform/debug/__init__.py`
  - 调试模块声明文件。
- `services/library_platform/debug/routes.py`
  - 调试执行接口路径常量占位文件。

### 4.8 工具脚本文件

- `tools/publish_cli.py`
  - 发布登记脚本占位文件，当前提供注册载荷构造函数。
- `tools/validate_package.py`
  - 算法包校验脚本占位文件。
- `tools/scaffold/__init__.py`
  - 脚手架工具模块声明文件。
- `tools/scaffold/create_algorithm.py`
  - 新算法包脚手架生成工具占位文件。

### 4.9 测试文件

- `tests/test_repo_layout.py`
  - 校验当前脚手架目录结构是否存在。
- `tests/sdk/test_algorithm_contracts.py`
  - 用于放置 SDK 契约相关测试。
- `tests/sdk/test_package_validator.py`
  - 用于放置元数据和算法包校验相关测试。
- `tests/algorithms/test_missing_value_algorithm.py`
  - 用于放置示例算法行为测试。
- `tests/platform/test_algorithm_models.py`
  - 用于放置平台模型层测试。
- `tests/platform/test_registry_api.py`
  - 用于放置注册和校验接口测试。
- `tests/platform/test_catalog_api.py`
  - 用于放置目录查询接口测试。
- `tests/platform/test_debug_execute_api.py`
  - 用于放置调试执行接口测试。
- `tests/integration/test_schema_bootstrap.py`
  - 用于放置数据库和平台结构初始化测试。
- `tests/tools/test_publish_cli.py`
  - 用于放置发布工具测试。
- `tests/docs/test_readme_mentions_platform_modules.py`
  - 用于放置 README 文档说明测试。

### 4.10 文档文件

- `docs/algorithm-package-spec.md`
  - 算法包规范文档占位文件。
- `docs/architecture/python-algorithm-library-platform.md`
  - 平台架构说明文档占位文件。
- `docs/plans/2026-03-17-python-operator-asset-platform-design.md`
  - 当前一期架构设计文档。
- `docs/plans/2026-03-17-python-operator-asset-platform-implementation.md`
  - 当前一期实现计划文档。
- `docs/plans/2026-03-18-python-algorithm-library-platform-follow-up.md`
  - 当前开发阶段的后续任务归档文档，用于下次继续时快速恢复上下文。

## 5. 当前状态

当前仓库已经完成以下工作：

- 搭建了一期目录骨架
- 创建了 SDK、算法包、平台模块、工具和测试文件
- 在所有 Python 文件顶部补充了中文文件功能说明
- SDK 已落地基础契约、结构化元数据和基础校验逻辑
- 示例算法 `algo_missing_value` 已能提供元数据并完成调试执行
- 平台应用已具备最小 FastAPI 入口，并打通 `registry / catalog / debug` 三组接口
- 注册、目录和调试接口当前基于内存注册中心工作，可完成最小链路验证
- 平台接口层已经接入 Pydantic schema
- 数据库层已提供无依赖元数据定义，占位后续真实持久化接入

当前还未完成的部分包括：

- 从内存注册中心切换到真实持久化实现
- 统一 API 返回 envelope 和错误结构
- 引入真实数据库依赖、ORM 和迁移工具
- 补齐 pytest 与正式依赖管理
- 联通私有 PyPI 发布与注册流程
- 完善脚手架、配置管理和对外文档

## 6. 下一步建议

建议后续按照下面顺序继续推进：

1. 先把注册中心抽象成 repository/service 两层，并落到真实持久化实现
2. 统一注册、目录和调试接口的响应 envelope 与错误格式
3. 补齐应用配置、健康检查和启动方式
4. 引入 SQLAlchemy / Alembic / PostgreSQL 等正式持久化栈
5. 补齐私有 PyPI 发布、注册和校验工具链
6. 完善脚手架和开发文档

更详细的续做清单见：

- `docs/plans/2026-03-18-python-algorithm-library-platform-follow-up.md`

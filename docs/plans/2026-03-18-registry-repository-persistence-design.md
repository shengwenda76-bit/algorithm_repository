# 注册中心可替换持久化仓储设计

## 1. 目标

本次增量设计的目标不是直接把平台切到 PostgreSQL，而是先把注册中心的数据访问层抽象稳定下来，并提供一个可运行的 sqlite 版最小持久化实现。

这样做的核心收益是：

- 当前可以继续使用标准库完成最小落库
- `RegistryService`、路由层和调试执行层不需要感知底层数据库细节
- 后续切换到 PostgreSQL / SQLAlchemy / Alembic 时，只需要替换仓储实现，而不是重写业务服务

## 2. 设计结论

本次建议采用：

`RegistryRepository 协议 + InMemoryRegistryRepository + SqliteRegistryRepository + repository factory`

其中：

- `RegistryRepository`
  - 定义注册中心的数据访问边界
- `InMemoryRegistryRepository`
  - 继续提供当前内存版实现，保持现有测试和本地调试简单可用
- `SqliteRegistryRepository`
  - 提供最小可落库的 sqlite 实现
- `repository factory`
  - 根据配置决定当前使用内存版还是 sqlite 版

## 3. 边界约束

### 3.1 Service 层约束

`RegistryService` 只依赖仓储协议，不依赖：

- `sqlite3`
- SQL 语句
- 数据库连接对象
- 具体数据库行对象

Service 层只处理：

- 校验
- 业务异常转换
- 返回接口所需的业务视图结构

### 3.2 Repository 层约束

仓储层负责：

- 三张表的读写
- latest 版本切换
- 详情 join 组装
- 调试执行目标查询

仓储层对外返回统一的业务视图字典，不向上游暴露：

- `sqlite3.Row`
- SQLAlchemy model
- 原始表行结构

### 3.3 db.py 约束

`db.py` 保持为数据库基础设施层，只负责：

- 表结构元数据
- 数据库 URL 约定
- sqlite 连接和初始化辅助

不承载：

- 注册流程逻辑
- 查询聚合逻辑
- 业务异常处理

## 4. 三张表语义

### 4.1 algorithms

用于存放算法稳定主信息：

- `code`
- `name`
- `category`
- `description`
- `status`
- `created_at`
- `updated_at`

### 4.2 algorithm_versions

用于存放版本级执行信息：

- `code`
- `version`
- `entrypoint`
- `inputs_json`
- `outputs_json`
- `params_json`
- `resources_json`
- `requirements_json`
- `tags_json`
- `status`
- `is_latest`
- `created_at`
- `updated_at`

### 4.3 algorithm_artifacts

用于存放版本对应制品：

- `code`
- `version`
- `package_name`
- `package_version`
- `repository_url`
- `artifact_type`
- `filename`
- `sha256`
- `created_at`
- `updated_at`

## 5. Repository 协议

建议仓储协议至少包含以下方法：

- `version_exists(code, version)`
- `save_registration(definition, artifact)`
- `list_algorithms()`
- `get_algorithm(code)`
- `list_versions(code)`
- `get_version_detail(code, version)`
- `get_execution_target(code, version=None)`

这些方法的返回结构应保持稳定，这样未来切换数据库时：

- `RegistryService` 不需要重写
- 路由层不需要重写
- schema 层不需要重写

## 6. sqlite 版注册流程

`save_registration(definition, artifact)` 使用单事务完成：

1. upsert `algorithms`
2. insert `algorithm_versions`
3. insert `algorithm_artifacts`
4. update 该 `code` 下旧版本 `is_latest=0`
5. update 当前版本 `is_latest=1`

同时保留业务规则：

- 同一 `(code, version)` 不允许重复注册
- 同一 `code` 下如果 `name / category / description` 变化，则更新 `algorithms`
- 最新版本标记始终只能有一条

## 7. 查询语义

### 7.1 GET /algorithms

- 查询 `algorithms`
- join `algorithm_versions` 中 `is_latest=1`
- 返回：
  - `code`
  - `name`
  - `category`
  - `description`
  - `version`
  - `status`

### 7.2 GET /algorithms/{code}

- 与列表页同逻辑
- 仅按 `code` 过滤为一条

### 7.3 GET /algorithms/{code}/versions

- 查询指定 `code` 下全部版本
- 返回：
  - `version`
  - `status`
  - `is_latest`

### 7.4 GET /algorithms/{code}/versions/{version}

- 查询：
  - `algorithms`
  - `algorithm_versions`
  - `algorithm_artifacts`
- 组装成完整详情：
  - 算法主信息
  - 版本元数据
  - 制品信息

### 7.5 POST /algorithms/{code}/execute

- 如果传了 `version`，按 `code + version` 查 `algorithm_versions`
- 如果没传，按 `is_latest=1` 查
- 返回：
  - `code`
  - `version`
  - `entrypoint`

然后由 `DebugExecutionService` 动态加载执行。

## 8. 配置与切换策略

建议在应用入口增加 repository factory：

- 未配置数据库时，默认使用 `InMemoryRegistryRepository`
- 配置 `sqlite:///...` 时，使用 `SqliteRegistryRepository`

后续切换 PostgreSQL 时，只需要：

- 保留仓储协议
- 新增 `PostgresRegistryRepository`
- 在 factory 中增加选择逻辑

## 9. 测试策略

本次改造建议保留三层测试：

### 9.1 Repository 测试

新增 sqlite 仓储专项测试，覆盖：

- 注册插入三张表
- 更新主表信息
- latest 标记切换
- 查询详情 join
- execute 默认取最新版本

### 9.2 现有平台 API 测试

继续保留：

- `test_registry_api.py`
- `test_catalog_api.py`
- `test_debug_execute_api.py`

用于确保切换仓储实现后，接口行为不变。

### 9.3 app / factory 测试

新增工厂测试，验证：

- 默认使用内存版
- 配置 sqlite URL 时使用 sqlite 版

## 10. 一期结论

本次最推荐的落地方向是：

**先把仓储边界抽稳，再用 sqlite 提供最小持久化实现。**

这样既能保证后续切 PostgreSQL 可行，也不会把当前代码复杂度一次性拉得太高。

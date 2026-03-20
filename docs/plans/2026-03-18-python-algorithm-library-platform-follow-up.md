# Python 算法库平台后续任务归档

## 1. 归档目的

本文用于归档当前一期开发已经完成的内容、仍待继续的任务，以及下次恢复开发时的建议切入点。

当前仓库已经从“纯脚手架”推进到了“最小可运行基线”：

- 目录结构、SDK、示例算法、平台服务和工具脚本都已创建
- 注册、目录、调试三组接口已经可以跑通最小链路
- 平台接口层已经统一接入 Pydantic schema
- 当前仍以“内存注册中心 + 无依赖数据库元数据占位”的方式运行

因此，后续任务的重点不再是“把骨架搭出来”，而是“把现有骨架逐步替换成真实实现”。

## 2. 当前已完成能力

### 2.1 SDK 与算法包

- `sdk/algorithm_sdk/base.py`
  - 已提供统一算法基类 `BaseAlgorithm`
- `sdk/algorithm_sdk/contracts.py`
  - 已支持 `FieldSpec`、`ResourceSpec` 和结构化契约字典化输出
- `sdk/algorithm_sdk/meta.py`
  - 已支持 `entrypoint / inputs / outputs / params / resources / requirements / tags`
- `sdk/algorithm_sdk/validators.py`
  - 已支持算法元数据和算法包信息的基础字段校验
- `algorithms/algo_missing_value/`
  - 已提供一个可执行的示例算法包，可用于调试接口联调

### 2.2 平台服务

- `services/library_platform/app.py`
  - 已提供最小可运行的 FastAPI 应用入口
- `services/library_platform/registry/`
  - 已支持注册和校验
- `services/library_platform/catalog/`
  - 已支持算法列表、详情、版本列表和版本详情查询
- `services/library_platform/debug/`
  - 已支持按 `entrypoint` 进行一次调试执行
- `services/library_platform/schemas.py`
  - 已提供注册、查询、调试相关的请求和响应 schema
- `services/library_platform/models.py`
  - 已与 richer metadata 对齐
- `services/library_platform/db.py`
  - 已提供无依赖的表元数据定义，但还不是真实数据库接入

### 2.3 测试与验证

当前已通过的验证主要包括：

- `tests/platform/test_registry_api.py`
- `tests/platform/test_catalog_api.py`
- `tests/platform/test_debug_execute_api.py`
- `tests/platform/test_app_entry.py`
- `tests/platform/test_schemas.py`
- `tests/platform/test_algorithm_models.py`
- `tests/sdk/test_algorithm_contracts.py`
- `tests/sdk/test_package_validator.py`
- `tests/algorithms/test_missing_value_algorithm.py`
- `tests/integration/test_schema_bootstrap.py`

另外还验证过：

- `python services/library_platform/app.py`
- `python -m py_compile ...`

说明当前代码已经具备“最小可运行、最小可验证”的基础。

## 3. 当前未完成但最值得继续的任务

### 3.1 第一优先级：把注册中心从内存实现切到可持久化实现

这是当前最自然、也最值得优先推进的一步。

原因：

- 现在 `registry / catalog / debug` 都依赖内存态数据
- 当前的 `db.py` 只有表结构元数据，没有真正参与读写
- 如果不先补持久化，后面的目录查询、发布登记、状态治理都会停留在演示态

建议拆法：

1. 抽出 repository 层，例如：
   - `services/library_platform/registry/repository.py`
2. 保留一个 `InMemoryRegistryRepository`
3. 再补一个 `DatabaseRegistryRepository` 或占位实现
4. 让 `RegistryService` 只依赖 repository 抽象，不直接持有内存字典

完成标志：

- 注册结果可以写入持久层抽象
- 目录查询从同一 repository 读取
- 调试执行仍能复用查询结果
- 现有平台测试仍通过

### 3.2 第二优先级：统一 API 返回 envelope 和错误结构

当前接口已经能跑，但响应结构还比较“直接返回业务对象”，后面接前端时会略显松散。

建议统一成类似结构：

```json
{
  "success": true,
  "message": "ok",
  "data": {}
}
```

错误响应也建议统一，例如：

```json
{
  "success": false,
  "message": "algorithm version already exists",
  "errors": [
    {
      "field": "version",
      "reason": "duplicate"
    }
  ]
}
```

完成标志：

- `register / validate / catalog / execute` 的响应风格统一
- 测试断言统一围绕 envelope 结构编写

### 3.3 第三优先级：补应用配置与运行方式

当前 `app.py` 已能创建 FastAPI 实例，但还缺少更正式的配置入口。

建议补充：

- `settings.py` 或等价配置模块
- 环境变量读取
- 健康检查接口
- 开发启动说明

完成标志：

- 平台可以用更正式的方式启动
- 数据库地址、仓库地址等配置不再写死在代码里

## 4. 一期补完任务清单

这些任务不一定要立刻做，但都属于一期范围内值得补齐的内容。

### 4.1 数据与持久化

- 引入 SQLAlchemy
- 引入 Alembic
- 定义真实 ORM 模型或映射层
- 建立 PostgreSQL 初始化和迁移脚本
- 把当前 `db.py` 从“元数据字典”升级为“真实连接与元数据管理”

### 4.2 发布与工具链

- 完善 `tools/publish_cli.py`
- 完善 `tools/validate_package.py`
- 完善 `tools/scaffold/create_algorithm.py`
- 联通“打包 -> 私有 PyPI -> 注册中心登记”的链路

### 4.3 测试与工程化

- 安装并启用 `pytest`
- 增加更完整的 API 测试和集成测试
- 明确依赖管理方式，例如 `pyproject.toml` 或 requirements 文件
- 增加开发环境启动说明

### 4.4 文档与示例

- 把 README 中的“当前状态”持续和真实代码保持同步
- 补一份 API 使用示例文档
- 补一份“如何新增一个算法包”的开发者说明

## 5. 建议的恢复开发顺序

如果下次继续，我建议按下面顺序推进：

1. 先做注册中心 repository 抽象和持久化接入点
2. 再统一 API 返回 envelope
3. 再补应用配置、健康检查和启动方式
4. 再接 SQLAlchemy / Alembic / PostgreSQL
5. 最后联通私有 PyPI 发布与注册工具链

这样做的好处是：

- 不会过早把精力耗在基础设施细节上
- 可以保证当前已经打通的接口链路持续可用
- 每一步都能有明确的回归测试

## 6. 下次继续时建议先看的文件

- `services/library_platform/app.py`
- `services/library_platform/registry/service.py`
- `services/library_platform/registry/routes.py`
- `services/library_platform/catalog/routes.py`
- `services/library_platform/debug/routes.py`
- `services/library_platform/models.py`
- `services/library_platform/schemas.py`
- `services/library_platform/db.py`
- `sdk/algorithm_sdk/meta.py`
- `sdk/algorithm_sdk/contracts.py`

## 7. 下次继续前的建议验证命令

建议恢复开发前先跑这几组命令，确认当前基线仍然是绿的：

```powershell
python -m unittest discover -s tests/platform -p "test_registry_api.py" -v
python -m unittest discover -s tests/platform -p "test_catalog_api.py" -v
python -m unittest discover -s tests/platform -p "test_debug_execute_api.py" -v
python -m unittest discover -s tests/platform -p "test_schemas.py" -v
python -m unittest discover -s tests/sdk -p "test_algorithm_contracts.py" -v
python services/library_platform/app.py
```

## 8. 当前一句话结论

当前仓库已经具备了 Python 算法库平台一期的“最小可运行基线”，下一个最推荐的切入点是：**把内存注册中心替换为可持久化的 repository 实现，并在此基础上统一 API 响应结构。**

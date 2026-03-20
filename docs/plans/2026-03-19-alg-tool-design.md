# alg_tool Design

## Goal

在当前仓库中产出一个可整体复制到任意空目录使用的 `alg_tool/` 工具包。算法开发者只需要保留该文件夹，即可通过 `create_alg.py` 快速生成标准算法包模板，并通过 `publish.py` 完成校验、测试、构建，以及在配置存在时执行上传私有 PyPI 和注册平台的动作。

## Scope

本次设计只覆盖两类开发者动作：

- 创建标准算法包骨架
- 发布单个算法包

本次不覆盖：

- 多算法批量发布
- 复杂 CI 编排
- 平台侧注册接口协议改造
- 私有 PyPI 或平台注册服务的部署

## Portability Constraints

`alg_tool` 必须具备可移植性，不能依赖当前仓库中的 `sdk/`、`services/` 或 `tools/` 目录。算法开发者把 `alg_tool/` 文件夹复制到新的工作目录后，应能直接运行：

```bash
python alg_tool/create_alg.py --name algo_missing_value
python alg_tool/publish.py --name algo_missing_value
```

为满足这一点，`alg_tool` 需要自带：

- 模板文件
- 共享工具函数
- 最小可运行的 `algorithm_sdk` 副本

## Proposed Layout

```text
alg_tool/
├─ __init__.py
├─ create_alg.py
├─ publish.py
├─ common.py
├─ README.md
├─ templates/
│  ├─ pyproject.toml.tpl
│  ├─ package_readme.md.tpl
│  ├─ __init__.py.tpl
│  ├─ entry.py.tpl
│  ├─ meta.py.tpl
│  ├─ schema.py.tpl
│  └─ test_algorithm.py.tpl
└─ vendor/
   └─ algorithm_sdk/
      ├─ __init__.py
      ├─ base.py
      ├─ contracts.py
      ├─ meta.py
      └─ validators.py
```

## create_alg.py Design

### Behavior

执行：

```bash
python alg_tool/create_alg.py --name algo_missing_value
```

在当前工作目录生成：

```text
algorithms/algo_missing_value/
├─ pyproject.toml
├─ README.md
├─ algo_missing_value/
│  ├─ __init__.py
│  ├─ entry.py
│  ├─ meta.py
│  └─ schema.py
└─ tests/
   └─ test_algo_missing_value.py
```

### Derived Values

- 目录名：`algo_missing_value`
- 包名：`algo-missing-value`
- 算法编码：`missing_value`
- 默认入口：`algo_missing_value.entry:Algorithm`

### Template Principles

- 模板尽量最小，避免给开发者过重心智负担
- 入口类统一命名为 `Algorithm`
- 元数据常量统一命名为 `META`
- 同时提供 `ALGORITHM_META = META` 兼容当前仓库现有写法
- README 明确说明要补的内容、本地测试方式、发布方式

## publish.py Design

### Phase 1: Local Validation

发布前先做本地静态和运行时校验：

- 算法目录存在
- 必需文件存在
- `meta.py`、`schema.py`、`entry.py` 可导入
- `META` 或 `ALGORITHM_META` 存在
- `code`、`name`、`version`、`entrypoint` 存在
- `entrypoint` 可动态加载
- `pyproject.toml` 的包名与目录名一致
- `meta` 中的 `code` 与目录名推导结果一致
- 输入输出参数结构满足基本约束
- 执行 `pytest algorithms/<name>/tests -q`

### Phase 2: Build

在算法目录中执行：

```bash
python -m build
```

构建完成后检查：

- `dist/*.whl`
- `dist/*.tar.gz`

并计算 `wheel` 的 `sha256`

### Phase 3: Optional Upload and Registration

如果 `settings.py` 或环境变量覆盖中存在完整配置，则自动继续：

- 上传私有 PyPI
- 调用 `POST /algorithms/register`

如果配置缺失，则只执行本地校验和构建，并给出下一步提示。

### Settings

`alg_tool` 默认提供 `settings.py` 作为集中配置入口，算法开发者复制整个工具目录后，只需修改这一处即可完成上传和平台注册参数配置。环境变量仍然保留，用于覆盖 `settings.py` 中的同名字段。

主要配置分组包括：

- `PYPI.REPOSITORY_URL`
- `PYPI.USERNAME`
- `PYPI.PASSWORD`
- `PYPI.TIMEOUT_SECONDS`
- `PYPI.VERIFY_SSL`
- `PLATFORM.REGISTER_URL`
- `PLATFORM.TOKEN`
- `PLATFORM.TIMEOUT_SECONDS`
- `PLATFORM.VERIFY_SSL`
- `VALIDATION.CHECK_REMOTE_CONNECTIVITY`

对应环境变量覆盖项包括：

- `ALG_TOOL_PYPI_REPOSITORY_URL`
- `ALG_TOOL_PYPI_USERNAME`
- `ALG_TOOL_PYPI_PASSWORD`
- `ALG_TOOL_PYPI_TIMEOUT_SECONDS`
- `ALG_TOOL_PYPI_VERIFY_SSL`
- `ALG_TOOL_PLATFORM_REGISTER_URL`
- `ALG_TOOL_PLATFORM_TOKEN`
- `ALG_TOOL_PLATFORM_TIMEOUT_SECONDS`
- `ALG_TOOL_PLATFORM_VERIFY_SSL`
- `ALG_TOOL_VALIDATION_CHECK_REMOTE_CONNECTIVITY`

### Preflight Validation

发布前先做两层检查：

- 配置完整性校验：避免只配一半参数就进入上传
- 远端连通性校验：在真正上传和注册前先探测远端地址是否可达

## Error Handling

- 目录缺失、导入失败、校验失败时直接终止并返回清晰错误
- 外部命令失败时透传标准输出和错误输出摘要
- 上传或注册失败时保留已成功完成的本地校验和构建结果

## Testing Strategy

采用 TDD，优先覆盖：

- `create_alg.py` 能在临时空目录中生成完整模板
- 生成结果可被导入和测试
- `publish.py` 能在未配置网络环境时完成本地校验与构建信息整理
- `publish.py` 能正确组装平台注册 payload

## Recommended Next Step

先在当前仓库中实现 `alg_tool/`，并通过测试保证它只依赖自身目录内容。完成后，`alg_tool/` 可直接整体复制到算法开发者目录中使用。

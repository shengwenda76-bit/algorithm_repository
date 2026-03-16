# Python 插件化算法包设计

**日期：2026-03-13**
**状态：已确认，可作为后续改造基线**

---

## 1. 目标

将当前算法平台中的示例算法改造成“标准 Python 插件包”形态，并以此作为未来接入真实私有 PyPI 的目标设计。

本次设计的核心目标有四个：

1. 算法包按标准 Python wheel 包发布。
2. 算法入口通过 `pyproject.toml` 的 `entry_points` 声明。
3. 算法注册由平台显式执行，而不是由算法包导入副作用触发。
4. Worker 对算法包执行“下载 -> 安装（`--no-deps`）-> 发现插件 -> 校验 -> 注册 -> 执行”的标准链路。

---

## 2. 核心决策

### 2.1 算法注册是平台行为

算法包不负责调用 `AlgorithmRegistry.register(...)`。  
算法包只负责声明：

1. 算法入口类
2. 算法元数据
3. 参数与输入校验逻辑

平台注册链路负责：

1. 下载指定版本 wheel
2. 安装到本地运行目录（`--no-deps`）
3. 发现 `entry_points`
4. 加载入口类
5. 校验入口类是否继承 `BaseAlgorithm`
6. 调用 `AlgorithmRegistry.register(...)`

### 2.1.1 算法包依赖独立契约包，而不是平台源码路径

算法包不能直接依赖 `app.algorithms.base` 这样的平台内部模块路径。  
否则一旦算法包从私有 PyPI 独立发布，平台源码目录结构就会成为外部算法包的隐式前提，破坏独立性。

正确做法是：

1. 将 `BaseAlgorithm`、`AlgorithmMeta`、`ExecutionMode` 抽到独立契约包，例如 `algorithm_sdk`。
2. 算法包仅依赖这个契约包。
3. 平台自身也依赖同一个契约包。

这样可以保证：

1. 算法包可独立打包与发布。
2. 平台运行时与算法开发时共享同一份契约定义。
3. 后续私有 PyPI 接入不会依赖平台仓库目录结构。

### 2.2 使用标准 Python 插件机制

算法包统一使用：

```toml
[project.entry-points."algorithm_platform.algorithms"]
missing_value = "algo_missing_value.entry:MissingValueAlgorithm"
```

其中：

1. `algorithm_platform.algorithms` 是平台约定的插件组名。
2. `missing_value` 是插件名，建议与 `algo_code` 保持一致。
3. `algo_missing_value.entry:MissingValueAlgorithm` 是入口类的标准声明方式。

### 2.3 分类是元数据，不是安装路径

`data_cleaning`、`data_processing` 这些分类信息不再体现在本地安装路径中，而是保存在算法元数据里。

原因：

1. 真实私有 PyPI 下载/安装后的落盘路径主要由包名决定。
2. 分类本质是治理信息，不是部署路径。
3. 路径按分类分层会让“源码开发目录”和“运行时安装目录”混淆。

### 2.4 算法验证分层处理

验证不全部写在算法内部，而是分三层：

1. 平台接入校验
   - 包是否存在
   - 版本是否可用
   - `entry_points` 是否可发现
   - 入口类是否可导入
2. 平台契约校验
   - 入口类是否继承 `BaseAlgorithm`
   - 元数据是否完整
   - 输出是否满足平台契约
3. 算法业务校验
   - 参数是否合法
   - 输入数据是否满足算法前提
   - 业务规则是否成立

---

## 3. 目标目录结构

```text
app/algorithms/
├── __init__.py
├── base.py
├── registry.py
├── runtime_packages/                    # 模拟“已从私有 PyPI 下载并安装后”的算法包
│   ├── __init__.py
│   ├── algo_missing_value/
│   │   ├── __init__.py
│   │   ├── entry.py
│   │   ├── meta.py
│   │   └── validators.py
│   ├── algo_outliers/
│   │   ├── __init__.py
│   │   ├── entry.py
│   │   ├── meta.py
│   │   └── validators.py
│   └── algo_standardize/
│       ├── __init__.py
│       ├── entry.py
│       ├── meta.py
│       └── validators.py
└── _algo_template/                     # 标准算法包开发模板
    ├── README.md
    ├── pyproject.toml.example
    ├── src/
    │   └── algo_template/
    │       ├── __init__.py
    │       ├── entry.py
    │       ├── meta.py
    │       └── validators.py
    └── tests/
        └── test_entry.py
```

说明：

1. `runtime_packages/` 仅用于当前仓库内模拟“安装后的插件包形态”。
2. `_algo_template/` 用于算法团队开发新算法包时参考。
3. `data_cleaning/`、`data_processing/` 等旧目录应从运行时目录中移除。

---

## 4. 标准算法包模板

每个标准算法包内部统一包含以下文件：

### 4.1 `entry.py`

职责：

1. 定义算法入口类
2. 继承 `BaseAlgorithm`
3. 实现 `execute()`
4. 调用本包 `validators.py` 完成业务校验

示例：

```python
from app.algorithms.base import BaseAlgorithm
from .meta import ALGORITHM_META
from .validators import validate_inputs, validate_params


class MissingValueAlgorithm(BaseAlgorithm):
    meta = ALGORITHM_META

    def execute(self, inputs: dict, params: dict) -> dict:
        validate_inputs(inputs)
        validate_params(params)
        ...
```

### 4.2 `meta.py`

职责：

1. 声明算法元数据
2. 保存 `algo_code`、`category`、`version` 等治理信息

### 4.3 `validators.py`

职责：

1. 保存算法自身的参数校验逻辑
2. 保存算法自身的输入校验逻辑
3. 避免 `entry.py` 过于臃肿

### 4.4 `__init__.py`

职责：

1. 作为 Python 包标识
2. 可对外导出入口类
3. 不允许放注册副作用

---

## 5. 标准 `pyproject.toml` 模板

算法团队发布到私有 PyPI 时，建议采用如下模板：

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "algo-missing-value"
version = "1.0.0"
description = "缺失值处理算法包"
requires-python = ">=3.12"
dependencies = []

[project.entry-points."algorithm_platform.algorithms"]
missing_value = "algo_missing_value.entry:MissingValueAlgorithm"

[tool.algorithm_platform]
algo_code = "missing_value"
category = "data_cleaning"
display_name = "缺失值处理"
```

说明：

1. `project.name` 对应包名。
2. `project.version` 对应包版本。
3. `entry_points` 用于声明平台插件入口。
4. `[tool.algorithm_platform]` 用于保存平台定制元数据。

---

## 6. 平台运行时关联关系

### 6.1 `AlgorithmRegistry` 的职责

[app/algorithms/registry.py](/d:/02_dicitionary/github/h4/algorithm_repository/app/algorithms/registry.py) 未来只负责：

1. 按 `algo_code + version` 保存运行时算法类
2. 提供 `contains()`、`get()`、`register()`、`clear()`

它不负责：

1. 查私有 PyPI
2. 下载 wheel
3. 安装包
4. 解析 `entry_points`

### 6.2 真实关联链路

`Registry` 与私有 PyPI 之间不应直接耦合，目标链路应为：

```text
ExecutionService
  -> AlgorithmResolver
  -> AlgorithmFetcher
  -> AlgorithmInstaller
  -> PluginDiscovery
  -> PlatformValidator
  -> AlgorithmRegistry.register()
  -> execute()
```

### 6.3 Worker 执行链路

Worker 在接到节点任务后，目标执行过程如下：

1. 根据 `algo_code + version` 检查 `AlgorithmRegistry.contains()`
2. 若未命中：
   - 解析算法包名与版本
   - 从私有 PyPI 下载 wheel
   - 本地安装 wheel（`--no-deps`）
   - 读取 `entry_points(group="algorithm_platform.algorithms")`
   - 根据插件名匹配 `algo_code`
   - 加载入口类
   - 校验其是否继承 `BaseAlgorithm`
   - 平台显式调用 `AlgorithmRegistry.register(...)`
3. 从 `Registry` 取出算法类
4. 执行算法
5. 回写节点结果和状态

---

## 7. 当前仓库的过渡实现策略

由于当前仓库还没有真实的 wheel 下载与安装链路，建议采用“两层设计、一层适配”的方式：

1. 目录结构一步到位按标准插件包形态改造。
2. 示例算法改造成“已安装后的包目录”形态。
3. `AlgorithmLoader` 先做一层适配：
   - 当前阶段：按包路径模拟入口发现
   - 后续阶段：替换为标准 `importlib.metadata.entry_points()`

这样可以保证：

1. 当前代码结构与未来真实私有 PyPI 目标态一致
2. 后续只需替换发现/安装机制，不需要重构算法目录本身
3. 在过渡阶段允许 `runtime_packages/` 暂时留在平台仓库中，但其内部导入路径应尽快替换成独立契约包

---

## 8. 三个示例算法映射

当前示例算法建议映射如下：

1. `missing_value`
   - 包名：`algo_missing_value`
   - 入口类：`MissingValueAlgorithm`
   - 类别：`data_cleaning`
2. `outliers`
   - 包名：`algo_outliers`
   - 入口类：`OutliersAlgorithm`
   - 类别：`data_cleaning`
3. `standardize`
   - 包名：`algo_standardize`
   - 入口类：`StandardizeAlgorithm`
   - 类别：`data_processing`

---

## 9. 结论

本设计的最终结论是：

1. 算法包采用标准 Python wheel 形态发布。
2. 算法入口使用 `pyproject.toml entry_points` 声明。
3. 算法注册由平台显式执行，不使用导入副作用。
4. 算法验证采用“平台接入校验 + 平台契约校验 + 算法业务校验”的分层设计。
5. 当前仓库应尽快将 `app/algorithms` 改造成标准插件包模拟结构，为后续真实私有 PyPI 接入铺路。
6. `runtime_packages/` 和 `_algo_template/` 中的入口类、元数据定义应尽快改为依赖独立契约包，而不是 `app.algorithms.base`。

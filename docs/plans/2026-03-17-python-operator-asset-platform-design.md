# Python 算子资产平台注册平台设计

## 1. 文档目的

本文用于明确当前负责范围内的 Python 算子平台架构。目标不是建设一个直接执行算法的计算平台，而是建设一套面向 Python 算子的资产控制平面，负责：

- 标准化开发与打包
- 算子元数据注册与治理
- 算子目录查询与展示
- 向 eKuiper / Flink 提供统一的算子解析与接入信息
- 后续平滑演进到私有 PyPI / 制品仓库模式

本文基于以下前提进行设计：

- 当前只聚焦 Python 算子，不覆盖 Java / Go / Shell 算子治理
- Python 算子主要以 eKuiper / Flink 的插件或 UDF 形式运行
- 当前平台不负责 DAG 调度和算法执行
- 算法包分发采用 `多算法包 + 私有 PyPI`
- 平台负责注册中心、目录服务和引擎接入 API

## 2. 设计结论摘要

建议采用如下总体架构：

`多算法包仓库 + 算法 SDK + 私有 PyPI + 注册中心 + 目录服务 + 引擎接入 API`

其中：

- `多算法包仓库`：承载 Python 算法实现代码
- `算法 SDK`：定义统一算子契约、元数据和校验规范
- `私有 PyPI`：负责分发 wheel 包
- `注册中心`：管理算法元数据、版本、生命周期和兼容性
- `目录服务`：面向前端提供算法查询和展示
- `引擎接入 API`：向 eKuiper / Flink 返回可安装包、入口点和兼容信息

核心原则：

- PyPI 负责“分发包”，不是“管理算法资产”
- 注册中心负责“管理算法资产”，不是“执行算法”
- 计算引擎负责“加载和执行算法”，不是“维护算法台账”
- DAG 中引用的是平台级 `algo_code`，不是 PyPI 包名

## 3. 备选方案对比

### 3.1 方案 A：一体式资产服务

把注册、目录、引擎查询接口全部做在一个服务里，私有 PyPI 独立。

优点：

- 上线快
- 模型简单
- 第一阶段开发成本低

缺点：

- 读写模型耦合
- 后续审批、兼容性校验、同步链路扩展时容易臃肿

### 3.2 方案 B：分层控制平面

将平台拆分为：

- 私有 PyPI
- 注册中心
- 目录服务
- 引擎接入 API

优点：

- 责任清晰
- 易于演进
- 方便对接前端与引擎侧不同诉求

缺点：

- 比一体式多一层同步或服务编排

### 3.3 方案 C：事件驱动微服务化

在方案 B 基础上继续拆出审批、校验、同步、告警等多个异步服务。

优点：

- 最利于大规模治理
- 适合多团队协作

缺点：

- 第一阶段明显过重
- 运维和交付成本偏高

### 3.4 推荐方案

推荐采用 `方案 B：分层控制平面`，但在第一阶段可以先以“单代码仓、多模块、可独立部署”的方式落地，不急于一开始就拆成完全独立的微服务。

## 4. 目标架构

### 4.1 总体结构

```text
开发者
  -> 多算法包仓库
  -> CI 构建发布
      -> 私有 PyPI
      -> 注册中心

注册中心
  -> 目录服务
      -> 前端算法目录 / 算法市场

DAG 平台 / 计算引擎
  -> 引擎接入 API
      -> 查询注册中心
      -> 返回包坐标、入口点、schema、兼容性、状态

计算引擎
  -> 私有 PyPI 拉包
  -> 引擎内部完成插件 / UDF 注册与执行
```

### 4.2 对原始思路的修正

在原始图中，“执行适配层”容易被理解为平台直接执行 Python 算子。当前职责边界下，建议改为“引擎接入层”或“算子解析 API”，其职责是：

- 解析 `algo_code` 和版本约束
- 返回可用版本
- 返回 PyPI 包坐标和校验信息
- 返回入口点和兼容性声明
- 决定当前版本是否允许被引擎使用

因此，本平台是“资产控制平面”，不是“执行平面”。

## 5. 服务边界

### 5.1 算法 SDK

负责定义统一的 Python 算子开发规范：

- `BaseAlgorithm` 或统一接口基类
- `AlgorithmMeta`
- 参数 schema / 输入输出 schema
- 入口点约定
- 校验器
- 本地调试工具

SDK 是算法包和平台契约之间的桥梁。

### 5.2 多算法包仓库

负责承载多个独立 Python 算法包源码：

- 每个算法包独立打包
- 每个算法包独立测试
- 统一依赖 SDK
- 统一由 CI 打包并发布到私有 PyPI

### 5.3 私有 PyPI

负责：

- 保存和分发 wheel 包
- 按包名和版本提供下载
- 作为引擎侧安装来源

不负责：

- 资产生命周期管理
- 兼容性决策
- 状态治理
- 前端展示

### 5.4 注册中心

注册中心是权威写模型，负责：

- 算子登记
- 算子版本登记
- 元数据维护
- 生命周期状态流转
- 兼容性声明管理
- 包坐标绑定
- 审计日志

注册中心回答的问题是：

- 平台里有哪些算子
- 某个算子有哪些版本
- 哪些版本已发布
- 哪些版本允许被引擎使用

### 5.5 目录服务

目录服务是读模型，面向前端展示，负责：

- 算子列表
- 搜索
- 分类和标签筛选
- 算子详情页
- 版本信息展示
- 参数与示例配置展示

目录服务不做状态治理，只消费已发布的结果。

### 5.6 引擎接入 API

引擎接入 API 面向 eKuiper / Flink，负责：

- 按 `algo_code + version constraint + engine context` 解析可用版本
- 返回包坐标和下载信息
- 返回入口点
- 返回 schema 和兼容性
- 对禁用或不兼容版本进行拦截

## 6. 核心领域模型

### 6.1 `Algorithm`

表示一个稳定的算子资产。

建议字段：

- `algo_code`
- `name`
- `category`
- `tags`
- `owner`
- `description`
- `status`

### 6.2 `AlgorithmVersion`

表示算子的具体版本实例，是治理核心。

建议字段：

- `algo_code`
- `version`
- `release_notes`
- `lifecycle_state`
- `published_at`
- `created_by`

### 6.3 `PackageArtifact`

表示真实制品信息。

建议字段：

- `package_name`
- `package_version`
- `repository_type`
- `repository_url`
- `filename`
- `sha256`
- `build_source`

### 6.4 `RuntimeContract`

描述引擎如何接入算子。

建议字段：

- `entry_point_group`
- `entry_point_name`
- `entry_point_target`
- `interface_type`
- `parameter_schema`
- `input_schema`
- `output_schema`
- `example_config`

### 6.5 `Compatibility`

描述运行兼容关系。

建议字段：

- `engine_type`
- `engine_version_range`
- `python_version_range`
- `os`
- `arch`
- `sdk_version_range`

### 6.6 `AuditLog`

记录关键变更。

建议字段：

- `resource_type`
- `resource_id`
- `action`
- `operator`
- `before`
- `after`
- `created_at`

## 7. 生命周期状态机

建议 `AlgorithmVersion` 使用如下状态：

- `Draft`
- `Registered`
- `Verified`
- `Published`
- `Deprecated`
- `Disabled`

状态含义：

- `Draft`：仅完成部分录入，不可展示，不可执行
- `Registered`：已登记元数据和包坐标，但尚未完成完整校验
- `Verified`：已通过包存在性、入口点、schema、兼容性等校验
- `Published`：正式对目录可见，且允许被引擎解析
- `Deprecated`：历史版本保留展示，但默认不推荐新任务使用
- `Disabled`：强制下线，引擎不可再使用

治理原则：

- `Published` 是唯一默认可执行状态
- 版本不可变，不允许同版本覆盖发布
- 生产 DAG 不应依赖 `latest`
- `Disabled` 必须对引擎硬拒绝

## 8. 关键数据流

### 8.1 开发与打包

开发者基于 SDK 创建算法包，补充：

- 元数据
- 入口点
- 参数 schema
- 输入输出 schema
- 兼容性声明

CI 执行单测、契约校验、打包。

### 8.2 发布到私有 PyPI

CI 将 wheel 发布到私有 PyPI，并记录：

- `package_name`
- `package_version`
- `repository_url`
- `sha256`

到这一步只说明“包存在”，不说明“平台可用”。

### 8.3 注册中心登记

CI 或发布工具调用注册中心登记版本，提交：

- 算子基础信息
- 包坐标
- 入口点
- schema
- 兼容性声明
- 发布说明

注册中心完成：

- 唯一性校验
- 元数据完整性校验
- 版本重复校验
- 包坐标可解析校验
- 契约结构校验

### 8.4 目录展示

目录服务同步或查询注册中心，仅展示 `Published` 状态版本。

### 8.5 引擎解析与接入

引擎在解析 DAG 中的算子节点时，调用引擎接入 API，传入：

- `algo_code`
- `version` 或版本约束
- `engine_type`
- `engine_version`
- `python_version`

引擎接入 API 返回：

- 最终命中版本
- 包名和版本
- 仓库地址
- 文件校验值
- 入口点
- schema
- 兼容性判定

随后引擎再从私有 PyPI 拉包并完成本地注册。

## 9. 推荐 API 边界

### 9.1 注册中心 API

- `POST /algorithms`
- `GET /algorithms/{algo_code}`
- `POST /algorithms/{algo_code}/versions`
- `GET /algorithms/{algo_code}/versions/{version}`
- `POST /algorithms/{algo_code}/versions/{version}/verify`
- `POST /algorithms/{algo_code}/versions/{version}/publish`
- `POST /algorithms/{algo_code}/versions/{version}/deprecate`
- `POST /algorithms/{algo_code}/versions/{version}/disable`

### 9.2 目录服务 API

- `GET /catalog/algorithms`
- `GET /catalog/algorithms/{algo_code}`
- `GET /catalog/algorithms/{algo_code}/versions`
- `GET /catalog/algorithms/{algo_code}/versions/{version}`

### 9.3 引擎接入 API

- `POST /engine/resolve`
- `POST /engine/compatibility/check`
- `GET /engine/algorithms/{algo_code}/versions`

## 10. 异常处理与治理规则

### 10.1 包已存在但注册失败

结果：

- 私有 PyPI 中存在制品
- 注册中心不承认其为正式平台资产
- 目录不展示
- 引擎不可解析

### 10.2 注册成功但包不可拉取

处理：

- 注册时校验或后台探测失败
- 禁止进入 `Published`
- 已发布版本自动告警并禁止继续解析

### 10.3 契约不合法

例如：

- 入口点不存在
- schema 缺失
- 元数据字段不完整

处理：

- 保留在 `Registered`
- 不允许发布

### 10.4 引擎上下文不兼容

例如：

- Flink 版本不支持
- Python 版本不满足要求

处理：

- `resolve` 直接返回不兼容错误
- 不返回降级后的模糊结果

## 11. 推荐代码仓结构

建议逻辑上至少拆成以下部分：

```text
algorithm_repository/
  docs/
    plans/
  sdk/
    algorithm_sdk/
  algorithms/
    algo_missing_value/
    algo_xxx/
  services/
    registry_service/
    catalog_service/
    resolve_service/
  tools/
    scaffold/
    publish_cli/
```

说明：

- `sdk/`：统一算子契约
- `algorithms/`：多算法包源码
- `services/`：注册中心、目录服务、引擎接入 API
- `tools/`：脚手架、发布和校验工具

第一阶段可以是一个仓库内多个模块，后续再根据需要拆仓或拆服务。

## 12. 分阶段演进建议

### 12.1 第一阶段

- 多算法包规范
- 算法 SDK
- 私有 PyPI 对接
- 注册中心
- 目录服务
- 引擎接入 API

### 12.2 第二阶段

- 审批流
- 自动兼容性校验
- 审计查询
- 目录增强检索
- 告警和健康探测

### 12.3 第三阶段

- 多语言算子扩展
- 多制品仓支持
- 多环境发布策略
- 权限和多租户治理

## 13. 结论

本设计建议将当前项目定位为：

**面向 Python 算子的资产控制平面。**

它负责标准化开发、元数据治理、目录展示和引擎接入解析，但不直接承担算法执行。

在该定位下：

- 私有 PyPI 是分发层
- 注册中心是资产治理层
- 目录服务是展示层
- 引擎接入 API 是引擎桥接层

这四者协同后，才能支撑“可开发、可注册、可展示、可接入、可扩展”的 Python 算子资产体系。

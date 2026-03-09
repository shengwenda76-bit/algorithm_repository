# 算法平台设计文档（草案）

日期：2026-03-05
状态：已在 brainstorming 评审中确认
范围：建设一个与业务平台联动的算法平台。业务平台负责可视化流程编排，算法平台负责异步执行完整流程。

## 1. 已确认约束

- 联动模式：异步提交 + 回调/轮询。
- 执行模型：算法平台内置执行（当前阶段不采用“每算法独立容器”）。
- 输入输出定义：在算法平台手工注册 JSON Schema，并进行版本化管理。
- 流程编排归属：业务平台。
- 运行时归属：业务平台一次性提交完整 DSL，算法平台负责全流程编排与执行。
- 规模目标（一期）：小规模，并发流程实例少于 50。
- 失败策略：快速失败；任一节点失败则整条流程失败；支持手工重试整条流程。

## 2. 架构选型

选定方案：模块化单体 + 任务队列抽象。

原因：
- 能满足一期交付速度。
- 模块边界清晰，便于后续拆分。
- 天然适配异步执行与回调/轮询。
- 运维复杂度低于微服务方案。

已评估替代方案：
- 纯单体直连执行：启动快，但后续演进路径较弱。
- 全微服务 + MQ：扩展性强，但对当前范围属于过度设计。

## 3. 系统边界

业务平台职责：
- 可视化流程编排与编辑。
- 构建并提交 Flow DSL。 
- 接收回调和/或轮询执行状态。

算法平台职责：
- 算法库与版本管理。
- 输入/输出 JSON Schema 版本管理。
- DSL 校验与 DAG 编排。
- 节点执行、运行态持久化、日志、回调。

## 4. 核心组件

- Algorithm Registry（算法注册中心）
  - 存储算法元数据、版本、入口点、Schema。
- DSL Validator（DSL 校验器）
  - 校验 Schema、依赖图、节点引用、映射规则。
- Orchestrator（编排器）
  - DAG 拓扑调度与执行状态机。
- Executor（执行器）
  - 执行内置算法入口，统一超时与错误归一化。
- Task Store（任务存储）
  - 持久化流程/节点运行状态、快照、错误信息。
- Callback/Query API（回调与查询接口）
  - 向业务平台推送完成事件，并提供轮询接口。

## 5. 运行时数据流

1. 业务平台调用 `POST /v1/executions`，提交 Flow DSL + run_context。
2. 算法平台校验 DSL 及算法版本引用。
3. 校验通过后，创建 `execution_id` 并立即返回。
4. 编排器解析就绪节点并投递执行任务。
5. Worker 执行节点并持久化节点输出快照。
6. 首个节点失败时：节点置为 `FAILED`，流程置为 `FAILED`，停止下游调度。
7. 流程结束（`SUCCEEDED` 或 `FAILED`）后发送回调；轮询查询持续可用。

## 6. 对外 API 契约（算法平台）

- `GET /v1/algorithms`
  - 按分类/状态/最新版本返回算法列表。
- `GET /v1/algorithms/{algo_code}/versions/{version}`
  - 返回 `input_schema`、`output_schema` 与运行默认配置。
- `POST /v1/executions`
  - 提交完整 Flow DSL；返回 `execution_id` 与初始状态。
- `GET /v1/executions/{execution_id}`
  - 返回流程级状态与摘要。
- `GET /v1/executions/{execution_id}/nodes`
  - 返回节点级状态与快照摘要。
- `POST /v1/executions/{execution_id}/retry`
  - 手工重试整条流程。

业务平台回调端点：
- `POST <business_callback_url>`
  - 回调签名载荷，包含 `execution_id`、最终状态、摘要、时间戳。

## 7. Flow DSL 最小结构

- `meta`
  - `flow_code`、`flow_version`、`trace_id`、`callback_url`。
- `nodes[]`
  - `node_id`、`algo_code`、`algo_version`、`params`、`timeout_sec`。
- `edges[]`
  - `from_node`、`to_node`、`mapping_rules`。
- `inputs`
  - 本次运行初始数据引用或内联参数。

## 8. 数据模型（一期）

- `algorithm_def`
  - `algo_code`、`name`、`category`、`owner`、`status`。
- `algorithm_version`
  - `algo_code`、`version`、`input_schema_json`、`output_schema_json`、`entrypoint`、`default_timeout_sec`、`is_active`。
- `execution`
  - `execution_id`、`flow_code`、`flow_version`、`status`、`dsl_snapshot_json`、`run_context_json`、`started_at`、`ended_at`、`error_summary`。
- `execution_node`
  - `execution_id`、`node_id`、`algo_code`、`algo_version`、`status`、`input_snapshot_json`、`output_snapshot_json`、`started_at`、`ended_at`、`error_detail`。
- `execution_event`（建议）
  - 追加写入的生命周期与状态迁移事件。

## 9. 错误处理与可靠性

- 校验期错误：返回 `400`，并提供机器可读错误码。
- 运行期节点错误：统一错误类型并记录堆栈。
- 超时：转换为 `TIMEOUT` 错误并使流程失败。
- 回调失败：异步重试（例如指数退避重试 3 次）。
- 幂等性：执行提交接口支持 `idempotency_key`。

## 10. 可观测性基线

- 关联追踪：`trace_id` 贯穿 API、编排、Worker、回调。
- 指标：
  - `flow_success_rate`
  - `flow_duration`
  - `node_failure_topn`
  - `callback_success_rate`
- 日志：
  - 流程生命周期日志
  - 节点输入/输出摘要日志（避免大对象全量落盘）
  - 结构化错误日志

## 11. 测试基线

- 单元测试：
  - DSL 校验器
  - DAG 拓扑调度
  - 参数映射解析
  - 状态迁移
- 集成测试：
  - 全成功路径
  - 中间节点失败 -> 快速失败
  - 回调重试路径
- 契约测试：
  - 与业务平台的回调 payload/签名校验。
- 回归样例：
  - 缺失值处理 -> 异常检测 -> 标准化。

## 12. 一期非目标

- 不支持双端流程定义的双真相源。
- 不引入补偿/跳过/降级策略。
- 暂不建设高并发分布式调度能力。

## 13. 演进路径

- 将进程内队列抽象替换为 MQ，尽量不改 API 契约。
- 当并发目标提升时，将 Executor 与 Orchestrator 拆分为独立服务。
- 一期稳定后再引入高级失败策略。

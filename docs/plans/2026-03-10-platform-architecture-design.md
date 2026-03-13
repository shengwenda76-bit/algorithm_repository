# H平台基座与算法库系统架构设计与交互方案

**Date**: 2026-03-10
**Status**: Approved

## 1. 架构总览与路线选择

在方案选择阶段，我们对比了两种架构路线。最终基于技术栈吻合度和高开发效率，选择采用 **方案 A: 原生微服务 (FastAPI + Celery + Redis/MQ)**。

### 路线对比

#### 方案 A（当前采用）：原生微服务 + Celery/Redis
*   **架构形态**：使用 FastAPI 作为算法库网关，Celery 作为任务调度与并行执行框架。
*   **优点**：
    *   **开发效率极高**：Python 生态中最成熟的异步方案。
    *   **DAG天然支持**：Celery 自身提供的 `chain`, `chord`, `group` 等 Canvas 原语完美契合 DAG 的执行逻辑。
*   **缺点**：
    *   运行环境隔离较弱。若不同算法依赖存在强烈冲突，管理单一环境的 Celery Worker 较为困难。

#### 方案 B（备选）：云原生 K8s Job + Argo Workflow
*   **架构形态**：算法层接收到 DAG 后翻译为 Kubernetes 的 Argo 工作流 YAML，经由 K8s 动态起停 Pod 来执行不同节点的算子计算。
*   **优点**：绝对的计算环境容器级隔离，支持庞大且异构的算力分配。
*   **缺点**：技术和运维门槛极高，K8s 调度有秒级冷启动延迟。

---

## 2. 系统组件边界与职责划分

基于“**基座重、算法引擎轻**”的原则，系统做如下划分：

### 2.1 H平台基座 (Base Platform / 控制流核心)
*   **核心动作**：
    *   提供可视化的算法连线编排界面。
    *   **持有图的完整寿命**：用户画完的完整结构图被保存在基座数据库。执行时，基座负责将完整的结构解析为 DAG JSON 协议发给执行引擎。
    *   监听状态机的事件消息队列（RabbitMQ/Kafka），并将最新计算进度、结果数据链接通过 WebSocket 推送给前端页面。

### 2.2 算法处理接口层 (FastAPI / 调度入口)
*   **职责**：算法库对外的唯一业务桥梁。
*   **核心动作**：
    *   暴露 `GET /schemas` 路由，将算子的输入输出规范（Pydantic Schema）动态下发给基座。
    *   接收 `POST /execute` 路由传递的执行 Payload（包含 Nodes 与 Edges），进行基本校验后拆解结构为 Celery Task 拓扑链。
    *   **绝不在此层执行任何 CPU 密集计算**，将任务推入 Broker 后即刻返回 202 异步响应码。

### 2.3 算法计算执行层 (Celery Workers / 算力承载)
*   **职责**：实际干粗重计算活的后台节点集群。
*   **核心动作**：
    *   分布式、无状态运行。
    *   根据分配到的任务标识加载实际算子代码。
    *   **大文件流转**：通过上游传来的 MinIO `s3://` 链接，去对象存储下载数据作为输入；计算完毕后将宽表、模型等上传回 MinIO 保存。基座和引擎间**坚决不通过业务接口直传文件二进制流**。
    *   算子执行启停或报错时，将状态流转及最终结果对象的 URI 包装为事件推送到消息队列（MQ）回传给基座。

---

## 3. 核心数据流转协议

### 3.1 算法元数据动态加载 (同步)
基座调用 `GET /api/v1/algorithms/registry` 获取算子的渲染必须信息。
```json
// Example Response Schema
{
  "category": "ts_preprocessing",
  "algorithms": [
    {
      "name": "linear_interp",
      "display_name": "线性插值",
      "schema": {
        "properties": { "limit": {"type": "integer", "default": null} }
      }
    }
  ]
}
```

### 3.2 任务派发与数据依赖定义 (异步)
为了标识节点间的数据依赖，在 Payload 中采用 `$ref`（Reference）机制。
*   **URL**: `POST /api/v1/workflows/execute`
*   **Payload Example**:
```json
{
  "workflow_id": "wf-1001",
  "nodes": [
    {
       "node_id": "node-1",
       "algorithm_name": "ts_preprocessing.linear_interp",
       "inputs": {"data_uri": "s3://tenant-A/raw/data.csv"}
    },
    {
       "node_id": "node-2",
       "algorithm_name": "feature_extraction.tsfresh",
       "inputs": {
          // 这里标识 node-2 强依赖 node-1 的输出内容
          "data_uri": {"$ref": "node-1.outputs.result_uri"}
       }
    }
  ],
  "edges": [
     {"source": "node-1", "target": "node-2"}
  ]
}
```

### 3.3 进度状态事件回传 (MQ)
*   **通知渠道**：RabbitMQ 等中间件。
*   **消息体格式**：
```json
{
   "event_type": "NODE_COMPLETED",   // NODE_STARTED, NODE_FAILED 等
   "run_id": "wf-1001",
   "node_id": "node-1",
   "status": "SUCCESS",
   "outputs": {"result_uri": "s3://tenant-A/intermedia/node-1-result.parquet"},
   "error_message": null
}
```

---

## 4. 目录结构与部署建议

### 4.1 代码结构组织

```text
algorithm_repository/
├── app/
│   ├── api/            # FastAPI 核心网关控制层
│   ├── core/           # 服务基础设施如 MinIO, Celery App Init
│   ├── services/       # 业务服务层（负责 DAG JSON 翻译为 Celery Chain）
│   ├── algorithms/     # 统一算法实装层
│   │   ├── base.py     # 引擎运行时基类与约束
│   │   ├── registry.py # 算子 Schema 动态导出与自动装配机制
│   │   └── ts_preprocessing/
│   │       ├── linear_interp.py
│   │       └── ffill.py
│   └── worker/         # Celery 工作进程的任务统一入口层
├── tests/              
└── docker-compose.yml  # 提供快速的本地服务堆栈
```

### 4.2 集群组件伸缩建议
*   **API Gateway**: 部署 2+ 实例即可支撑正常流量。
*   **Celery Workers**: 根据负载水平横向伸缩 N 个实例。且支持配置针对高耗能算法的专属高配 `Queue` 队列实例绑定。

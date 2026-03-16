"""节点执行任务。"""

from __future__ import annotations

from app.schemas.execution import NodeExecutionResult
from app.schemas.flow_dsl import FlowNode
from app.services.algorithm_loader import algorithm_loader


def execute_node(node: FlowNode) -> NodeExecutionResult:
    """执行单个节点，并在需要时动态加载算法。"""

    try:
        # 执行前确保算法已注册；如果本地缺失，会触发解析、下载和导入。
        loaded = algorithm_loader.ensure_loaded(node.algo_code, node.algo_version)
        algorithm = loaded.algorithm_cls()
        outputs = algorithm.execute(inputs=node.inputs, params=node.params)
        return NodeExecutionResult(
            node_id=node.node_id,
            algo_code=node.algo_code,
            algo_version=node.algo_version,
            status="SUCCEEDED",
            outputs=outputs,
            source=loaded.source,
        )
    except Exception as exc:
        # 骨架阶段统一将异常折叠到节点结果中，便于上层编排器处理。
        return NodeExecutionResult(
            node_id=node.node_id,
            algo_code=node.algo_code,
            algo_version=node.algo_version,
            status="FAILED",
            error=str(exc),
        )

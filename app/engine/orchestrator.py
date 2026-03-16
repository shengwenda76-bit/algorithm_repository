"""最小串行编排器。"""

from __future__ import annotations

from app.engine.tasks import execute_node
from app.schemas.execution import ExecutionResult, NodeExecutionResult
from app.schemas.flow_dsl import FlowDSL, FlowNode


class Orchestrator:
    """按节点声明顺序同步编排执行。"""

    def start_execution(self, execution_id: str, flow: FlowDSL) -> ExecutionResult:
        """按顺序执行全部节点，遇到失败立即停止。"""

        node_results: list[NodeExecutionResult] = []
        completed_status: dict[str, str] = {}

        for node in flow.nodes:
            if not self._dependencies_satisfied(node, completed_status):
                # 依赖未满足时直接跳过当前节点，并结束本次执行。
                result = NodeExecutionResult(
                    node_id=node.node_id,
                    algo_code=node.algo_code,
                    algo_version=node.algo_version,
                    status="SKIPPED",
                    error="Dependencies not satisfied",
                )
                node_results.append(result)
                completed_status[node.node_id] = result.status
                return ExecutionResult(
                    execution_id=execution_id,
                    status="FAILED",
                    node_results=node_results,
                )

            # 当前骨架仍然采用同步逐节点执行，后续可替换为 Celery 调度。
            result = execute_node(node)
            node_results.append(result)
            completed_status[node.node_id] = result.status
            if result.status != "SUCCEEDED":
                return ExecutionResult(
                    execution_id=execution_id,
                    status="FAILED",
                    node_results=node_results,
                )

        return ExecutionResult(
            execution_id=execution_id,
            status="SUCCEEDED",
            node_results=node_results,
        )

    @staticmethod
    def _dependencies_satisfied(node: FlowNode, completed_status: dict[str, str]) -> bool:
        """检查当前节点的前置依赖是否全部成功。"""

        return all(completed_status.get(dependency) == "SUCCEEDED" for dependency in node.depends_on)


orchestrator = Orchestrator()

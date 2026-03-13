from typing import List, Dict, Set, Optional
from collections import deque, defaultdict
import logging

from app.schemas.flow_dsl import FlowDSL
from app.algorithms.registry import AlgorithmRegistry

logger = logging.getLogger(__name__)

class DAGNode:
    def __init__(self, node_id: str, algo_code: str, algo_version: str, params: dict, timeout_sec: int):
        self.node_id = node_id
        self.algo_code = algo_code
        self.algo_version = algo_version
        self.params = params
        self.timeout_sec = timeout_sec
        self.dependencies: Set[str] = set()
        self.successors: Set[str] = set()
        self.execution_mode = "celery_task"
        
        # 尝试从注册表获取真实执行模式
        try:
            algo_cls = AlgorithmRegistry.get(algo_code, algo_version)
            self.execution_mode = getattr(algo_cls.meta, "execution_mode", "celery_task")
        except Exception:
            # 如果暂未注册（比如平台校验阶段容错），默认作为独立任务
            pass

class BundleNode(DAGNode):
    """一个包含连续 In-Memory 节点的复合执行节点"""
    def __init__(self, bundled_node_ids: List[str], timeout_sec: int):
        # 使用一个特殊格式的 node_id，表明是 Bundle
        node_id = f"bundle_{'_'.join(bundled_node_ids)}"
        super().__init__(node_id, "SYSTEM_BUNDLE", "1.0", {}, timeout_sec)
        self.bundled_node_ids = bundled_node_ids
        self.execution_mode = "bundled_in_memory"

class DAG:
    """有向无环图，负责解析 DSL、拓扑排序和智能打包合并"""
    def __init__(self, dsl: FlowDSL):
        self.dsl = dsl
        self.nodes: Dict[str, DAGNode] = {}
        self.edges: List[dict] = []
        self._build_graph()

    def _build_graph(self):
        # 1. 实例化所有节点
        for n in self.dsl.nodes:
            node = DAGNode(
                node_id=n.node_id,
                algo_code=n.algo_code,
                algo_version=n.algo_version,
                params=n.default_params,
                timeout_sec=n.timeout_sec
            )
            self.nodes[n.node_id] = node

        # 2. 构建边关系
        for edge in self.dsl.edges:
            self.edges.append({
                "from_node": edge.from_node,
                "to_node": edge.to_node,
                "mapping_rules": [
                    {"from": m.from_path, "to": m.to_path} for m in edge.mapping_rules
                ]
            })
            if edge.from_node in self.nodes and edge.to_node in self.nodes:
                self.nodes[edge.from_node].successors.add(edge.to_node)
                self.nodes[edge.to_node].dependencies.add(edge.from_node)

    def validate_no_cycle(self) -> bool:
        """Kahn 算法检测环"""
        in_degree = {n_id: len(node.dependencies) for n_id, node in self.nodes.items()}
        queue = deque([n_id for n_id, deg in in_degree.items() if deg == 0])
        count = 0

        while queue:
            curr = queue.popleft()
            count += 1
            for succ in self.nodes[curr].successors:
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        return count == len(self.nodes)

    def optimize_and_bundle(self) -> Dict[str, DAGNode]:
        """
        [智能打包压缩]
        在图中寻找严格 1-to-1 串行的 in_memory 节点，将其合并为 BundleNode。
        返回一个新的打完包的 nodes 字典。
        """
        # 为了不破坏原有结构，创建一个复制的版本进行替换
        new_nodes = self.nodes.copy()
        merged_groups = []
        
        # 使用不相交集合或简单的链表合并算法（因为是严格 1对1，链路必定是没有分叉的线性表）
        # Rule: X 必须只有1个后继Y, Y 必须只有1个前驱X, 且 X Y 都是 in_memory
        
        visited = set()
        for node_id, node in self.nodes.items():
            if node_id in visited:
                continue
                
            # 找到链的起点
            current = node
            chain = [current]
            visited.add(current.node_id)
            
            while True:
                if current.execution_mode != "in_memory":
                    break
                    
                # 如果当前节点且仅有 1 个后继
                if len(current.successors) == 1:
                    succ_id = list(current.successors)[0]
                    succ_node = self.nodes[succ_id]
                    # 那个后继也仅有 1 个前驱，并且也是 in_memory
                    if len(succ_node.dependencies) == 1 and succ_node.execution_mode == "in_memory":
                        chain.append(succ_node)
                        visited.add(succ_id)
                        current = succ_node
                    else:
                        break
                else:
                    break
                    
            if len(chain) > 1:
                merged_groups.append(chain)

        # 生成 BundleNode 替代原来链条上的节点
        # 并修正依赖关系
        bundle_map = {} # 旧 node_id 对应的新的 Bundle_id
        
        for chain in merged_groups:
            bundled_ids = [n.node_id for n in chain]
            total_timeout = sum(n.timeout_sec for n in chain)
            
            bundle = BundleNode(bundled_ids, total_timeout)
            
            # Bundle 的前驱 = 链首元素的前驱
            bundle.dependencies = set(chain[0].dependencies)
            # Bundle 的后继 = 链尾元素的后继
            bundle.successors = set(chain[-1].successors)
            
            new_nodes[bundle.node_id] = bundle
            
            for n in chain:
                bundle_map[n.node_id] = bundle.node_id
                del new_nodes[n.node_id]

        # 修正剩余节点的前驱和后继引用
        for new_node in new_nodes.values():
            new_node.dependencies = {bundle_map.get(dep, dep) for dep in new_node.dependencies}
            new_node.successors = {bundle_map.get(suc, suc) for suc in new_node.successors}

        logger.info(f"[智能打包] 原始 {len(self.nodes)} 节点, 现合并产生 {len(merged_groups)} 个压缩任务组, 汇总共 {len(new_nodes)} 个下发图节点.")
        return new_nodes

    def topological_sort(self, use_optimization: bool = True) -> List[List[DAGNode]]:
        """
        拓扑排序，返回按层分组的节点集合。
        每层（内部的 List）内的节点相互独立，可以完全并行执行。
        
        use_optimization: 是否应用 in_memory 自动压缩
        """
        nodes_ref = self.optimize_and_bundle() if use_optimization else self.nodes
        
        in_degree = {n_id: len(node.dependencies) for n_id, node in nodes_ref.items()}
        queue = deque([n_id for n_id, deg in in_degree.items() if deg == 0])
        
        layers = []
        while queue:
            level_size = len(queue)
            current_layer = []
            for _ in range(level_size):
                curr = queue.popleft()
                current_layer.append(nodes_ref[curr])
                for succ in nodes_ref[curr].successors:
                    in_degree[succ] -= 1
                    if in_degree[succ] == 0:
                        queue.append(succ)
            
            layers.append(current_layer)
            
        return layers

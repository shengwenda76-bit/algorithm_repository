import logging
from typing import List, Dict, Any

# from celery import shared_task
from app.algorithms.registry import AlgorithmRegistry

logger = logging.getLogger(__name__)

# @shared_task(bind=True)
def execute_single_node(self, execution_id: str, node_id: str, algo_code: str, algo_version: str, params: dict, input_data: dict):
    """
    [纯净的单节点 Celery Worker 任务]
    负责：
    1. 执行前，从 MinIO 下载所需的 input_data.dataset_ref(s) 到内存或本地文件/Dataset
    2. 加载算子实例
    3. 执行算子
    4. 执行后，如果算子处于 "celery_task" 长时模式并产生落盘数据，将结果 dataset 上传到 MinIO
    """
    logger.info(f"[{execution_id}] 开始独立执行算子节点 {node_id} ({algo_code}@{algo_version})")

    algo_cls = AlgorithmRegistry.get(algo_code, algo_version)
    algo_instance = algo_cls()
    
    # === 开始前：IO 预处理 ===
    # 将 minio://xxx 转换为 df 或者本地路径
    # materialized_inputs = StorageService.download_inputs(input_data)
    materialized_inputs = input_data

    # === 校验并执行业务逻辑 ===
    algo_instance.validate_params(params)
    output_result = algo_instance.execute(params, materialized_inputs)

    # === 执行后：IO 回传 ===
    # 上传内存里的 DataFrame 或 生成的文件至 MinIO
    # persisted_paths = StorageService.upload_outputs(output_result, execution_id, node_id)
    persisted_paths = output_result
    
    return persisted_paths


# @shared_task(bind=True)
def execute_bundled_nodes(self, execution_id: str, dsl_snapshot: dict, node_id_chain: List[str]):
    """
    [智能合并的多节点级联任务 (in_memory 专用)]
    这是由 Orchestrator 合并的一系列极轻量的数据处理算子构成的节点流。
    负责：
    1. ONLY ONCE: 从 MinIO 下载链条起始输入数据到内存（DF）
    2. LOOP: 轮流实例化所有的算法并在内存中击穿、透传变量 `df = A(df) -> B(df) -> C(df)`
    3. ONLY ONCE: 最终产物写入 MinIO
    4. 单独更新数据库状态供 H4 前端查询回写
    """
    bundle_name = "->".join(node_id_chain)
    logger.info(f"[{execution_id}] 开始在单实例内存中级联执行捆绑节点: {bundle_name}")

    # 获取链条第一个节点的输入参数配置，并物化其输入
    first_node_id = node_id_chain[0]
    first_node_def = _get_node_from_dsl(dsl_snapshot, first_node_id)
    
    # materialized_inputs = StorageService.download_inputs(first_node_def.input_data)
    current_payload = {"dataset_ref": "memory_df"} # mock materialized inputs

    for idx, sub_node_id in enumerate(node_id_chain):
        node_def = _get_node_from_dsl(dsl_snapshot, sub_node_id)
        
        algo_cls = AlgorithmRegistry.get(node_def["algo_code"], node_def["algo_version"])
        algo_instance = algo_cls()

        params = node_def["params"]

        logger.info(f"  -> [{execution_id}] 瞬发执行内部算子 {sub_node_id} ...")
        algo_instance.validate_params(params)
        
        # 链式输入传递, 直接无盘化通过内存覆盖
        current_payload = algo_instance.execute(params, current_payload)
        
        # 可选：如果前端希望看每个子节点精确的状态，可以在这通知 DB 更新 sub_node_id 为 SUCCEEDED。
        # 由于都在一个容器内，非常迅速。

    # === 最后一次 IO 上传 ===
    last_node_id = node_id_chain[-1]
    # persisted_paths = StorageService.upload_outputs(current_payload, execution_id, last_node_id)
    persisted_paths = {"dataset_ref": "minio://resolved.parquet"}
    
    logger.info(f"[{execution_id}] 组合链 {bundle_name} 高速执行完毕，仅产生一次网络IO")
    return persisted_paths

def _get_node_from_dsl(dsl: dict, node_id: str) -> dict:
    """工具函数"""
    return {
        "algo_code": "mock",
        "algo_version": "1.0",
        "params": {},
        "input_data": {}
    }

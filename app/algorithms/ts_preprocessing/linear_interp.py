import logging
from typing import Dict, Any
from app.algorithms.base import BaseAlgorithm, AlgorithmMeta
from app.algorithms.registry import AlgorithmRegistry

logger = logging.getLogger(__name__)

# 1. 定义该算法的元数据，用于描述版本、输入输出结构等
_META = AlgorithmMeta(
    algo_code="ts_clean_linear_interp",
    name="线性插值填充",
    category="ts_preprocessing",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "dataset_ref": {"type": "string", "description": "输入的数据集MinIO路径"}
        },
        "required": ["dataset_ref"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "dataset_ref": {"type": "string", "description": "处理后产出的数据集MinIO路径"}
        },
        "required": ["dataset_ref"]
    },
    default_timeout_sec=120
)

# 2. 使用装饰器自动注册到 AlgorithmRegistry 中
@AlgorithmRegistry.register
class LinearInterpolationAlgorithm(BaseAlgorithm):
    """
    具体的算法类实现：时序数据预处理 - 线性插值
    """
    meta = _META  # 绑定元数据

    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        3. （可选）执行前的特定传参校验
        """
        # 例如: 验证是否传入了合法的 max_gap 间隔要求
        if "max_gap" in params and not isinstance(params["max_gap"], int):
            raise ValueError("配置参数 'max_gap' 必须是一个整数(integer)类型。")
        if "max_gap" in params and params["max_gap"] < 0:
            raise ValueError("配置参数 'max_gap' 必须是自然数。")

    def execute(self, params: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        4. 算法核心执行逻辑
        """
        input_dataset_ref = inputs.get("dataset_ref")
        max_gap = params.get("max_gap", 0)  # 从流程编排中传来的参数
        
        logger.info(f"[{self.meta.algo_code}] 开始处理。源数据集: {input_dataset_ref}, 参数 max_gap={max_gap}")
        
        # -------------------------------------------------------------
        # ✅ 这里存放团队成员的核心算法开发逻辑：
        # 1. 下载输入依赖数据
        #    local_in_path = storage_service.download(input_dataset_ref)
        # 2. 本地执行或加载到内存数据帧计算 (如 Pandas 处理)
        #    df = pd.read_csv(local_in_path)
        #    df = df.interpolate(method='linear', limit=max_gap if max_gap > 0 else None)
        # 3. 输出并保存产出结果
        #    local_out_path = f"/data/algorithm_cache/processed_{execution_id}.csv"
        #    df.to_csv(local_out_path, index=False)
        # 4. 回传至对象存储
        #    output_dataset_ref = storage_service.upload(local_out_path, ...)
        # -------------------------------------------------------------
        
        # 为演示目的，我们模拟生成路径：
        output_dataset_ref = f"{input_dataset_ref}_linear_interpolated"
        logger.info(f"[{self.meta.algo_code}] 处理完成！产出数据集: {output_dataset_ref}")
        
        # 必须返回满足 output_schema 定义的字典
        return {
            "dataset_ref": output_dataset_ref
        }

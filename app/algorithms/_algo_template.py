"""
【开发人员必看】算法开发与接入模板

1. 请先根据需求，在 `app/algorithms/` 下寻找合适的分类目录（如未包含可以新建类别目录，比如 `ts_anomaly`）。
2. 在类别目录下新建你的算法 Python 文件，**直接复制本模板的内容进行修改**。
3. 系统会在启动时自动扫描 `app/algorithms` 的所有子包并进行注册，无需在其他地方改动导入列表。
"""

import logging
from typing import Dict, Any

# 重要: 这两个基类需要被引入
from app.algorithms.base import BaseAlgorithm, AlgorithmMeta
from app.algorithms.registry import AlgorithmRegistry

logger = logging.getLogger(__name__)

# ==========================================================
# 步骤 1：定义你的算法模型基础元数据集参数（即流程图上看到的约束）
# ==========================================================
_META = AlgorithmMeta(
    algo_code="YOUR_ALGORITHM_UNIQUE_CODE",  # 形如 'ts_feat_mean', 'txt_rank_bm25'
    name="在这里写算法对外展示的中文名称",       # 形如 '均值提取'
    category="YOUR_CATEGORY",                # 务必与外层目录业务类别对应, e.g. 'ts_feature'
    version="1.0.0",                         # 标准的三位序列版本号
    
    # 输入与输出遵循 JSON Schema 草案规范
    input_schema={
        "type": "object",
        "properties": {
            "dataset_ref": {"type": "string", "description": "MinIO数据集路径，必填"}
            # 可按需补充接收如模型引用（model_ref）等
        },
        "required": ["dataset_ref"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "dataset_ref": {"type": "string", "description": "处理后产出的MinIO数据集路径"}
        },
        "required": ["dataset_ref"]
    },
    default_timeout_sec=60                   # 平台的默认容忍超时执行时间
)

# ==========================================================
# 步骤 2：正式建立你的算法对象，通过注册器 @AlgorithmRegistry.register 暴露
# ==========================================================
@AlgorithmRegistry.register
class MyCustomAlgorithmTemplate(BaseAlgorithm):
    """
    修改此类的名称为具备特征的英文业务命名，例如 MeanFeatureAlgorithm 
    """
    # 强制绑定步骤 1 的元数据声明
    meta = _META

    # ==========================================================
    # 步骤 3（可选）：安全传参校验。用于保护由于图形连线传入给节点的“用户可配置参数 params”。
    # ==========================================================
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        如果不合法，或者缺少必备的入参，应当主动抛出异常阻断后续运行
        """
        # 示例:
        # if "threshold" not in params:
        #     raise ValueError("必须给定阈值 threshold")
        # if params["threshold"] < 0:
        #     raise ValueError("threshold 不能是负数或者非法数据")
        pass

    # ==========================================================
    # 步骤 4（必填）：实际代码业务与计算的地方
    # ==========================================================
    def execute(self, params: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行环节
        
        Args:
            params: 你的 validate_params 方法校验后的执行参数（来自画图画布上的右侧参数配置表单）。
            inputs: 上游所有产生的数据节点组装后的路径或其他数据源结果，通过 input_schema 校验拿到。
            
        Returns:
            Dict[str, Any]: 当前节点的任务输出，通常必须产出 output_schema 要求的标准格式
        """
        dataset_ref = inputs.get("dataset_ref")
        
        logger.info(f"[{self.meta.algo_code}] 正在执行算法任务, 处理数据: {dataset_ref}")
        
        # 🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
        # ==================== 开始写你的处理逻辑 ====================
        # (通常涵盖: storage_service 下载 -> CPU/GPU 处理 -> storage_service 上传记录结果)
        
        result_dataset_ref = dataset_ref + "_done"
        
        # ==================== 结束你的处理逻辑 ====================
        # 🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
        
        logger.info(f"[{self.meta.algo_code}] 处理流转完成, 下发结果: {result_dataset_ref}")
        
        return {
            "dataset_ref": result_dataset_ref
        }

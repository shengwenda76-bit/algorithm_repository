"""
缺失值处理算子
分类：数据清洗
执行模式：in_memory（轻量级，可被 Orchestrator 内存打包合并执行）
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import logging
from app.algorithms.base import BaseAlgorithm, AlgorithmMeta
from app.algorithms.registry import AlgorithmRegistry

logger = logging.getLogger(__name__)

_META = AlgorithmMeta(
    algo_code="missing_value",
    name="缺失值处理",
    description="对数据中的缺失值按列进行填充或删除处理",
    category="数据清洗",
    version="1.0",
    execution_mode="in_memory",
    input_schema={
        "type": "object",
        "properties": {
            "dataset_ref": {
                "type": "string",
                "description": "输入数据集引用（MinIO 路径或内存 DataFrame）"
            }
        },
        "required": ["dataset_ref"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "dataset_ref": {
                "type": "string",
                "description": "处理后的数据集引用"
            }
        }
    },
    param_schema={
        "type": "object",
        "properties": {
            "target_columns": {
                "type": "array",
                "items": {"type": "string"},
                "title": "处理属性",
                "description": "需要进行缺失值处理的列名列表，由 H4 平台根据用户上传数据自动分析并填充，支持全选"
            },
            "method": {
                "type": "string",
                "title": "缺失值处理方法",
                "options": {
                    "ffill": {"label": "前值填充", "description": "使用前一个有效值填充缺失值"},
                    "bfill": {"label": "后值填充", "description": "使用后一个有效值填充缺失值"},
                    "mean": {"label": "均值填充", "description": "使用该列的算术平均值填充缺失值"},
                    "median": {"label": "中位数填充", "description": "使用该列的中位数填充缺失值"},
                    "mode": {"label": "众数填充", "description": "使用该列出现频率最高的值填充缺失值"},
                    "constant": {"label": "指定固定值", "description": "使用用户指定的常数值填充缺失值"},
                    "drop": {"label": "删除", "description": "直接删除包含缺失值的整行数据"}
                },
                "default": "drop"
            },
            "constant_value": {
                "type": "number",
                "title": "指定值常数",
                "description": "仅当 method=constant 时有效",
                "visible_when": {"method": "constant"}
            }
        },
        "required": ["method"]
    }
)


@AlgorithmRegistry.register
class MissingValueAlgorithm(BaseAlgorithm):
    """缺失值处理算子"""
    meta = _META

    def execute(self, params: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        df: pd.DataFrame = inputs.get("dataset_ref")
        if not isinstance(df, pd.DataFrame):
            raise ValueError("[缺失值处理] 输入 dataset_ref 无效: 必须为 pandas DataFrame")

        method: str = params.get("method", "drop")
        target_cols: List[str] = params.get("target_columns", [])
        constant_value: Optional[float] = params.get("constant_value")

        # ---- 业务参数校验 ----
        missing_cols = [col for col in target_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"指定的处理列不存在于数据集中: {missing_cols}")

        if method == "constant" and constant_value is None:
            raise ValueError("由于选择了固定值填充(constant)，必须指定 constant_value 参数")

        # 如果用户未指定列（或全选），则默认处理所有列
        if not target_cols:
            target_cols = list(df.columns)

        logger.info(f"[缺失值处理] method={method}, 目标列={target_cols}")

        # ---- 执行处理 ----
        if method == "drop":
            df = df.dropna(subset=target_cols)
        elif method == "ffill":
            df[target_cols] = df[target_cols].ffill()
        elif method == "bfill":
            df[target_cols] = df[target_cols].bfill()
        elif method == "mean":
            for col in target_cols:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].mean())
        elif method == "median":
            for col in target_cols:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
        elif method == "mode":
            for col in target_cols:
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val.iloc[0])
        elif method == "constant":
            if constant_value is not None:
                df[target_cols] = df[target_cols].fillna(constant_value)
            else:
                logger.warning("[缺失值处理] method=constant 但未指定 constant_value，跳过")

        logger.info(f"[缺失值处理] 处理完成，剩余 {len(df)} 行")
        return {"dataset_ref": df}

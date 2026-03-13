"""
数据标准化算子
分类：数据处理
执行模式：in_memory（轻量级，可被 Orchestrator 内存打包合并执行）
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import logging
from app.algorithms.base import BaseAlgorithm, AlgorithmMeta
from app.algorithms.registry import AlgorithmRegistry

logger = logging.getLogger(__name__)

_META = AlgorithmMeta(
    algo_code="standardize",
    name="数据标准化",
    description="对数值型数据进行归一化、标准化或其他尺度变换",
    category="数据处理",
    version="1.0",
    execution_mode="in_memory",
    input_schema={
        "type": "object",
        "properties": {
            "dataset_ref": {
                "type": "string",
                "description": "输入数据集引用"
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
                "title": "标准化处理属性",
                "description": "需要进行标准化的列名列表，由 H4 平台根据用户上传数据自动分析并填充，支持全选"
            },
            "method": {
                "type": "string",
                "title": "标准化方法",
                "options": {
                    "minmax": {"label": "Min-Max 归一化(0~1)", "description": "将数据线性缩放到 [0, 1] 区间"},
                    "zscore": {"label": "Z-Score 标准化", "description": "将数据转换为均值为0、标准差为1的分布"},
                    "maxabs": {"label": "MaxAbs 缩放(-1~1)", "description": "按最大绝对值缩放到 [-1, 1] 区间"},
                    "robust": {"label": "Robust 鲁棒缩放", "description": "基于中位数和四分位距缩放，对异常值更鲁棒"},
                    "log": {"label": "Log 对数变换", "description": "对数据取 log(1+x)，适用于右偏分布"},
                    "custom_range": {"label": "自定义区间缩放", "description": "将数据缩放到用户自定义的 [min, max] 区间"}
                },
                "default": "minmax"
            },
            "custom_min": {
                "type": "number",
                "title": "自定义区间下限",
                "default": 0,
                "visible_when": {"method": "custom_range"}
            },
            "custom_max": {
                "type": "number",
                "title": "自定义区间上限",
                "default": 100,
                "visible_when": {"method": "custom_range"}
            }
        },
        "required": ["method"]
    }
)


@AlgorithmRegistry.register
class StandardizeAlgorithm(BaseAlgorithm):
    """数据标准化算子"""
    meta = _META

    def execute(self, params: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        df: pd.DataFrame = inputs.get("dataset_ref")
        if not isinstance(df, pd.DataFrame):
            raise ValueError("[数据标准化] 输入 dataset_ref 无效: 必须为 pandas DataFrame")

        method: str = params.get("method", "minmax")
        target_cols: List[str] = params.get("target_columns", [])
        custom_min: float = params.get("custom_min", 0)
        custom_max: float = params.get("custom_max", 100)

        # ---- 业务参数校验 ----
        missing_cols = [col for col in target_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"指定的处理列不存在于数据集中: {missing_cols}")

        if method == "custom_range" and custom_min >= custom_max:
            raise ValueError(f"自定义区间无效: custom_min({custom_min}) 必须小于 custom_max({custom_max})")

        # 默认：处理所有数值列
        if not target_cols:
            target_cols = list(df.select_dtypes(include='number').columns)

        logger.info(f"[数据标准化] method={method}, 目标列={target_cols}")

        for col in target_cols:
            col_min = df[col].min()
            col_max = df[col].max()
            col_mean = df[col].mean()
            col_std = df[col].std()
            col_range = col_max - col_min

            if method == "minmax":
                if col_range != 0:
                    df[col] = (df[col] - col_min) / col_range
                else:
                    df[col] = 0.0

            elif method == "zscore":
                if col_std != 0:
                    df[col] = (df[col] - col_mean) / col_std
                else:
                    df[col] = 0.0

            elif method == "maxabs":
                max_abs = df[col].abs().max()
                if max_abs != 0:
                    df[col] = df[col] / max_abs

            elif method == "robust":
                median_val = df[col].median()
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                if iqr != 0:
                    df[col] = (df[col] - median_val) / iqr
                else:
                    df[col] = 0.0

            elif method == "log":
                df[col] = np.log1p(df[col].clip(lower=0))

            elif method == "custom_range":
                if col_range != 0:
                    normalized = (df[col] - col_min) / col_range
                    df[col] = normalized * (custom_max - custom_min) + custom_min
                else:
                    df[col] = custom_min

        logger.info(f"[数据标准化] 处理完成，共 {len(df)} 行")
        return {"dataset_ref": df}

"""
异常值检测与处理算子
分类：数据清洗
执行模式：in_memory（轻量级，可被 Orchestrator 内存打包合并执行）
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import logging
from app.algorithms.base import BaseAlgorithm, AlgorithmMeta
from app.algorithms.registry import AlgorithmRegistry

logger = logging.getLogger(__name__)

_META = AlgorithmMeta(
    algo_code="outliers_detection",
    name="异常值检测与处理",
    description="基于统计方法检测数据中的异常值，并按用户选择的策略进行处理",
    category="数据清洗",
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
                "title": "检测属性",
                "description": "需要进行异常值检测的列名列表，由 H4 平台根据用户上传数据自动分析并填充，支持全选"
            },
            "detect_method": {
                "type": "string",
                "title": "异常值检测方法",
                "options": {
                    "zscore": {"label": "Z-Score 检验", "description": "基于标准差判定，适用于近似正态分布的数据"},
                    "iqr": {"label": "IQR 四分位距法", "description": "基于四分位距判定，对异常值更鲁棒"},
                    "grubbs": {"label": "Grubbs 检验", "description": "基于最大偏差的统计检验方法"}
                },
                "default": "zscore"
            },
            "threshold": {
                "type": "number",
                "title": "阈值",
                "description": "Z-Score/Grubbs 模式下为标准差倍数(默认3)；IQR 模式下为四分位距倍数(默认1.5)",
                "default": 3.0
            },
            "handle_method": {
                "type": "string",
                "title": "异常值处理方法",
                "options": {
                    "drop": {"label": "删除异常行", "description": "直接移除包含异常值的整行数据"},
                    "clip": {"label": "截断至边界值", "description": "将超出范围的值截断到上下边界"},
                    "mean": {"label": "均值替换", "description": "用该列均值替换异常值"},
                    "median": {"label": "中位数替换", "description": "用该列中位数替换异常值"},
                    "constant": {"label": "指定固定值替换", "description": "用用户指定的常数替换异常值"},
                    "mark": {"label": "仅标记不处理", "description": "添加标记列标识异常行，不修改原始数据"}
                },
                "default": "drop"
            },
            "constant_value": {
                "type": "number",
                "title": "指定替换值",
                "description": "仅当 handle_method=constant 时有效",
                "visible_when": {"handle_method": "constant"}
            }
        },
        "required": ["detect_method", "handle_method"]
    }
)


@AlgorithmRegistry.register
class OutliersDetectionAlgorithm(BaseAlgorithm):
    """异常值检测与处理算子"""
    meta = _META

    def execute(self, params: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        df: pd.DataFrame = inputs.get("dataset_ref")
        if not isinstance(df, pd.DataFrame):
            raise ValueError("[异常值检测] 输入 dataset_ref 无效: 必须为 pandas DataFrame")

        detect_method: str = params.get("detect_method", "zscore")
        handle_method: str = params.get("handle_method", "drop")
        threshold: float = params.get("threshold", 3.0)
        target_cols: List[str] = params.get("target_columns", [])
        constant_value: Optional[float] = params.get("constant_value")

        # ---- 业务参数校验 ----
        missing_cols = [col for col in target_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"指定的处理列不存在于数据集中: {missing_cols}")

        if handle_method == "constant" and constant_value is None:
            raise ValueError("由于选择了固定值替换(constant)，必须指定 constant_value 参数")

        # 默认：处理所有数值列
        if not target_cols:
            target_cols = list(df.select_dtypes(include='number').columns)

        logger.info(f"[异常值检测] detect={detect_method}, handle={handle_method}, "
                     f"threshold={threshold}, 目标列={target_cols}")

        # ---- Step 1: 检测异常值，生成布尔掩码 (True=异常) ----
        outlier_mask = pd.DataFrame(False, index=df.index, columns=target_cols)

        if detect_method == "zscore":
            for col in target_cols:
                mean_val = df[col].mean()
                std_val = df[col].std()
                if std_val > 0:
                    outlier_mask[col] = ((df[col] - mean_val) / std_val).abs() > threshold

        elif detect_method == "iqr":
            for col in target_cols:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                outlier_mask[col] = (df[col] < lower) | (df[col] > upper)

        elif detect_method == "grubbs":
            for col in target_cols:
                mean_val = df[col].mean()
                std_val = df[col].std()
                if std_val > 0:
                    g_stat = (df[col] - mean_val).abs() / std_val
                    outlier_mask[col] = g_stat > threshold

        total_outliers = outlier_mask.any(axis=1).sum()
        logger.info(f"[异常值检测] 共检测到 {total_outliers} 行包含异常值")

        # ---- Step 2: 按策略处理异常值 ----
        if handle_method == "drop":
            df = df[~outlier_mask.any(axis=1)]

        elif handle_method == "clip":
            for col in target_cols:
                if detect_method == "iqr":
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
                else:
                    mean_val, std_val = df[col].mean(), df[col].std()
                    lower, upper = mean_val - threshold * std_val, mean_val + threshold * std_val
                df[col] = df[col].clip(lower=lower, upper=upper)

        elif handle_method == "mean":
            for col in target_cols:
                df.loc[outlier_mask[col], col] = df[col].mean()

        elif handle_method == "median":
            for col in target_cols:
                df.loc[outlier_mask[col], col] = df[col].median()

        elif handle_method == "constant":
            if constant_value is not None:
                for col in target_cols:
                    df.loc[outlier_mask[col], col] = constant_value

        elif handle_method == "mark":
            df["_outlier_flag"] = outlier_mask.any(axis=1).astype(int)
            logger.info("[异常值检测] 仅标记模式，已添加 _outlier_flag 列")

        logger.info(f"[异常值检测] 处理完成，剩余 {len(df)} 行")
        return {"dataset_ref": df}

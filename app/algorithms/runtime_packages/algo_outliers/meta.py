"""异常值处理算法元数据。"""

from app.contracts.algorithm import AlgorithmMeta, ExecutionMode

ALGORITHM_META = AlgorithmMeta(
    algo_code="outliers",
    name="异常值处理",
    category="data_cleaning",
    version="1.0.0",
    execution_mode=ExecutionMode.IN_MEMORY,
    description="按 z-score 阈值移除异常值。",
)

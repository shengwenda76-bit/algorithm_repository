"""缺失值处理算法元数据。"""

from app.contracts.algorithm import AlgorithmMeta, ExecutionMode

ALGORITHM_META = AlgorithmMeta(
    algo_code="missing_value",
    name="缺失值处理",
    category="data_cleaning",
    version="1.0.0",
    execution_mode=ExecutionMode.IN_MEMORY,
    description="将空值替换为指定默认值。",
)

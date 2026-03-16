"""标准化算法元数据。"""

from app.contracts.algorithm import AlgorithmMeta, ExecutionMode

ALGORITHM_META = AlgorithmMeta(
    algo_code="standardize",
    name="数据标准化",
    category="data_processing",
    version="1.0.0",
    execution_mode=ExecutionMode.IN_MEMORY,
    description="对数值序列执行最小最大归一化。",
)

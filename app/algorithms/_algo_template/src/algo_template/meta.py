"""模板算法元数据。"""

from app.contracts.algorithm import AlgorithmMeta, ExecutionMode

ALGORITHM_META = AlgorithmMeta(
    algo_code="algo_template",
    name="模板算法",
    category="data_processing",
    version="1.0.0",
    execution_mode=ExecutionMode.IN_MEMORY,
    description="用于演示标准插件算法包的模板元数据。",
)

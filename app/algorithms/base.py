from abc import ABC, abstractmethod
from typing import Any, Dict

class AlgorithmMeta:
    """算法元数据"""
    def __init__(self, algo_code: str, name: str, category: str, version: str, 
                 input_schema: dict, output_schema: dict, default_timeout_sec: int = 60):
        self.algo_code = algo_code
        self.name = name
        self.category = category
        self.version = version
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.default_timeout_sec = default_timeout_sec

class BaseAlgorithm(ABC):
    """所有具体算法类的基类"""
    meta: AlgorithmMeta

    @abstractmethod
    def execute(self, params: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行算法核心逻辑
        
        Args:
            params: 配置的算法参数 (如 threshold, max_gap 等)
            inputs: 上游节点传递的输入数据 (如 dataset_ref)
            
        Returns:
            Dict[str, Any]: 输出结果字典，必须完全符合 meta.output_schema
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        参数校验逻辑（可选覆写，默认为通过）。
        供平台在运行前调用，验证传入的 params 数据是否合法。
        如果不合法抛出 ValueError 即可。
        """
        pass

from abc import ABC, abstractmethod
from typing import Any, Dict

class AlgorithmMeta:
    """算法元数据"""
    def __init__(self, algo_code: str, name: str, description: str = "", category: str = "general", 
                 version: str = "1.0.0", execution_mode: str = "celery_task", 
                 input_schema: dict = None, output_schema: dict = None,
                 param_schema: dict = None, default_timeout_sec: int = 60):
        self.algo_code = algo_code
        self.name = name
        self.description = description
        self.category = category
        self.version = version
        self.execution_mode = execution_mode
        self.input_schema = input_schema if input_schema is not None else {}
        self.output_schema = output_schema if output_schema is not None else {}
        self.param_schema = param_schema if param_schema is not None else {}
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
        参数校验逻辑（默认提供基于 meta.param_schema 的格式校验）。
        如果不合法抛出 ValueError。
        供平台在运行前调用，验证传入的 params 数据是否合法。
        """
        if getattr(self.meta, 'param_schema', None):
            try:
                import jsonschema
                jsonschema.validate(instance=params, schema=self.meta.param_schema)
            except ImportError:
                # 若未安装 jsonschema，做简单的 required 校验
                required_keys = self.meta.param_schema.get("required", [])
                for key in required_keys:
                    if key not in params:
                        raise ValueError(f"缺少必填参数: {key}")
            except jsonschema.exceptions.ValidationError as e:
                raise ValueError(f"参数校验失败: 字段 '{e.json_path}' - {e.message}")

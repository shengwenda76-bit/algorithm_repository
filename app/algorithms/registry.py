import importlib
import pkgutil
import logging
from typing import Dict, Type, List, Optional
from app.algorithms.base import BaseAlgorithm

logger = logging.getLogger(__name__)

class AlgorithmNotFoundError(Exception):
    def __init__(self, algo_code: str, version: str):
        super().__init__(f"未找到对应的算法: {algo_code} (版本: {version})")

class AlgorithmRegistry:
    """算法注册表 — 负责收集并管理本系统中所有算法的自动发现与注册"""
    
    # 用字典保存已注册算法: mapping 的 key 格式为 "algo_code@version"
    _registry: Dict[str, Type[BaseAlgorithm]] = {}

    @classmethod
    def register(cls, algo_class: Type[BaseAlgorithm]) -> Type[BaseAlgorithm]:
        """类装饰器：将带有 meta 的算法类注册进系统"""
        if not hasattr(algo_class, "meta") or algo_class.meta is None:
            raise ValueError(f"算法类 {algo_class.__name__} 缺少 'meta' 定义")
        
        meta = algo_class.meta
        key = f"{meta.algo_code}@{meta.version}"
        
        if key in cls._registry:
            logger.warning(f"算法注册表已存在相同的配置，正在覆盖: {key}")
            
        cls._registry[key] = algo_class
        logger.info(f"成功注册算法类别: {key}")
        return algo_class

    @classmethod
    def get(cls, algo_code: str, version: str) -> Type[BaseAlgorithm]:
        """根据 algo_code 和 version 获取对应的算法实现类"""
        key = f"{algo_code}@{version}"
        if key not in cls._registry:
            raise AlgorithmNotFoundError(algo_code, version)
        return cls._registry[key]

    @classmethod
    def list_all(cls, category: Optional[str] = None) -> List[Dict]:
        """列出所有已注册的算法清单，提供给接口 /v1/algorithms 返回前端"""
        results = []
        for key, algo_class in cls._registry.items():
            meta = algo_class.meta
            if category and meta.category != category:
                continue
            
            results.append({
                "algo_code": meta.algo_code,
                "name": meta.name,
                "category": meta.category,
                "version": meta.version,
                "input_schema": meta.input_schema,
                "output_schema": meta.output_schema,
                "default_timeout_sec": meta.default_timeout_sec
            })
        return results

    @classmethod
    def discover_algorithms(cls, package_name: str = "app.algorithms"):
        """
        自动扫描指定包下的所有子模块。
        通过 importlib 动态导入模块，从而触发文件内的 @AlgorithmRegistry.register 装饰器。
        
        FastAPI 启动（或 Celery Worker 启动）时调用此函数即可一键扫描全量代码。
        """
        logger.info(f"开始自动扫描包 {package_name} 下的算法应用...")
        try:
            package = importlib.import_module(package_name)
        except ImportError as e:
            logger.error(f"无法导入算法主包 {package_name}: {e}")
            return

        # 遍历子模块并动态载入
        for _, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            if not is_pkg:
                try:
                    importlib.import_module(name)
                except Exception as e:
                    logger.error(f"加载模块 {name} 失败: {e}")

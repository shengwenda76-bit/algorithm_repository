"""API 处理函数依赖提供器。"""

from app.services.algorithm_catalog_service import algorithm_catalog_service
from app.services.execution_service import execution_service


def get_algorithm_catalog_service():
    """返回算法目录服务实例。"""

    return algorithm_catalog_service


def get_execution_service():
    """返回执行服务实例。"""

    return execution_service

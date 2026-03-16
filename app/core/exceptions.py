"""运行时骨架使用的自定义异常。"""


class AlgorithmCatalogError(Exception):
    """算法目录相关异常的基类。"""


class AlgorithmNotFoundError(AlgorithmCatalogError):
    """当算法或指定版本不存在时抛出。"""

    def __init__(self, algo_code: str, version: str):
        super().__init__(f"Algorithm not found: {algo_code}@{version}")


class ArtifactFetchError(Exception):
    """当算法制品获取或校验失败时抛出。"""


class AlgorithmLoadError(Exception):
    """当下载后的算法模块无法导入时抛出。"""

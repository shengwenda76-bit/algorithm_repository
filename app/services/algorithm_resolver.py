"""将 `algo_code@version` 解析为运行时制品信息。"""

from app.schemas.algorithm import ResolvedArtifact
from app.services.algorithm_catalog_service import algorithm_catalog_service


class AlgorithmResolver:
    """对算法目录服务的轻量封装。"""

    def resolve(self, algo_code: str, version: str) -> ResolvedArtifact:
        """为执行阶段解析算法制品元数据。"""

        return algorithm_catalog_service.get_resolved_artifact(algo_code, version)


algorithm_resolver = AlgorithmResolver()

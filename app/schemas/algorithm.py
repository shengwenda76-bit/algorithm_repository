"""算法目录与制品解析相关的数据模型。"""

from pydantic import BaseModel, Field


class AlgorithmCatalogEntry(BaseModel):
    """平台对外暴露的算法目录元数据。"""

    algo_code: str = Field(..., description="Unique algorithm code")
    name: str = Field(..., description="Display name")
    category: str = Field(..., description="Algorithm category")
    version: str = Field(..., description="Current active version")
    package_name: str = Field(..., description="Artifact package name")
    import_package: str = Field(..., description="Installed import package name")
    entry_module: str = Field(..., description="Module loaded at runtime")
    class_name: str = Field(..., description="Algorithm class inside the entry module")
    description: str = Field(default="", description="Human-readable description")
    execution_mode: str = Field(default="in_memory", description="Execution mode")


class ResolvedArtifact(BaseModel):
    """由目录解析得到的运行时制品信息。"""

    algo_code: str
    version: str
    package_name: str
    import_package: str
    entry_module: str
    class_name: str
    artifact_filename: str
    artifact_url: str
    source_dir: str

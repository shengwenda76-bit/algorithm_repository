"""本文件用于定义算法库平台接口层使用的 Pydantic schema。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FieldSpecSchema(BaseModel):
    """字段定义 schema。"""

    name: str
    data_type: str
    description: str = ""
    required: bool = True
    default: Any = None
    example: Any = None


class ResourceSpecSchema(BaseModel):
    """资源需求 schema。"""

    cpu: str = ""
    memory: str = ""
    timeout: str = ""


class AlgorithmDefinitionSchema(BaseModel):
    """算法定义 schema。"""

    code: str
    name: str
    version: str
    entrypoint: str = ""
    category: str = ""
    description: str = ""
    inputs: list[FieldSpecSchema] = Field(default_factory=list)
    outputs: list[FieldSpecSchema] = Field(default_factory=list)
    params: list[FieldSpecSchema] = Field(default_factory=list)
    resources: ResourceSpecSchema = Field(default_factory=ResourceSpecSchema)
    requirements: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    status: str = "registered"


class PackageArtifactSchema(BaseModel):
    """算法包信息 schema。"""

    code: str = ""
    version: str = ""
    package_name: str
    package_version: str = ""
    repository_url: str = ""
    artifact_type: str = ""
    filename: str = ""
    sha256: str = ""


class RegistrationRequestSchema(BaseModel):
    """算法注册请求 schema。"""

    definition: AlgorithmDefinitionSchema
    artifact: PackageArtifactSchema


class ValidationErrorsSchema(BaseModel):
    """校验错误集合 schema。"""

    definition: list[str] = Field(default_factory=list)
    artifact: list[str] = Field(default_factory=list)


class ValidationResultSchema(BaseModel):
    """校验结果 schema。"""

    valid: bool
    errors: ValidationErrorsSchema


class RegistrationResponseSchema(BaseModel):
    """注册响应 schema。"""

    code: str
    name: str
    version: str
    status: str
    definition: AlgorithmDefinitionSchema
    artifact: PackageArtifactSchema


class AlgorithmListItemSchema(BaseModel):
    """算法列表项 schema。"""

    code: str
    name: str
    version: str
    category: str = ""
    description: str = ""
    status: str


class AlgorithmListResponseSchema(BaseModel):
    """算法列表响应 schema。"""

    items: list[AlgorithmListItemSchema] = Field(default_factory=list)
    total: int = 0


class AlgorithmDetailResponseSchema(BaseModel):
    """算法详情响应 schema。"""

    code: str
    name: str
    version: str
    category: str = ""
    description: str = ""
    status: str


class AlgorithmVersionItemSchema(BaseModel):
    """版本列表项 schema。"""

    version: str
    status: str
    name: str
    is_latest: bool = False


class AlgorithmVersionListResponseSchema(BaseModel):
    """算法版本列表响应 schema。"""

    code: str
    items: list[AlgorithmVersionItemSchema] = Field(default_factory=list)


class AlgorithmVersionDetailResponseSchema(BaseModel):
    """算法版本详情响应 schema。"""

    code: str
    name: str
    version: str
    status: str
    definition: AlgorithmDefinitionSchema
    artifact: PackageArtifactSchema


class DebugExecuteRequestSchema(BaseModel):
    """调试执行请求 schema。"""

    version: str | None = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)


class DebugExecuteResponseSchema(BaseModel):
    """调试执行响应 schema。"""

    code: str
    version: str
    result: dict[str, Any]

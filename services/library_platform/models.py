"""本文件用于定义算法库平台核心模型的占位结构。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from sdk.algorithm_sdk.contracts import FieldSpec, ResourceSpec


@dataclass(slots=True)
class AlgorithmDefinition:
    """算法定义占位模型。"""

    code: str
    name: str
    version: str
    entrypoint: str = ""
    category: str = ""
    description: str = ""
    inputs: list[FieldSpec] = field(default_factory=list)
    outputs: list[FieldSpec] = field(default_factory=list)
    params: list[FieldSpec] = field(default_factory=list)
    resources: ResourceSpec = field(default_factory=ResourceSpec)
    requirements: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    status: str = "registered"

    def to_dict(self) -> dict[str, Any]:
        """返回算法定义的字典表示。"""

        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AlgorithmDefinition":
        """根据请求体构造算法定义对象。"""

        return cls(
            code=payload["code"],
            name=payload["name"],
            version=payload["version"],
            entrypoint=payload.get("entrypoint", ""),
            category=payload.get("category", ""),
            description=payload.get("description", ""),
            inputs=[FieldSpec(**item) for item in payload.get("inputs", [])],
            outputs=[FieldSpec(**item) for item in payload.get("outputs", [])],
            params=[FieldSpec(**item) for item in payload.get("params", [])],
            resources=ResourceSpec(**payload.get("resources", {})),
            requirements=list(payload.get("requirements", [])),
            tags=list(payload.get("tags", [])),
            status=payload.get("status", "registered"),
        )


@dataclass(slots=True)
class PackageArtifact:
    """算法包信息占位模型。"""

    code: str
    version: str
    package_name: str
    package_version: str = ""
    repository_url: str = ""
    artifact_type: str = ""
    filename: str = ""
    sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        """返回算法包信息的字典表示。"""

        return asdict(self)

    @classmethod
    def from_payload(
        cls,
        code: str,
        version: str,
        payload: dict[str, Any],
    ) -> "PackageArtifact":
        """根据请求体构造算法包信息对象。"""

        return cls(
            code=code,
            version=version,
            package_name=payload["package_name"],
            package_version=payload.get("package_version", ""),
            repository_url=payload.get("repository_url", ""),
            artifact_type=payload.get("artifact_type", ""),
            filename=payload.get("filename", ""),
            sha256=payload.get("sha256", ""),
        )

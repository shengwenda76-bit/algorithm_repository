"""本文件用于提供算法注册中心的最小内存实现。"""

from __future__ import annotations

from dataclasses import dataclass

from sdk.algorithm_sdk.validators import (
    validate_algorithm_meta,
    validate_package_artifact,
)
from services.library_platform.models import AlgorithmDefinition, PackageArtifact
from services.library_platform.registry.repository import (
    InMemoryRegistryRepository,
    RegistryRepository,
)


class DuplicateAlgorithmVersionError(Exception):
    """同一算法版本重复注册时抛出的异常。"""


class InvalidRegistrationPayloadError(Exception):
    """注册请求体不合法时抛出的异常。"""


class AlgorithmNotFoundError(Exception):
    """算法不存在时抛出的异常。"""


@dataclass(slots=True)
class RegistrationRecord:
    """注册记录占位模型。"""

    definition: AlgorithmDefinition
    artifact: PackageArtifact
    status: str = "registered"
    is_latest: bool = False

    def to_dict(self) -> dict[str, object]:
        """返回注册结果的字典表示。"""

        return {
            "code": self.definition.code,
            "name": self.definition.name,
            "version": self.definition.version,
            "status": self.status,
            "is_latest": self.is_latest,
            "definition": self.definition.to_dict(),
            "artifact": self.artifact.to_dict(),
        }


class RegistryService:
    """算法注册中心的最小内存实现。"""

    def __init__(self, repository: RegistryRepository | None = None) -> None:
        self._repository = repository or InMemoryRegistryRepository()

    def validate_payload(self, payload: dict) -> dict[str, object]:
        """校验算法注册请求体。"""

        definition_payload = payload.get("definition", {})
        artifact_payload = payload.get("artifact", {})
        definition_errors = validate_algorithm_meta(definition_payload)
        artifact_errors = validate_package_artifact(artifact_payload)

        return {
            "valid": not definition_errors and not artifact_errors,
            "errors": {
                "definition": definition_errors,
                "artifact": artifact_errors,
            },
        }

    def register(self, payload: dict) -> dict[str, object]:
        """注册新的算法版本。"""

        validation_result = self.validate_payload(payload)
        if not validation_result["valid"]:
            raise InvalidRegistrationPayloadError("Registration payload is invalid.")

        definition_payload = payload["definition"]
        artifact_payload = payload["artifact"]
        key = (definition_payload["code"], definition_payload["version"])
        if self._repository.version_exists(*key):
            raise DuplicateAlgorithmVersionError(
                f"Algorithm version {definition_payload['code']}:{definition_payload['version']} already registered."
            )

        definition = AlgorithmDefinition.from_payload(definition_payload)
        artifact = PackageArtifact.from_payload(
            code=definition.code,
            version=definition.version,
            payload=artifact_payload,
        )
        self._repository.save_registration(definition=definition, artifact=artifact)
        detail = self._repository.get_version_detail(definition.code, definition.version)
        if detail is None:
            raise AlgorithmNotFoundError(
                f"Algorithm version {definition.code}:{definition.version} not found."
            )
        return detail

    def list_algorithms(self) -> dict[str, object]:
        """返回当前已注册的算法列表。"""

        items = self._repository.list_algorithms()
        return {"items": items, "total": len(items)}

    def get_algorithm(self, code: str) -> dict[str, object]:
        """返回指定算法的详情。"""

        summary = self._repository.get_algorithm(code)
        if summary is None:
            raise AlgorithmNotFoundError(f"Algorithm {code} not found.")
        return summary

    def list_versions(self, code: str) -> dict[str, object]:
        """返回指定算法的版本列表。"""

        versions = self._repository.list_versions(code)
        if not versions:
            raise AlgorithmNotFoundError(f"Algorithm {code} not found.")
        return {"code": code, "items": versions}

    def get_version(self, code: str, version: str) -> dict[str, object]:
        """返回指定算法版本的详情。"""

        detail = self._repository.get_version_detail(code, version)
        if detail is None:
            raise AlgorithmNotFoundError(f"Algorithm version {code}:{version} not found.")
        return detail

    def get_record(self, code: str, version: str | None = None) -> RegistrationRecord:
        """返回指定算法的注册记录。"""

        target = self._repository.get_execution_target(code=code, version=version)
        if target is None:
            if version is None:
                raise AlgorithmNotFoundError(f"Algorithm {code} not found.")
            raise AlgorithmNotFoundError(f"Algorithm version {code}:{version} not found.")

        detail = self.get_version(code, target["version"])
        return RegistrationRecord(
            definition=AlgorithmDefinition.from_payload(detail["definition"]),
            artifact=PackageArtifact.from_payload(
                code=code,
                version=target["version"],
                payload=detail["artifact"],
            ),
            status=str(detail["status"]),
            is_latest=bool(detail.get("is_latest", False)),
        )

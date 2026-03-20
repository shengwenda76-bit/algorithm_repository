"""本文件用于提供可替换的算法注册中心仓储实现。"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable

from services.library_platform.db import bootstrap_sqlite_schema, connect_sqlite
from services.library_platform.models import AlgorithmDefinition, PackageArtifact


def _utcnow() -> str:
    """返回统一格式的 UTC 时间戳。"""

    return datetime.now(timezone.utc).isoformat()


@runtime_checkable
class RegistryRepository(Protocol):
    """注册中心仓储协议。"""

    def version_exists(self, code: str, version: str) -> bool:
        """判断指定算法版本是否已经存在。"""

    def save_registration(self, definition: AlgorithmDefinition, artifact: PackageArtifact) -> None:
        """保存注册结果。"""

    def list_algorithms(self) -> list[dict[str, object]]:
        """返回算法列表视图。"""

    def get_algorithm(self, code: str) -> dict[str, object] | None:
        """返回算法详情摘要。"""

    def list_versions(self, code: str) -> list[dict[str, object]]:
        """返回算法版本列表。"""

    def get_version_detail(self, code: str, version: str) -> dict[str, object] | None:
        """返回算法版本详情。"""

    def get_execution_target(
        self,
        code: str,
        version: str | None = None,
    ) -> dict[str, str] | None:
        """返回调试执行目标。"""


@dataclass(slots=True)
class AlgorithmRow:
    """算法主表记录。"""

    code: str
    name: str
    category: str = ""
    description: str = ""
    status: str = "registered"
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class AlgorithmVersionRow:
    """算法版本表记录。"""

    code: str
    version: str
    entrypoint: str
    inputs_json: list[dict[str, Any]] = field(default_factory=list)
    outputs_json: list[dict[str, Any]] = field(default_factory=list)
    params_json: list[dict[str, Any]] = field(default_factory=list)
    resources_json: dict[str, Any] = field(default_factory=dict)
    requirements_json: list[str] = field(default_factory=list)
    tags_json: list[str] = field(default_factory=list)
    status: str = "registered"
    is_latest: bool = False
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class AlgorithmArtifactRow:
    """算法制品表记录。"""

    code: str
    version: str
    package_name: str
    package_version: str = ""
    repository_url: str = ""
    artifact_type: str = ""
    filename: str = ""
    sha256: str = ""
    created_at: str = ""
    updated_at: str = ""


class InMemoryRegistryRepository:
    """按三张表组织的内存仓储。"""

    def __init__(self) -> None:
        self._algorithms: dict[str, AlgorithmRow] = {}
        self._versions: dict[tuple[str, str], AlgorithmVersionRow] = {}
        self._artifacts: dict[tuple[str, str], AlgorithmArtifactRow] = {}

    def version_exists(self, code: str, version: str) -> bool:
        """判断指定算法版本是否已经存在。"""

        return (code, version) in self._versions

    def save_registration(
        self,
        definition: AlgorithmDefinition,
        artifact: PackageArtifact,
    ) -> None:
        """保存算法主表、版本表和制品表信息。"""

        self._upsert_algorithm(definition)
        self._insert_version(definition)
        self._insert_artifact(artifact)
        self._mark_latest_version(definition.code, definition.version)

    def list_algorithms(self) -> list[dict[str, object]]:
        """返回算法列表视图。"""

        items: list[dict[str, object]] = []
        for code in sorted(self._algorithms):
            summary = self.get_algorithm(code)
            if summary is not None:
                items.append(summary)
        return items

    def get_algorithm(self, code: str) -> dict[str, object] | None:
        """返回单个算法的主信息和最新版本摘要。"""

        algorithm = self._algorithms.get(code)
        latest_version = self._get_latest_version_row(code)
        if algorithm is None or latest_version is None:
            return None

        return {
            "code": algorithm.code,
            "name": algorithm.name,
            "version": latest_version.version,
            "category": algorithm.category,
            "description": algorithm.description,
            "status": latest_version.status,
        }

    def list_versions(self, code: str) -> list[dict[str, object]]:
        """返回指定算法的全部版本信息。"""

        algorithm = self._algorithms.get(code)
        if algorithm is None:
            return []

        items = [
            {
                "version": row.version,
                "status": row.status,
                "name": algorithm.name,
                "is_latest": row.is_latest,
            }
            for (item_code, _), row in self._versions.items()
            if item_code == code
        ]
        items.sort(key=lambda item: item["version"])
        return items

    def get_version_detail(self, code: str, version: str) -> dict[str, object] | None:
        """返回算法版本详情视图。"""

        algorithm = self._algorithms.get(code)
        version_row = self._versions.get((code, version))
        if algorithm is None or version_row is None:
            return None

        artifact_row = self._artifacts.get((code, version))
        return _build_version_detail_view(algorithm, version_row, artifact_row)

    def get_execution_target(
        self,
        code: str,
        version: str | None = None,
    ) -> dict[str, str] | None:
        """返回调试执行所需的版本和入口点信息。"""

        if code not in self._algorithms:
            return None

        if version is None:
            version_row = self._get_latest_version_row(code)
        else:
            version_row = self._versions.get((code, version))
        if version_row is None:
            return None

        return {
            "code": code,
            "version": version_row.version,
            "entrypoint": version_row.entrypoint,
        }

    def _upsert_algorithm(self, definition: AlgorithmDefinition) -> None:
        """插入或更新算法主表信息。"""

        now = _utcnow()
        algorithm = self._algorithms.get(definition.code)
        if algorithm is None:
            self._algorithms[definition.code] = AlgorithmRow(
                code=definition.code,
                name=definition.name,
                category=definition.category,
                description=definition.description,
                status=definition.status,
                created_at=now,
                updated_at=now,
            )
            return

        algorithm.name = definition.name
        algorithm.category = definition.category
        algorithm.description = definition.description
        algorithm.status = definition.status
        algorithm.updated_at = now

    def _insert_version(self, definition: AlgorithmDefinition) -> None:
        """插入算法版本表记录。"""

        now = _utcnow()
        payload = definition.to_dict()
        self._versions[(definition.code, definition.version)] = AlgorithmVersionRow(
            code=definition.code,
            version=definition.version,
            entrypoint=definition.entrypoint,
            inputs_json=deepcopy(payload["inputs"]),
            outputs_json=deepcopy(payload["outputs"]),
            params_json=deepcopy(payload["params"]),
            resources_json=deepcopy(payload["resources"]),
            requirements_json=deepcopy(payload["requirements"]),
            tags_json=deepcopy(payload["tags"]),
            status=definition.status,
            is_latest=False,
            created_at=now,
            updated_at=now,
        )

    def _insert_artifact(self, artifact: PackageArtifact) -> None:
        """插入算法制品表记录。"""

        now = _utcnow()
        self._artifacts[(artifact.code, artifact.version)] = AlgorithmArtifactRow(
            code=artifact.code,
            version=artifact.version,
            package_name=artifact.package_name,
            package_version=artifact.package_version,
            repository_url=artifact.repository_url,
            artifact_type=artifact.artifact_type,
            filename=artifact.filename,
            sha256=artifact.sha256,
            created_at=now,
            updated_at=now,
        )

    def _mark_latest_version(self, code: str, version: str) -> None:
        """切换指定算法的最新版本标记。"""

        now = _utcnow()
        for (item_code, item_version), row in self._versions.items():
            if item_code != code:
                continue
            row.is_latest = item_version == version
            row.updated_at = now

        algorithm = self._algorithms.get(code)
        version_row = self._versions.get((code, version))
        if algorithm is not None and version_row is not None:
            algorithm.status = version_row.status
            algorithm.updated_at = now

    def _get_latest_version_row(self, code: str) -> AlgorithmVersionRow | None:
        """返回指定算法的最新版本记录。"""

        candidates = [
            row for (item_code, _), row in self._versions.items() if item_code == code
        ]
        if not candidates:
            return None

        latest = next((row for row in candidates if row.is_latest), None)
        if latest is not None:
            return latest

        return max(candidates, key=lambda item: item.version)


class SqliteRegistryRepository:
    """按三张表组织的 sqlite 仓储。"""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._connection = connect_sqlite(database_url)
        bootstrap_sqlite_schema(self._connection)

    def close(self) -> None:
        """关闭 sqlite 连接。"""

        self._connection.close()

    def version_exists(self, code: str, version: str) -> bool:
        """判断指定算法版本是否已经存在。"""

        row = self._connection.execute(
            "SELECT 1 FROM algorithm_versions WHERE code = ? AND version = ?",
            (code, version),
        ).fetchone()
        return row is not None

    def save_registration(
        self,
        definition: AlgorithmDefinition,
        artifact: PackageArtifact,
    ) -> None:
        """保存注册结果到 sqlite。"""

        now = _utcnow()
        payload = definition.to_dict()
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO algorithms (code, name, category, description, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                    name = excluded.name,
                    category = excluded.category,
                    description = excluded.description,
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (
                    definition.code,
                    definition.name,
                    definition.category,
                    definition.description,
                    definition.status,
                    now,
                    now,
                ),
            )
            self._connection.execute(
                """
                INSERT INTO algorithm_versions (
                    code, version, entrypoint, inputs_json, outputs_json, params_json,
                    resources_json, requirements_json, tags_json, status, is_latest,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    definition.code,
                    definition.version,
                    definition.entrypoint,
                    json.dumps(payload["inputs"], ensure_ascii=False),
                    json.dumps(payload["outputs"], ensure_ascii=False),
                    json.dumps(payload["params"], ensure_ascii=False),
                    json.dumps(payload["resources"], ensure_ascii=False),
                    json.dumps(payload["requirements"], ensure_ascii=False),
                    json.dumps(payload["tags"], ensure_ascii=False),
                    definition.status,
                    0,
                    now,
                    now,
                ),
            )
            self._connection.execute(
                """
                INSERT INTO algorithm_artifacts (
                    code, version, package_name, package_version, repository_url,
                    artifact_type, filename, sha256, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.code,
                    artifact.version,
                    artifact.package_name,
                    artifact.package_version,
                    artifact.repository_url,
                    artifact.artifact_type,
                    artifact.filename,
                    artifact.sha256,
                    now,
                    now,
                ),
            )
            self._connection.execute(
                "UPDATE algorithm_versions SET is_latest = 0, updated_at = ? WHERE code = ?",
                (now, definition.code),
            )
            self._connection.execute(
                """
                UPDATE algorithm_versions
                SET is_latest = 1, updated_at = ?
                WHERE code = ? AND version = ?
                """,
                (now, definition.code, definition.version),
            )

    def list_algorithms(self) -> list[dict[str, object]]:
        """返回算法列表视图。"""

        rows = self._connection.execute(
            """
            SELECT
                a.code,
                a.name,
                a.category,
                a.description,
                v.version,
                v.status
            FROM algorithms AS a
            JOIN algorithm_versions AS v
              ON a.code = v.code
             AND v.is_latest = 1
            ORDER BY a.code
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def get_algorithm(self, code: str) -> dict[str, object] | None:
        """返回算法详情摘要。"""

        row = self._connection.execute(
            """
            SELECT
                a.code,
                a.name,
                a.category,
                a.description,
                v.version,
                v.status
            FROM algorithms AS a
            JOIN algorithm_versions AS v
              ON a.code = v.code
             AND v.is_latest = 1
            WHERE a.code = ?
            """,
            (code,),
        ).fetchone()
        return dict(row) if row is not None else None

    def list_versions(self, code: str) -> list[dict[str, object]]:
        """返回指定算法的全部版本信息。"""

        algorithm = self._connection.execute(
            "SELECT name FROM algorithms WHERE code = ?",
            (code,),
        ).fetchone()
        if algorithm is None:
            return []

        rows = self._connection.execute(
            """
            SELECT version, status, is_latest
            FROM algorithm_versions
            WHERE code = ?
            ORDER BY version
            """,
            (code,),
        ).fetchall()
        return [
            {
                "version": row["version"],
                "status": row["status"],
                "name": algorithm["name"],
                "is_latest": bool(row["is_latest"]),
            }
            for row in rows
        ]

    def get_version_detail(self, code: str, version: str) -> dict[str, object] | None:
        """返回算法版本详情视图。"""

        row = self._connection.execute(
            """
            SELECT
                a.code AS algorithm_code,
                a.name AS algorithm_name,
                a.category AS algorithm_category,
                a.description AS algorithm_description,
                a.status AS algorithm_status,
                a.created_at AS algorithm_created_at,
                a.updated_at AS algorithm_updated_at,
                v.code AS version_code,
                v.version AS version_value,
                v.entrypoint,
                v.inputs_json,
                v.outputs_json,
                v.params_json,
                v.resources_json,
                v.requirements_json,
                v.tags_json,
                v.status AS version_status,
                v.is_latest,
                v.created_at AS version_created_at,
                v.updated_at AS version_updated_at,
                art.package_name,
                art.package_version,
                art.repository_url,
                art.artifact_type,
                art.filename,
                art.sha256,
                art.created_at AS artifact_created_at,
                art.updated_at AS artifact_updated_at
            FROM algorithms AS a
            JOIN algorithm_versions AS v
              ON a.code = v.code
            LEFT JOIN algorithm_artifacts AS art
              ON v.code = art.code
             AND v.version = art.version
            WHERE a.code = ? AND v.version = ?
            """,
            (code, version),
        ).fetchone()
        if row is None:
            return None

        algorithm = AlgorithmRow(
            code=row["algorithm_code"],
            name=row["algorithm_name"],
            category=row["algorithm_category"] or "",
            description=row["algorithm_description"] or "",
            status=row["algorithm_status"],
            created_at=row["algorithm_created_at"],
            updated_at=row["algorithm_updated_at"],
        )
        version_row = AlgorithmVersionRow(
            code=row["version_code"],
            version=row["version_value"],
            entrypoint=row["entrypoint"],
            inputs_json=json.loads(row["inputs_json"] or "[]"),
            outputs_json=json.loads(row["outputs_json"] or "[]"),
            params_json=json.loads(row["params_json"] or "[]"),
            resources_json=json.loads(row["resources_json"] or "{}"),
            requirements_json=json.loads(row["requirements_json"] or "[]"),
            tags_json=json.loads(row["tags_json"] or "[]"),
            status=row["version_status"],
            is_latest=bool(row["is_latest"]),
            created_at=row["version_created_at"],
            updated_at=row["version_updated_at"],
        )
        artifact_row = None
        if row["package_name"] is not None:
            artifact_row = AlgorithmArtifactRow(
                code=code,
                version=version,
                package_name=row["package_name"],
                package_version=row["package_version"] or "",
                repository_url=row["repository_url"] or "",
                artifact_type=row["artifact_type"] or "",
                filename=row["filename"] or "",
                sha256=row["sha256"] or "",
                created_at=row["artifact_created_at"] or "",
                updated_at=row["artifact_updated_at"] or "",
            )

        return _build_version_detail_view(algorithm, version_row, artifact_row)

    def get_execution_target(
        self,
        code: str,
        version: str | None = None,
    ) -> dict[str, str] | None:
        """返回调试执行所需的版本和入口点信息。"""

        if version is None:
            row = self._connection.execute(
                """
                SELECT code, version, entrypoint
                FROM algorithm_versions
                WHERE code = ? AND is_latest = 1
                """,
                (code,),
            ).fetchone()
        else:
            row = self._connection.execute(
                """
                SELECT code, version, entrypoint
                FROM algorithm_versions
                WHERE code = ? AND version = ?
                """,
                (code, version),
            ).fetchone()
        return dict(row) if row is not None else None


def _build_version_detail_view(
    algorithm: AlgorithmRow,
    version_row: AlgorithmVersionRow,
    artifact_row: AlgorithmArtifactRow | None,
) -> dict[str, object]:
    """组装统一的版本详情视图。"""

    definition = AlgorithmDefinition.from_payload(
        {
            "code": algorithm.code,
            "name": algorithm.name,
            "version": version_row.version,
            "entrypoint": version_row.entrypoint,
            "category": algorithm.category,
            "description": algorithm.description,
            "inputs": deepcopy(version_row.inputs_json),
            "outputs": deepcopy(version_row.outputs_json),
            "params": deepcopy(version_row.params_json),
            "resources": deepcopy(version_row.resources_json),
            "requirements": deepcopy(version_row.requirements_json),
            "tags": deepcopy(version_row.tags_json),
            "status": version_row.status,
        }
    )
    artifact = PackageArtifact(
        code=algorithm.code,
        version=version_row.version,
        package_name=artifact_row.package_name if artifact_row is not None else "",
        package_version=artifact_row.package_version if artifact_row is not None else "",
        repository_url=artifact_row.repository_url if artifact_row is not None else "",
        artifact_type=artifact_row.artifact_type if artifact_row is not None else "",
        filename=artifact_row.filename if artifact_row is not None else "",
        sha256=artifact_row.sha256 if artifact_row is not None else "",
    )
    return {
        "code": algorithm.code,
        "name": algorithm.name,
        "version": version_row.version,
        "status": version_row.status,
        "is_latest": version_row.is_latest,
        "definition": definition.to_dict(),
        "artifact": artifact.to_dict(),
    }

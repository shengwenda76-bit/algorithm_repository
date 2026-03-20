import json
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from services.library_platform.models import Algorithm, AlgorithmVersion, AlgorithmArtifact
from services.library_platform.schemas.registry import RegisterRequest

class AlgorithmRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_algorithm_by_code(self, code: str) -> Optional[Algorithm]:
        return self.db.query(Algorithm).filter(Algorithm.code == code).first()

    def version_exists(self, code: str, version: str) -> bool:
        return self.db.query(AlgorithmVersion).filter(
            AlgorithmVersion.algorithm_code == code,
            AlgorithmVersion.version == version
        ).first() is not None

    def create_or_update_algorithm(self, definition: Any) -> Algorithm:
        algo = self.get_algorithm_by_code(definition.code)
        if not algo:
            algo = Algorithm(
                code=definition.code,
                name=definition.name,
                category=definition.category,
                description=definition.description,
                status="active"
            )
            self.db.add(algo)
        else:
            algo.name = definition.name
            algo.category = definition.category
            algo.description = definition.description
        self.db.flush()
        return algo

    def add_version(self, payload: RegisterRequest) -> Tuple[AlgorithmVersion, AlgorithmArtifact]:
        definition = payload.definition
        artifact = payload.artifact
        
        # update all existing versions to not be latest
        self.db.query(AlgorithmVersion).filter(
            AlgorithmVersion.algorithm_code == definition.code
        ).update({"is_latest": False})
        
        # add new version
        new_version = AlgorithmVersion(
            algorithm_code=definition.code,
            version=definition.version,
            entrypoint=definition.entrypoint,
            inputs_json=json.dumps(definition.inputs, ensure_ascii=False),
            outputs_json=json.dumps(definition.outputs, ensure_ascii=False),
            params_json=json.dumps(definition.params, ensure_ascii=False),
            resources_json=json.dumps(definition.resources, ensure_ascii=False),
            requirements_json=json.dumps(definition.requirements, ensure_ascii=False),
            tags_json=json.dumps(definition.tags, ensure_ascii=False),
            status="registered",
            is_latest=True
        )
        self.db.add(new_version)
        
        # add artifact
        new_artifact = AlgorithmArtifact(
            algorithm_code=definition.code,
            version=definition.version,
            package_name=artifact.package_name,
            package_version=artifact.package_version,
            repository_url=artifact.repository_url,
            artifact_type=artifact.artifact_type,
            filename=artifact.filename,
            sha256=artifact.sha256
        )
        self.db.add(new_artifact)
        
        self.db.flush()
        return new_version, new_artifact

    def list_algorithms(self, category: Optional[str] = None, status: str = "active", skip: int = 0, limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        query = self.db.query(Algorithm, AlgorithmVersion.version).join(
            AlgorithmVersion, Algorithm.code == AlgorithmVersion.algorithm_code
        ).filter(AlgorithmVersion.is_latest == True)

        if category:
            query = query.filter(Algorithm.category == category)
        if status:
            query = query.filter(Algorithm.status == status)

        total = query.count()
        results = query.offset(skip).limit(limit).all()

        items = []
        for algo, version in results:
            items.append({
                "code": algo.code,
                "name": algo.name,
                "category": algo.category,
                "status": algo.status,
                "version": version
            })

        return items, total

    def get_version_detail(self, code: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query = self.db.query(Algorithm, AlgorithmVersion, AlgorithmArtifact).join(
            AlgorithmVersion, Algorithm.code == AlgorithmVersion.algorithm_code
        ).outerjoin(
            AlgorithmArtifact, 
            (AlgorithmArtifact.algorithm_code == AlgorithmVersion.algorithm_code) & 
            (AlgorithmArtifact.version == AlgorithmVersion.version)
        ).filter(Algorithm.code == code)

        if version:
            query = query.filter(AlgorithmVersion.version == version)
        else:
            query = query.filter(AlgorithmVersion.is_latest == True)

        result = query.first()
        if not result:
            return None

        algo, ver, art = result

        return {
            "code": algo.code,
            "name": algo.name,
            "version": ver.version,
            "is_latest": ver.is_latest,
            "status": ver.status,
            "definition": {
                "code": algo.code,
                "name": algo.name,
                "version": ver.version,
                "entrypoint": ver.entrypoint,
                "category": algo.category,
                "description": algo.description,
                "inputs": json.loads(ver.inputs_json),
                "outputs": json.loads(ver.outputs_json),
                "params": json.loads(ver.params_json),
                "resources": json.loads(ver.resources_json),
                "requirements": json.loads(ver.requirements_json),
                "tags": json.loads(ver.tags_json)
            },
            "artifact": {
                "package_name": art.package_name if art else "",
                "repository_url": art.repository_url if art else "",
                "filename": art.filename if art else "",
                "sha256": art.sha256 if art else ""
            }
        }

    def list_versions(self, code: str) -> List[Dict[str, Any]]:
        algo = self.get_algorithm_by_code(code)
        if not algo:
            return []

        versions = self.db.query(AlgorithmVersion).filter(
            AlgorithmVersion.algorithm_code == code
        ).order_by(AlgorithmVersion.version.desc()).all()

        return [
            {
                "version": v.version,
                "status": v.status,
                "name": algo.name,
                "is_latest": v.is_latest
            }
            for v in versions
        ]

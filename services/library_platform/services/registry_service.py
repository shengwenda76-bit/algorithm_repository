from typing import Dict, Any, Tuple
import logging
from fastapi import HTTPException

from sdk.algorithm_sdk.validators import validate_algorithm_meta, validate_package_artifact
from services.library_platform.repositories.algorithm_repository import AlgorithmRepository
from services.library_platform.schemas.registry import RegisterRequest

logger = logging.getLogger(__name__)

class RegistryService:
    def __init__(self, repository: AlgorithmRepository):
        self._repository = repository

    def validate_payload(self, payload: RegisterRequest) -> Dict[str, Any]:
        definition_payload = payload.definition.model_dump()
        artifact_payload = payload.artifact.model_dump()
        
        definition_errors = validate_algorithm_meta(definition_payload)
        artifact_errors = validate_package_artifact(artifact_payload)

        return {
            "valid": not definition_errors and not artifact_errors,
            "errors": {
                "definition": definition_errors,
                "artifact": artifact_errors,
            },
        }

    def register(self, payload: RegisterRequest) -> Dict[str, Any]:
        validation_result = self.validate_payload(payload)
        if not validation_result["valid"]:
            logger.warning(f"Validation failed for registration: {validation_result['errors']}")
            raise HTTPException(status_code=422, detail={
                "error": "VALIDATION_FAILED",
                "message": "Payload validation failed",
                "detail": validation_result["errors"]
            })

        definition = payload.definition
        if self._repository.version_exists(definition.code, definition.version):
            logger.warning(f"Duplicate registration attempt: {definition.code}:{definition.version}")
            raise HTTPException(status_code=409, detail={
                "error": "DUPLICATE_VERSION",
                "message": f"Algorithm {definition.code} version {definition.version} already registered.",
                "detail": {}
            })

        try:
            algo = self._repository.create_or_update_algorithm(definition)
            new_version, new_artifact = self._repository.add_version(payload)
            self._repository.db.commit()
            
            logger.info(f"Successfully registered algorithm {definition.code} version {definition.version}")
            return {
                "code": algo.code,
                "name": algo.name,
                "version": new_version.version,
                "status": new_version.status,
                "is_latest": new_version.is_latest,
                "registered_at": new_version.created_at.isoformat()
            }
        except Exception as e:
            self._repository.db.rollback()
            logger.error(f"Error saving registration: {e}")
            raise HTTPException(status_code=500, detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to save registration",
                "detail": str(e)
            })

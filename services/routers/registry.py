from fastapi import APIRouter, Depends, status
import logging

from services.schemas.registry import RegisterRequest, RegisterResponse, ValidateResponse
from services.services.registry_service import RegistryService
from services.dependencies import get_registry_service

router = APIRouter(prefix="/algorithms", tags=["registry"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_algorithm(
    payload: RegisterRequest,
    service: RegistryService = Depends(get_registry_service)
):
    logger.info(f"Received registration request for {payload.definition.code}:{payload.definition.version}")
    return service.register(payload)

@router.post("/validate", response_model=ValidateResponse, status_code=status.HTTP_200_OK)
def validate_algorithm(
    payload: RegisterRequest,
    service: RegistryService = Depends(get_registry_service)
):
    logger.info(f"Received validation request for {payload.definition.code}:{payload.definition.version}")
    return service.validate_payload(payload)

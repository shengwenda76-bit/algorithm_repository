from sqlalchemy.orm import Session
from fastapi import Depends
from services.database.base import SessionLocal
from services.repositories.algorithm_repository import AlgorithmRepository
from services.services.registry_service import RegistryService
from services.services.catalog_service import CatalogService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_algorithm_repository(db: Session = Depends(get_db)) -> AlgorithmRepository:
    return AlgorithmRepository(db)

def get_registry_service(repository: AlgorithmRepository = Depends(get_algorithm_repository)) -> RegistryService:
    return RegistryService(repository)

def get_catalog_service(repository: AlgorithmRepository = Depends(get_algorithm_repository)) -> CatalogService:
    return CatalogService(repository)

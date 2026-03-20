from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from services.library_platform.schemas.registry import AlgorithmDefinitionSchema

class AlgorithmSummary(BaseModel):
    code: str
    name: str
    category: Optional[str] = ""
    version: str
    status: str

class AlgorithmListResponse(BaseModel):
    items: List[AlgorithmSummary]
    total: int
    page: int
    page_size: int

class VersionSummary(BaseModel):
    version: str
    status: str
    name: str
    is_latest: bool

class VersionListResponse(BaseModel):
    code: str
    items: List[VersionSummary]

class ArtifactDetail(BaseModel):
    package_name: str
    repository_url: Optional[str]
    filename: Optional[str]
    sha256: Optional[str]

class VersionDetailResponse(BaseModel):
    code: str
    name: str
    version: str
    is_latest: bool
    status: str
    definition: AlgorithmDefinitionSchema
    artifact: ArtifactDetail

class AlgorithmDetailResponse(VersionDetailResponse):
    pass

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AlgorithmDefinitionSchema(BaseModel):
    code: str
    name: str
    version: str
    entrypoint: str
    category: Optional[str] = ""
    description: Optional[str] = ""
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    outputs: List[Dict[str, Any]] = Field(default_factory=list)
    params: List[Dict[str, Any]] = Field(default_factory=list)
    resources: Dict[str, Any] = Field(default_factory=dict)
    requirements: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class AlgorithmArtifactSchema(BaseModel):
    package_name: str
    package_version: Optional[str] = ""
    repository_url: Optional[str] = ""
    artifact_type: Optional[str] = ""
    filename: Optional[str] = ""
    sha256: Optional[str] = ""

class RegisterRequest(BaseModel):
    definition: AlgorithmDefinitionSchema
    artifact: AlgorithmArtifactSchema

class RegisterResponse(BaseModel):
    code: str
    name: str
    version: str
    status: str
    is_latest: bool
    registered_at: str

class ValidateResponse(BaseModel):
    valid: bool
    errors: Dict[str, List[str]]

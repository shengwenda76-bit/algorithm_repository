from typing import Any, Dict, Optional
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: Optional[Dict[str, Any]] = None

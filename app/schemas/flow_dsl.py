from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MappingRule(BaseModel):
    from_path: str = Field(alias="from", description="Path in the upstream output, e.g., 'dataset_ref'")
    to_path: str = Field(alias="to", description="Path in the downstream input, e.g., 'dataset_ref'")

    model_config = {
        "populate_by_name": True
    }

class FlowNode(BaseModel):
    node_id: str
    step_name: Optional[str] = None
    category: Optional[str] = None
    algo_code: str
    algo_version: str
    default_params: Dict[str, Any] = Field(default_factory=dict)
    timeout_sec: int = 60

class FlowEdge(BaseModel):
    from_node: str
    to_node: str
    mapping_rules: List[MappingRule] = Field(default_factory=list)

class FlowDSL(BaseModel):
    nodes: List[FlowNode]
    edges: List[FlowEdge] = Field(default_factory=list)
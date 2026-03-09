from pydantic import BaseModel, Field


class FlowNode(BaseModel):
    node_id: str
    algo_code: str
    algo_version: str
    params: dict = Field(default_factory=dict)


class FlowEdge(BaseModel):
    from_node: str
    to_node: str
    mapping_rules: list[dict] = Field(default_factory=list)


class FlowDSL(BaseModel):
    nodes: list[FlowNode]
    edges: list[FlowEdge]

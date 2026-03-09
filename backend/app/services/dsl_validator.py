import networkx as nx


def validate_flow(dsl: dict) -> tuple[bool, list[dict]]:
    graph = nx.DiGraph()
    for node in dsl.get("nodes", []):
        graph.add_node(node["node_id"])
    for edge in dsl.get("edges", []):
        graph.add_edge(edge["from_node"], edge["to_node"])
    if not nx.is_directed_acyclic_graph(graph):
        return False, [{"code": "FLOW_GRAPH_CYCLE", "message": "cycle detected in flow graph"}]
    return True, []

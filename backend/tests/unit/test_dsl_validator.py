from app.services.dsl_validator import validate_flow


def test_reject_cyclic_dag():
    dsl = {
        "nodes": [
            {
                "node_id": "A",
                "algo_code": "missing_value",
                "algo_version": "1.0.0",
                "params": {},
            },
            {
                "node_id": "B",
                "algo_code": "missing_value",
                "algo_version": "1.0.0",
                "params": {},
            },
        ],
        "edges": [
            {"from_node": "A", "to_node": "B", "mapping_rules": []},
            {"from_node": "B", "to_node": "A", "mapping_rules": []},
        ],
    }
    ok, errors = validate_flow(dsl)
    assert ok is False
    assert errors[0]["code"] == "FLOW_GRAPH_CYCLE"

from dataclasses import dataclass


@dataclass(frozen=True)
class AlgorithmVersion:
    algo_code: str
    version: str
    input_schema: dict
    output_schema: dict
    default_timeout_sec: int = 60


class AlgorithmRegistry:
    def __init__(self) -> None:
        self._versions = {
            ("missing_value", "1.0.0"): AlgorithmVersion(
                algo_code="missing_value",
                version="1.0.0",
                input_schema={
                    "type": "object",
                    "properties": {"dataset_ref": {"type": "string"}},
                },
                output_schema={
                    "type": "object",
                    "properties": {"dataset_ref": {"type": "string"}},
                },
                default_timeout_sec=60,
            )
        }

    def list_algorithms(self) -> dict:
        return {
            "categories": [
                {
                    "category_code": "data_cleaning",
                    "category_name": "Data Cleaning",
                    "algorithms": [
                        {
                            "algo_code": "missing_value",
                            "name": "Missing Value",
                            "latest_version": "1.0.0",
                            "status": "active",
                        }
                    ],
                }
            ]
        }

    def get_version(self, algo_code: str, version: str) -> AlgorithmVersion | None:
        return self._versions.get((algo_code, version))

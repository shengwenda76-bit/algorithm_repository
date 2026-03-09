from pydantic import BaseModel


class AlgorithmVersionResponse(BaseModel):
    algo_code: str
    version: str
    input_schema: dict
    output_schema: dict
    default_timeout_sec: int

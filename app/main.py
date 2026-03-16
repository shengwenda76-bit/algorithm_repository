"""FastAPI 应用入口。"""

from fastapi import FastAPI

from app.api.v1.router import router as api_router

app = FastAPI(
    title="Algorithm Platform",
    version="0.1.0",
    description="Scaffold for the algorithm scheduling and execution platform.",
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    """提供基础存活探针。"""

    return {"status": "ok"}

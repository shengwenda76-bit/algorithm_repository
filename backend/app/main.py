from fastapi import FastAPI

from app.api.routes.algorithms import router as algorithms_router

app = FastAPI(title="algorithm-platform")
app.include_router(algorithms_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

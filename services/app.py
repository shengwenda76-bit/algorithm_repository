import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from services.settings import settings
from services.database.migrations import init_db
from services.routers.registry import router as registry_router
from services.routers.catalog import router as catalog_router

logger = logging.getLogger(__name__)

def create_fastapi_app() -> FastAPI:
    # Initialize database
    init_db()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG
    )

    # Middleware for request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            # Log successful requests
            logger.info(
                f"{request.method} {request.url.path} "
                f"| status={response.status_code} "
                f"| duration={process_time:.2f}ms"
            )
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} "
                f"| status=500 "
                f"| duration={process_time:.2f}ms "
                f"| error={str(e)}"
            )
            # Re-raise to let exception handlers catch it, or return generic
            raise

    # Include routers
    app.include_router(registry_router)
    app.include_router(catalog_router)

    @app.get("/", tags=["health"])
    def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "healthy"
        }

    return app

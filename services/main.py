import uvicorn
from services.logging.setup import setup_logging
from services.settings import settings

# Setup logging immediately before anything else
setup_logging()

# Import create_app after logging setup so logger in dependencies are initialized
from services.app import create_fastapi_app

app = create_fastapi_app()

def main():
    uvicorn.run(
        "services.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    main()

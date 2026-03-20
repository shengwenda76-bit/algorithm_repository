from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path

from services.settings import settings

def get_database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("sqlite:///"):
        # ensure directories exist for sqlite file
        db_path = url.replace("sqlite:///", "")
        
        # if path is relative, resolve it against project root
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        if not os.path.isabs(db_path):
            real_path = project_root / db_path
        else:
            real_path = Path(db_path)
            
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(real_path), exist_ok=True)
        return f"sqlite:///{real_path.as_posix()}"
    return url

engine = create_engine(
    get_database_url(), 
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

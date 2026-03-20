from services.library_platform.database.base import engine, Base
# Import all models here so that Base.metadata.create_all recognizes them
import services.library_platform.models

import logging

logger = logging.getLogger(__name__)

def init_db():
    try:
        # Create all tables in the engine
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

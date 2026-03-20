import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "python-algorithm-library-platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database Config
    DATABASE_URL: str = "sqlite:///.runtime/library_platform/algorithm_library.db"

    # Logging Config
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = ".runtime/logs"
    LOG_FILENAME: str = "library_platform.log"
    LOG_BACKUP_DAYS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def get_log_file_path(self) -> str:
        # resolve against project root
        project_root = Path(__file__).resolve().parent.parent.parent
        log_dir_path = project_root / self.LOG_DIR
        return str(log_dir_path / self.LOG_FILENAME)

settings = Settings()

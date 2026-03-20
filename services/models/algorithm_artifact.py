from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from services.database.base import Base

class AlgorithmArtifact(Base):
    __tablename__ = "algorithm_artifacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    algorithm_code = Column(String(128), ForeignKey("algorithms.code"), index=True, nullable=False)
    version = Column(String(64), nullable=False)
    package_name = Column(String(256), nullable=False)
    package_version = Column(String(64), default="")
    repository_url = Column(String(512), default="")
    artifact_type = Column(String(64), default="")
    filename = Column(String(256), default="")
    sha256 = Column(String(64), default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    algorithm = relationship("Algorithm", back_populates="artifacts")

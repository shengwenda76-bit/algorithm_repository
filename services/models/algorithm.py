from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from services.database.base import Base

class Algorithm(Base):
    __tablename__ = "algorithms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    category = Column(String(128), default="")
    description = Column(Text, default="")
    status = Column(String(32), default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    versions = relationship("AlgorithmVersion", back_populates="algorithm", cascade="all, delete-orphan")
    artifacts = relationship("AlgorithmArtifact", back_populates="algorithm", cascade="all, delete-orphan")

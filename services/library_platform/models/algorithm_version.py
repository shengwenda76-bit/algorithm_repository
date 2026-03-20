from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from services.library_platform.database.base import Base

class AlgorithmVersion(Base):
    __tablename__ = "algorithm_versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    algorithm_code = Column(String(128), ForeignKey("algorithms.code"), index=True, nullable=False)
    version = Column(String(64), nullable=False)
    entrypoint = Column(String(512), nullable=False)
    inputs_json = Column(Text, default="[]")
    outputs_json = Column(Text, default="[]")
    params_json = Column(Text, default="[]")
    resources_json = Column(Text, default="{}")
    requirements_json = Column(Text, default="[]")
    tags_json = Column(Text, default="[]")
    status = Column(String(32), default="registered")
    is_latest = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('algorithm_code', 'version', name='uq_algorithm_version'),
    )

    algorithm = relationship("Algorithm", back_populates="versions")

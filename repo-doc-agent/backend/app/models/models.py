from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())


class MonitoringStatus(str, enum.Enum):
    """Monitoring job status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisStatus(str, enum.Enum):
    """Repository analysis status enum"""
    PENDING = "pending"
    CLONING = "cloning"
    ANALYZING = "analyzing"
    GENERATING_DOCS = "generating_docs"
    COMPLETED = "completed"
    FAILED = "failed"


class Repository(Base):
    """Repository model - stores repo metadata"""
    __tablename__ = "repositories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    url = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Git info
    last_commit_hash = Column(String, nullable=True)
    branch = Column(String, default="main")
    
    # Status
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    # Monitoring
    monitoring_enabled = Column(Boolean, default=True)
    webhook_id = Column(String, nullable=True)  # GitHub/GitLab webhook ID
    
    # Timestamps
    last_analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    documentation = relationship("Documentation", back_populates="repository", cascade="all, delete-orphan")
    snapshots = relationship("CodeSnapshot", back_populates="repository", cascade="all, delete-orphan")
    monitoring_jobs = relationship("MonitoringJob", back_populates="repository", cascade="all, delete-orphan")


class Documentation(Base):
    """Documentation model - stores generated docs (versioned)"""
    __tablename__ = "documentation"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    repo_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    # Version control
    version = Column(Integer, nullable=False)
    commit_hash = Column(String, nullable=False)
    
    # Documentation content (JSON structure)
    content = Column(JSON, nullable=False)
    # Structure:
    # {
    #   "executive_summary": str,
    #   "product_overview": str,
    #   "key_features": List[str],
    #   "tech_stack": Dict[str, List[str]],
    #   "architecture": str (Mermaid diagram),
    #   "use_cases": List[str],
    #   "integrations": List[str],
    #   "marketing_points": List[str]
    # }
    
    # Metadata
    file_count = Column(Integer, default=0)
    lines_of_code = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="documentation")


class CodeSnapshot(Base):
    """Code snapshot model - stores file hashes for delta detection"""
    __tablename__ = "code_snapshots"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    repo_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    # File info
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)  # SHA256 hash
    file_size = Column(Integer, default=0)
    
    # Analysis result for this file
    analysis_result = Column(JSON, nullable=True)
    # Structure:
    # {
    #   "language": str,
    #   "functions": List[str],
    #   "classes": List[str],
    #   "imports": List[str],
    #   "complexity": int,
    #   "summary": str
    # }
    
    # Version
    commit_hash = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="snapshots")


class MonitoringJob(Base):
    """Monitoring job model - tracks webhook-triggered updates"""
    __tablename__ = "monitoring_jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    repo_id = Column(String, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    # Job info
    status = Column(Enum(MonitoringStatus), default=MonitoringStatus.PENDING)
    trigger_type = Column(String, default="webhook")  # webhook, manual, scheduled
    
    # Changes detected
    changes_detected = Column(JSON, nullable=True)
    # Structure:
    # {
    #   "added": List[str],
    #   "modified": List[str],
    #   "deleted": List[str],
    #   "commit_hash": str,
    #   "commit_message": str
    # }
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="monitoring_jobs")

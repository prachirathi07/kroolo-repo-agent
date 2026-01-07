import uuid
import enum

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

# Note: SQLAlchemy models have been removed in favor of Supabase Client (REST API).
# Use app.schemas.schemas for data validation and structure.


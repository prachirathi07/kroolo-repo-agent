from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class AnalysisStatusEnum(str, Enum):
    PENDING = "pending"
    CLONING = "cloning"
    ANALYZING = "analyzing"
    GENERATING_DOCS = "generating_docs"
    COMPLETED = "completed"
    FAILED = "failed"


class MonitoringStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Repository Schemas
class RepositoryCreate(BaseModel):
    """Schema for creating a new repository"""
    url: str = Field(..., description="Git repository URL (GitHub/GitLab)")
    auth_token: Optional[str] = Field(None, description="Personal access token for private repos")
    branch: str = Field("main", description="Branch to analyze")
    monitoring_enabled: bool = Field(True, description="Enable continuous monitoring")


class RepositoryResponse(BaseModel):
    """Schema for repository response"""
    id: str
    url: str
    name: Optional[str]
    description: Optional[str]
    status: AnalysisStatusEnum
    last_commit_hash: Optional[str]
    branch: str
    monitoring_enabled: bool
    webhook_id: Optional[str]
    error_message: Optional[str]
    last_analyzed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RepositoryList(BaseModel):
    """Schema for list of repositories"""
    repositories: List[RepositoryResponse]
    total: int


# Documentation Schemas
class DocumentationContent(BaseModel):
    """Schema for documentation content structure"""
    executive_summary: str
    product_overview: str
    key_features: List[str]
    tech_stack: Dict[str, List[str]]
    architecture: str  # Mermaid diagram syntax
    use_cases: List[str]
    integrations: List[str]
    marketing_points: List[str]


class DocumentationResponse(BaseModel):
    """Schema for documentation response"""
    id: str
    repo_id: str
    version: int
    commit_hash: str
    content: DocumentationContent
    file_count: int
    lines_of_code: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentationVersionList(BaseModel):
    """Schema for list of documentation versions"""
    versions: List[DocumentationResponse]
    total: int


# Monitoring Schemas
class ChangesDetected(BaseModel):
    """Schema for detected changes"""
    added: List[str]
    modified: List[str]
    deleted: List[str]
    commit_hash: str
    commit_message: str


class MonitoringJobResponse(BaseModel):
    """Schema for monitoring job response"""
    id: str
    repo_id: str
    status: MonitoringStatusEnum
    trigger_type: str
    changes_detected: Optional[ChangesDetected]
    error_message: Optional[str]
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MonitoringJobList(BaseModel):
    """Schema for list of monitoring jobs"""
    jobs: List[MonitoringJobResponse]
    total: int


# Webhook Schemas
class GitHubWebhookPayload(BaseModel):
    """Schema for GitHub webhook payload (simplified)"""
    ref: str
    repository: Dict[str, Any]
    commits: List[Dict[str, Any]]
    head_commit: Dict[str, Any]


class GitLabWebhookPayload(BaseModel):
    """Schema for GitLab webhook payload (simplified)"""
    ref: str
    project: Dict[str, Any]
    commits: List[Dict[str, Any]]


# Analysis Schemas
class AnalysisProgress(BaseModel):
    """Schema for analysis progress updates"""
    repo_id: str
    status: AnalysisStatusEnum
    progress_percentage: int
    current_step: str
    message: str


class AnalysisResult(BaseModel):
    """Schema for analysis result"""
    success: bool
    repo_id: str
    documentation_id: Optional[str]
    error: Optional[str]
    duration_seconds: float


# Export Schemas
class ExportFormat(str, Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"


class ExportRequest(BaseModel):
    """Schema for export request"""
    format: ExportFormat
    include_diagrams: bool = True

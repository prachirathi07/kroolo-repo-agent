from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.schemas import (
    RepositoryCreate,
    RepositoryResponse,
    RepositoryList,
    AnalysisResult
)
from app.models.models import Repository, Documentation, AnalysisStatus
from app.agents.graph import run_analysis
from app.core.logger import logger
import uuid

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_repository(
    repo_data: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start analysis of a new repository
    
    This endpoint creates a repository record and triggers
    the LangGraph analysis workflow in the background.
    """
    try:
        # Check if repository already exists
        existing_repo = db.query(Repository).filter(
            Repository.url == repo_data.url
        ).first()
        
        if existing_repo:
            return AnalysisResult(
                success=False,
                repo_id=existing_repo.id,
                documentation_id=None,
                error="Repository already exists. Use incremental update instead.",
                duration_seconds=0.0
            )
        
        # Create repository record
        repo_id = str(uuid.uuid4())
        new_repo = Repository(
            id=repo_id,
            url=repo_data.url,
            branch=repo_data.branch,
            monitoring_enabled=repo_data.monitoring_enabled,
            status=AnalysisStatus.PENDING
        )
        
        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)
        
        logger.info(f"Created repository record: {repo_id}")
        
        # Trigger analysis in background
        background_tasks.add_task(
            analyze_repository_task,
            repo_id=repo_id,
            repo_url=repo_data.url,
            branch=repo_data.branch,
            auth_token=repo_data.auth_token
        )
        
        return AnalysisResult(
            success=True,
            repo_id=repo_id,
            documentation_id=None,
            error=None,
            duration_seconds=0.0
        )
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_repository_task(
    repo_id: str,
    repo_url: str,
    branch: str,
    auth_token: str = None
):
    """Background task to run repository analysis"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Update status to analyzing
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        repo.status = AnalysisStatus.ANALYZING
        db.commit()
        
        logger.info(f"Starting analysis for repository: {repo_id}")
        
        # Run LangGraph analysis
        import time
        start_time = time.time()
        
        final_state = await run_analysis(
            repo_url=repo_url,
            repo_id=repo_id,
            branch=branch,
            auth_token=auth_token
        )
        
        duration = time.time() - start_time
        
        # Check for errors
        if final_state.get("errors"):
            repo.status = AnalysisStatus.FAILED
            repo.error_message = "; ".join(final_state["errors"])
            db.commit()
            logger.error(f"Analysis failed for {repo_id}: {repo.error_message}")
            return
        
        # Update repository with results
        repo.name = final_state.get("repo_name")
        repo.description = final_state.get("repo_description")
        repo.last_commit_hash = final_state.get("current_commit_hash")
        repo.status = AnalysisStatus.COMPLETED
        repo.last_analyzed_at = db.query(Repository).filter(Repository.id == repo_id).first().updated_at
        db.commit()
        
        # Create documentation record
        doc_content = {
            "executive_summary": final_state.get("executive_summary", ""),
            "product_overview": final_state.get("product_overview", ""),
            "key_features": final_state.get("features", []),
            "tech_stack": final_state.get("tech_stack", {}),
            "architecture": final_state.get("architecture_diagram", ""),
            "use_cases": final_state.get("use_cases", []),
            "integrations": final_state.get("integrations", []),
            "marketing_points": final_state.get("marketing_points", [])
        }
        
        documentation = Documentation(
            id=str(uuid.uuid4()),
            repo_id=repo_id,
            version=1,
            commit_hash=final_state.get("current_commit_hash"),
            content=doc_content,
            file_count=final_state.get("total_files", 0),
            lines_of_code=final_state.get("total_lines_of_code", 0)
        )
        
        db.add(documentation)
        db.commit()
        
        logger.info(f"Analysis completed for {repo_id} in {duration:.2f}s")
        
    except Exception as e:
        logger.error(f"Analysis task failed: {str(e)}")
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if repo:
            repo.status = AnalysisStatus.FAILED
            repo.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.get("", response_model=RepositoryList)
async def list_repositories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all repositories"""
    try:
        repositories = db.query(Repository).order_by(Repository.created_at.desc()).offset(skip).limit(limit).all()
        total = db.query(Repository).count()
        
        return RepositoryList(
            repositories=repositories,
            total=total
        )
    except Exception as e:
        logger.error(f"Database error in list_repositories: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Database connection failed",
                "message": "Please check your DATABASE_URL in the backend/.env file",
                "hint": "Make sure your Supabase/PostgreSQL credentials are correct"
            }
        )


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(repo_id: str, db: Session = Depends(get_db)):
    """Get repository by ID"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return repo


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str, db: Session = Depends(get_db)):
    """Delete repository and all associated data"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Delete from database (cascade will handle related records)
    db.delete(repo)
    db.commit()
    
    # Cleanup cloned files
    from app.services.git_service import git_service
    git_service.cleanup_repository(repo_id)
    
    return {"message": "Repository deleted successfully"}

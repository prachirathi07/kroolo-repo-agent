from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.schemas import (
    RepositoryCreate,
    RepositoryResponse,
    RepositoryList,
    AnalysisResult
)
from app.models.models import AnalysisStatus
from app.agents.graph import run_analysis
from app.core.logger import logger
import uuid
from datetime import datetime
import time

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_repository(
    repo_data: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Start analysis of a new repository
    
    This endpoint creates a repository record and triggers
    the LangGraph analysis workflow in the background.
    """
    try:
        # Check if repository already exists
        response = db.table("repositories").select("*").eq("url", repo_data.url).execute()
        existing_repo = response.data[0] if response.data else None
        
        if existing_repo:
            return AnalysisResult(
                success=False,
                repo_id=existing_repo['id'],
                documentation_id=None,
                error="Repository already exists. Use incremental update instead.",
                duration_seconds=0.0
            )
        
        # Create repository record
        repo_id = str(uuid.uuid4())
        new_repo = {
            "id": repo_id,
            "url": repo_data.url,
            "branch": repo_data.branch or "main",
            "monitoring_enabled": repo_data.monitoring_enabled,
            "status": AnalysisStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        db.table("repositories").insert(new_repo).execute()
        
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
    """Background task to run repository analysis (Supabase version)"""
    # Import locally to avoid circular imports or init issues
    from app.core.database import get_db
    db = get_db()
    
    try:
        # Update status to analyzing
        db.table("repositories").update({
            "status": AnalysisStatus.ANALYZING,
            "updated_at": datetime.now().isoformat()
        }).eq("id", repo_id).execute()
        
        logger.info(f"Starting analysis for repository: {repo_id}")
        
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
            error_msg = "; ".join(final_state["errors"])
            db.table("repositories").update({
                "status": AnalysisStatus.FAILED,
                "error_message": error_msg,
                "updated_at": datetime.now().isoformat()
            }).eq("id", repo_id).execute()
            
            logger.error(f"Analysis failed for {repo_id}: {error_msg}")
            return
        
        # Update repository with results
        db.table("repositories").update({
            "name": final_state.get("repo_name"),
            "description": final_state.get("repo_description"),
            "last_commit_hash": final_state.get("current_commit_hash"),
            "status": AnalysisStatus.COMPLETED,
            "last_analyzed_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }).eq("id", repo_id).execute()
        
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
        
        new_doc = {
            "id": str(uuid.uuid4()),
            "repo_id": repo_id,
            "version": 1,
            "commit_hash": final_state.get("current_commit_hash"),
            "content": doc_content,
            "file_count": final_state.get("total_files", 0),
            "lines_of_code": final_state.get("total_lines_of_code", 0),
            "created_at": datetime.now().isoformat()
        }
        
        db.table("documentation").insert(new_doc).execute()
        
        logger.info(f"Analysis completed for {repo_id} in {duration:.2f}s")
        
    except Exception as e:
        logger.error(f"Analysis task failed: {str(e)}")
        # Try to update status if possible
        try:
            db.table("repositories").update({
                "status": AnalysisStatus.FAILED,
                "error_message": str(e)
            }).eq("id", repo_id).execute()
        except:
            pass 


@router.get("", response_model=RepositoryList)
async def list_repositories(
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db)
):
    """Get list of all repositories"""
    try:
        # Supabase select with count
        response = db.table("repositories").select("*", count="exact").order("created_at", desc=True).range(skip, skip + limit - 1).execute()
        
        repositories = response.data
        total = response.count or 0
        
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
                "message": str(e)
            }
        )


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(repo_id: str, db = Depends(get_db)):
    """Get repository by ID"""
    response = db.table("repositories").select("*").eq("id", repo_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return response.data[0]


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str, db = Depends(get_db)):
    """Delete repository and all associated data"""
    # Check existence
    response = db.table("repositories").select("id").eq("id", repo_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Delete (Cascade in Supabase handles related records if configured, otherwise might need manual delete)
    # Assuming ON DELETE CASCADE is set in SQL definition
    db.table("repositories").delete().eq("id", repo_id).execute()
    
    # Cleanup cloned files
    from app.services.git_service import git_service
    git_service.cleanup_repository(repo_id)
    
    return {"message": "Repository deleted successfully"}


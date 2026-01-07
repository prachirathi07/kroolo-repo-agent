from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.schemas.schemas import MonitoringJobList

router = APIRouter()


@router.get("/jobs", response_model=MonitoringJobList)
async def get_monitoring_jobs(
    skip: int = 0,
    limit: int = 50,
    db = Depends(get_db)
):
    """
    Get list of monitoring jobs
    """
    response = db.table("monitoring_jobs").select("*", count="exact").order("created_at", desc=True).range(skip, skip + limit - 1).execute()
    
    jobs = response.data
    total = response.count or 0
    
    return MonitoringJobList(
        jobs=jobs,
        total=total
    )


@router.get("/jobs/{job_id}")
async def get_monitoring_job(job_id: str, db = Depends(get_db)):
    """
    Get monitoring job by ID
    """
    response = db.table("monitoring_jobs").select("*").eq("id", job_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return response.data[0]


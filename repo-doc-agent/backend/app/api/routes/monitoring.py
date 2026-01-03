from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import MonitoringJobList
from app.models.models import MonitoringJob

router = APIRouter()


@router.get("/jobs", response_model=MonitoringJobList)
async def get_monitoring_jobs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get list of monitoring jobs
    """
    jobs = db.query(MonitoringJob).order_by(
        MonitoringJob.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    total = db.query(MonitoringJob).count()
    
    return MonitoringJobList(
        jobs=jobs,
        total=total
    )


@router.get("/jobs/{job_id}")
async def get_monitoring_job(job_id: str, db: Session = Depends(get_db)):
    """
    Get monitoring job by ID
    """
    job = db.query(MonitoringJob).filter(MonitoringJob.id == job_id).first()
    
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

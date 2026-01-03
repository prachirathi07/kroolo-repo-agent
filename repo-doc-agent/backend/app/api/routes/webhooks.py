from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.logger import logger

router = APIRouter()


@router.post("/github")
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle GitHub webhook events
    
    TODO: Implement full webhook handling in Phase 4
    - Verify webhook signature
    - Parse push event
    - Trigger incremental analysis
    """
    try:
        payload = await request.json()
        logger.info(f"Received GitHub webhook: {payload.get('ref', 'unknown')}")
        
        # TODO: Implement webhook processing
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"GitHub webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gitlab")
async def gitlab_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle GitLab webhook events
    
    TODO: Implement full webhook handling in Phase 4
    """
    try:
        payload = await request.json()
        logger.info(f"Received GitLab webhook: {payload.get('ref', 'unknown')}")
        
        # TODO: Implement webhook processing
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"GitLab webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

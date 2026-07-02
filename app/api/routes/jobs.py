from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.database.session import get_db
from app.database.models import User, Workspace, Job
from app.api.dependencies import get_current_user
from app.workflows.pipeline import PipelineOrchestrator
from app.core.logger import get_logger

logger = get_logger("job_router")

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobCreate(BaseModel):
    job_type: str  # full_pipeline, google_maps_search, lead_enrichment, ai_analysis
    query: Optional[str] = None
    location: Optional[str] = None
    max_leads: int = 100
    source: str = "google_maps"


class JobResponse(BaseModel):
    id: int
    job_type: str
    status: str
    progress: int
    total_items: int
    processed_items: int
    result: dict = None
    error_message: str = None
    started_at: datetime = None
    completed_at: datetime = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_job(
    workspace_id: int,
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create and start a new job."""
    # Verify workspace access
    result = await session.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == current_user.id
        )
    )
    workspace = result.scalar_one_or_none()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    orchestrator = PipelineOrchestrator(session)
    
    try:
        if job_data.job_type == "full_pipeline":
            result = await orchestrator.run_full_pipeline(
                workspace_id=workspace_id,
                query=job_data.query or "businesses",
                location=job_data.location,
                max_leads=job_data.max_leads
            )
        elif job_data.job_type == "google_maps_search":
            result = await orchestrator.run_collection_only(
                workspace_id=workspace_id,
                query=job_data.query or "businesses",
                location=job_data.location,
                max_leads=job_data.max_leads,
                source=job_data.source
            )
        elif job_data.job_type == "lead_enrichment":
            result = await orchestrator.run_enrichment(
                workspace_id=workspace_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown job type: {job_data.job_type}"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Job creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    workspace_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all jobs for a workspace."""
    # Verify workspace access
    result = await session.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == current_user.id
        )
    )
    workspace = result.scalar_one_or_none()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    from app.database.repository.job_repository import JobRepository
    job_repo = JobRepository(session)
    jobs, _ = await job_repo.get_all(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    workspace_id: int,
    job_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific job."""
    # Verify workspace access
    result = await session.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == current_user.id
        )
    )
    workspace = result.scalar_one_or_none()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    from app.database.repository.job_repository import JobRepository
    job_repo = JobRepository(session)
    job = await job_repo.get_by_id(job_id, workspace_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.post("/{job_id}/cancel")
async def cancel_job(
    workspace_id: int,
    job_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a running job."""
    # Verify workspace access
    result = await session.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == current_user.id
        )
    )
    workspace = result.scalar_one_or_none()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    from app.database.repository.job_repository import JobRepository
    job_repo = JobRepository(session)
    job = await job_repo.cancel_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {"message": "Job cancelled", "job_id": job_id}

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.database.session import get_db
from app.database.models import User, Lead, Workspace
from app.database.repository.lead_repository import LeadRepository
from app.api.dependencies import get_current_user
from app.schemas.lead import (
    LeadCreate, LeadUpdate, LeadResponse, LeadDetailResponse,
    LeadBulkCreate, LeadBulkStatusUpdate, LeadStatsResponse, LeadSearchResponse
)
from app.core.logger import get_logger

logger = get_logger("lead_router")

router = APIRouter(prefix="/leads", tags=["Leads"])


async def get_workspace_or_404(
    workspace_id: int,
    session: AsyncSession,
    current_user: User
) -> Workspace:
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
    return workspace


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    workspace_id: int,
    lead_data: LeadCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    
    # Check for duplicate domain
    if lead_data.domain:
        existing = await lead_repo.get_by_domain(lead_data.domain, workspace_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lead with domain {lead_data.domain} already exists"
            )
    
    lead = await lead_repo.create(workspace_id=workspace_id, **lead_data.model_dump())
    
    logger.info(f"Lead created: {lead.id} in workspace {workspace_id}")
    return lead


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_leads(
    workspace_id: int,
    bulk_data: LeadBulkCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    leads_data = [lead.model_dump() for lead in bulk_data.leads]
    leads = await lead_repo.bulk_create(workspace_id, leads_data)
    
    logger.info(f"Bulk created {len(leads)} leads in workspace {workspace_id}")
    
    return {"message": f"Created {len(leads)} leads", "count": len(leads)}


@router.get("/", response_model=LeadSearchResponse)
async def list_leads(
    workspace_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    quality_tier: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    leads, total = await lead_repo.get_all(
        workspace_id=workspace_id,
        skip=skip,
        limit=limit,
        status=status,
        quality_tier=quality_tier,
        min_score=min_score
    )
    
    return LeadSearchResponse(
        leads=[LeadResponse.model_validate(lead) for lead in leads],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/stats", response_model=LeadStatsResponse)
async def get_lead_stats(
    workspace_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    stats = await lead_repo.get_stats(workspace_id)
    
    return LeadStatsResponse(**stats)


@router.get("/search")
async def search_leads(
    workspace_id: int,
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    leads = await lead_repo.search(workspace_id, q, skip, limit)
    
    return {
        "leads": [LeadResponse.model_validate(lead) for lead in leads],
        "total": len(leads)
    }


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(
    workspace_id: int,
    lead_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    lead = await lead_repo.get_by_id(lead_id, workspace_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    workspace_id: int,
    lead_id: int,
    lead_data: LeadUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    lead = await lead_repo.get_by_id(lead_id, workspace_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    update_data = lead_data.model_dump(exclude_unset=True)
    updated_lead = await lead_repo.update(lead_id, **update_data)
    
    logger.info(f"Lead updated: {lead_id}")
    return updated_lead


@router.patch("/bulk/status", response_model=dict)
async def bulk_update_status(
    workspace_id: int,
    bulk_data: LeadBulkStatusUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    count = await lead_repo.bulk_update_status(bulk_data.lead_ids, bulk_data.status)
    
    logger.info(f"Bulk updated {count} leads to status {bulk_data.status}")
    
    return {"message": f"Updated {count} leads", "count": count}


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    workspace_id: int,
    lead_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await get_workspace_or_404(workspace_id, session, current_user)
    
    lead_repo = LeadRepository(session)
    lead = await lead_repo.get_by_id(lead_id, workspace_id)
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    await lead_repo.delete(lead_id)
    
    logger.info(f"Lead deleted: {lead_id}")

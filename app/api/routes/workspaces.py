from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database.session import get_db
from app.database.models import User, Workspace
from app.api.dependencies import get_current_user
from app.core.logger import get_logger

logger = get_logger("workspace_router")

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


class WorkspaceCreate(BaseModel):
    name: str
    description: str = None


class WorkspaceUpdate(BaseModel):
    name: str = None
    description: str = None


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    owner_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Generate slug from name
    slug = workspace_data.name.lower().replace(" ", "-")
    slug = "".join(c if c.isalnum() or c in "-_" else "" for c in slug)
    
    # Check if slug exists
    result = await session.execute(select(Workspace).where(Workspace.slug == slug))
    if result.scalar_one_or_none():
        # Add random suffix
        import random
        slug = f"{slug}-{random.randint(1000, 9999)}"
    
    workspace = Workspace(
        name=workspace_data.name,
        slug=slug,
        description=workspace_data.description,
        owner_id=current_user.id
    )
    session.add(workspace)
    await session.commit()
    await session.refresh(workspace)
    
    logger.info(f"Workspace created: {workspace.name} by {current_user.email}")
    return workspace


@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(Workspace).where(Workspace.owner_id == current_user.id)
    )
    return list(result.scalars().all())


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    
    if workspace_data.name is not None:
        workspace.name = workspace_data.name
    if workspace_data.description is not None:
        workspace.description = workspace_data.description
    
    await session.commit()
    await session.refresh(workspace)
    
    logger.info(f"Workspace updated: {workspace.name}")
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    
    await session.delete(workspace)
    await session.commit()
    
    logger.info(f"Workspace deleted: {workspace_id}")

from typing import Optional, List, Tuple
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database.models import Lead, LeadStatus
from app.core.logger import get_logger

logger = get_logger("lead_repository")


class LeadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workspace_id: int, **kwargs) -> Lead:
        lead = Lead(workspace_id=workspace_id, **kwargs)
        self.session.add(lead)
        await self.session.flush()
        await self.session.refresh(lead)
        logger.info(f"Created lead: {lead.id} for workspace: {workspace_id}")
        return lead

    async def get_by_id(self, lead_id: int, workspace_id: Optional[int] = None) -> Optional[Lead]:
        query = select(Lead).where(Lead.id == lead_id)
        if workspace_id:
            query = query.where(Lead.workspace_id == workspace_id)
        result = await self.session.execute(query.options(
            selectinload(Lead.website),
            selectinload(Lead.contacts),
            selectinload(Lead.ai_report),
            selectinload(Lead.social_profiles)
        ))
        return result.scalar_one_or_none()

    async def get_by_domain(self, domain: str, workspace_id: int) -> Optional[Lead]:
        result = await self.session.execute(
            select(Lead).where(
                and_(Lead.domain == domain, Lead.workspace_id == workspace_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        quality_tier: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> Tuple[List[Lead], int]:
        query = select(Lead).where(Lead.workspace_id == workspace_id)
        count_query = select(func.count(Lead.id)).where(Lead.workspace_id == workspace_id)
        
        if status:
            query = query.where(Lead.status == status)
            count_query = count_query.where(Lead.status == status)
        
        if quality_tier:
            query = query.where(Lead.quality_tier == quality_tier)
            count_query = count_query.where(Lead.quality_tier == quality_tier)
        
        if min_score is not None:
            query = query.where(Lead.ai_score >= min_score)
            count_query = count_query.where(Lead.ai_score >= min_score)
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query.options(
            selectinload(Lead.website),
            selectinload(Lead.contacts),
            selectinload(Lead.ai_report)
        ))
        leads = list(result.scalars().all())
        
        return leads, total

    async def update(self, lead_id: int, **kwargs) -> Optional[Lead]:
        await self.session.execute(
            update(Lead).where(Lead.id == lead_id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(lead_id)

    async def update_status(self, lead_id: int, status: str) -> Optional[Lead]:
        return await self.update(lead_id, status=status)

    async def update_score(self, lead_id: int, score: float, quality_tier: str) -> Optional[Lead]:
        return await self.update(lead_id, ai_score=score, quality_tier=quality_tier)

    async def delete(self, lead_id: int) -> bool:
        result = await self.session.execute(
            delete(Lead).where(Lead.id == lead_id)
        )
        return result.rowcount > 0

    async def bulk_create(self, workspace_id: int, leads_data: List[dict]) -> List[Lead]:
        leads = [Lead(workspace_id=workspace_id, **data) for data in leads_data]
        self.session.add_all(leads)
        await self.session.flush()
        logger.info(f"Bulk created {len(leads)} leads for workspace: {workspace_id}")
        return leads

    async def bulk_update_status(self, lead_ids: List[int], status: str) -> int:
        result = await self.session.execute(
            update(Lead).where(Lead.id.in_(lead_ids)).values(status=status)
        )
        await self.session.flush()
        return result.rowcount

    async def search(
        self,
        workspace_id: int,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Lead]:
        search_pattern = f"%{query}%"
        result = await self.session.execute(
            select(Lead).where(
                and_(
                    Lead.workspace_id == workspace_id,
                    or_(
                        Lead.name.ilike(search_pattern),
                        Lead.company_name.ilike(search_pattern),
                        Lead.domain.ilike(search_pattern),
                        Lead.description.ilike(search_pattern)
                    )
                )
            ).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(self, workspace_id: int) -> dict:
        total_result = await self.session.execute(
            select(func.count(Lead.id)).where(Lead.workspace_id == workspace_id)
        )
        total = total_result.scalar() or 0
        
        # Status breakdown
        status_counts = {}
        for status in LeadStatus:
            result = await self.session.execute(
                select(func.count(Lead.id)).where(
                    and_(Lead.workspace_id == workspace_id, Lead.status == status.value)
                )
            )
            status_counts[status.value] = result.scalar() or 0
        
        # Quality tier breakdown
        tier_counts = {}
        for tier in ['A', 'B', 'C', 'D']:
            result = await self.session.execute(
                select(func.count(Lead.id)).where(
                    and_(Lead.workspace_id == workspace_id, Lead.quality_tier == tier)
                )
            )
            tier_counts[tier] = result.scalar() or 0
        
        # Average score
        avg_score_result = await self.session.execute(
            select(func.avg(Lead.ai_score)).where(
                and_(Lead.workspace_id == workspace_id, Lead.ai_score.isnot(None))
            )
        )
        avg_score = avg_score_result.scalar()
        
        return {
            "total": total,
            "by_status": status_counts,
            "by_quality_tier": tier_counts,
            "average_score": float(avg_score) if avg_score else 0
        }

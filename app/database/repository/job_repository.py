from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Job, JobStatus, JobType
from app.core.logger import get_logger

logger = get_logger("job_repository")


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workspace_id: int, job_type: str, **kwargs) -> Job:
        job = Job(
            workspace_id=workspace_id,
            job_type=job_type,
            **kwargs
        )
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        logger.info(f"Created job: {job.id} of type: {job_type}")
        return job

    async def get_by_id(self, job_id: int, workspace_id: Optional[int] = None) -> Optional[Job]:
        query = select(Job).where(Job.id == job_id)
        if workspace_id:
            query = query.where(Job.workspace_id == workspace_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> Tuple[List[Job], int]:
        query = select(Job).where(Job.workspace_id == workspace_id)
        count_query = select(func.count(Job.id)).where(Job.workspace_id == workspace_id)
        
        if status:
            query = query.where(Job.status == status)
            count_query = count_query.where(Job.status == status)
        
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0
        
        query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        jobs = list(result.scalars().all())
        
        return jobs, total

    async def get_running_jobs(self, workspace_id: int) -> List[Job]:
        result = await self.session.execute(
            select(Job).where(
                and_(
                    Job.workspace_id == workspace_id,
                    Job.status == JobStatus.RUNNING.value
                )
            )
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        job_id: int,
        status: str,
        error_message: Optional[str] = None,
        **kwargs
    ) -> Optional[Job]:
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message
        update_data.update(kwargs)
        
        await self.session.execute(
            update(Job).where(Job.id == job_id).values(**update_data)
        )
        await self.session.flush()
        return await self.get_by_id(job_id)

    async def start_job(self, job_id: int) -> Optional[Job]:
        return await self.update_status(job_id, JobStatus.RUNNING.value, started_at=datetime.utcnow())

    async def complete_job(self, job_id: int, result: dict = None) -> Optional[Job]:
        update_data = {
            "status": JobStatus.COMPLETED.value,
            "completed_at": datetime.utcnow(),
            "progress": 100
        }
        if result:
            update_data["result"] = result
        
        await self.session.execute(
            update(Job).where(Job.id == job_id).values(**update_data)
        )
        await self.session.flush()
        return await self.get_by_id(job_id)

    async def fail_job(self, job_id: int, error_message: str) -> Optional[Job]:
        return await self.update_status(
            job_id,
            JobStatus.FAILED.value,
            error_message=error_message,
            completed_at=datetime.utcnow()
        )

    async def update_progress(self, job_id: int, processed_items: int, total_items: int) -> Optional[Job]:
        progress = int((processed_items / total_items) * 100) if total_items > 0 else 0
        await self.session.execute(
            update(Job).where(Job.id == job_id).values(
                processed_items=processed_items,
                total_items=total_items,
                progress=progress
            )
        )
        await self.session.flush()
        return await self.get_by_id(job_id)

    async def cancel_job(self, job_id: int) -> Optional[Job]:
        return await self.update_status(
            job_id,
            JobStatus.CANCELLED.value,
            completed_at=datetime.utcnow()
        )

    async def delete(self, job_id: int) -> bool:
        result = await self.session.execute(
            delete(Job).where(Job.id == job_id)
        )
        return result.rowcount > 0

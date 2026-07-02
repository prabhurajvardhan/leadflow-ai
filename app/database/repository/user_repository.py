from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from app.core.logger import get_logger

logger = get_logger("user_repository")


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, username: str, hashed_password: str, **kwargs) -> User:
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            **kwargs
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        logger.info(f"Created user: {user.id}")
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, user_id: int, **kwargs) -> Optional[User]:
        await self.session.execute(
            update(User).where(User.id == user_id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        result = await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        return result.rowcount > 0

    async def exists_by_email(self, email: str) -> bool:
        result = await self.session.execute(
            select(User.id).where(User.email == email).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        result = await self.session.execute(
            select(User.id).where(User.username == username).limit(1)
        )
        return result.scalar_one_or_none() is not None

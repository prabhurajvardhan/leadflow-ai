from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from app.database.session import get_db
from app.database.models import User, RefreshToken
from app.database.repository.user_repository import UserRepository
from app.schemas.user import (
    UserCreate, UserResponse, UserInDB, LoginRequest, Token, TokenRefresh
)
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, verify_refresh_token
)
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("auth_router")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(session)
    
    # Check if email exists
    if await user_repo.exists_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username exists
    if await user_repo.exists_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = await user_repo.create(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    logger.info(f"User registered: {user.email}")
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(login_data.email)
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    await user_repo.update(user.id, last_login=datetime.utcnow())
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=expires_at
    )
    session.add(db_refresh_token)
    await session.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    session: AsyncSession = Depends(get_db)
):
    payload = verify_refresh_token(token_data.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    
    # Verify token exists in database and is not revoked
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token == token_data.refresh_token,
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or expired"
        )
    
    # Revoke old refresh token
    db_token.revoked = True
    
    # Get user
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store new refresh token
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    new_db_refresh_token = RefreshToken(
        token=new_refresh_token,
        user_id=user.id,
        expires_at=expires_at
    )
    session.add(new_db_refresh_token)
    await session.commit()
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout")
async def logout(
    token_data: TokenRefresh,
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token == token_data.refresh_token)
    )
    db_token = result.scalar_one_or_none()
    
    if db_token:
        db_token.revoked = True
        await session.commit()
    
    logger.info("User logged out")
    
    return {"message": "Logged out successfully"}

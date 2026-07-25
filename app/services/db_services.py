from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from app.models.user import User
from app.models.history import PredictionHistory
from app.core.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Fetches a user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    """Creates and persists a new user with a hashed password."""
    hashed_pwd = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def save_prediction_history(
    db: AsyncSession, 
    user_id: int, 
    ticker: str, 
    predicted_trend: str, 
    confidence_score: float
) -> PredictionHistory:
    """Saves an ML prediction record for a given user."""
    history_entry = PredictionHistory(
        user_id=user_id,
        ticker=ticker,
        predicted_trend=predicted_trend,
        confidence_score=confidence_score
    )
    db.add(history_entry)
    await db.commit()
    await db.refresh(history_entry)
    return history_entry


async def get_user_predictions(db: AsyncSession, user_id: int, limit: int = 10) -> List[PredictionHistory]:
    """Retrieves prediction history for a user sorted by most recent."""
    result = await db.execute(
        select(PredictionHistory)
        .where(PredictionHistory.user_id == user_id)
        .order_by(PredictionHistory.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
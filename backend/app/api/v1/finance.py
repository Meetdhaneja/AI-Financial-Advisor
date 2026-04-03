from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.finance import FinanceSummaryResponse
from app.services.finance.summary import build_finance_summary


router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/summary", response_model=FinanceSummaryResponse)
async def get_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> FinanceSummaryResponse:
    cache_key = f"summary:{current_user.id}:{start_date}:{end_date}"
    cached = await cache.get_json(cache_key)
    if cached:
        return FinanceSummaryResponse(**cached)

    summary = await build_finance_summary(db=db, user_id=current_user.id, start_date=start_date, end_date=end_date)
    await cache.set_json(cache_key, summary, expire_seconds=300)
    return FinanceSummaryResponse(**summary)


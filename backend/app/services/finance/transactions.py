from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Transaction, User
from app.schemas.transaction import TransactionCreate


async def create_transaction(
    db: AsyncSession,
    user: User,
    payload: TransactionCreate,
    is_anomaly: bool = False,
) -> Transaction:
    category = await db.scalar(select(Category).where(Category.id == payload.category_id))
    if category is None:
        raise ValueError("Category not found")

    transaction = Transaction(
        user_id=user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        transaction_type=payload.transaction_type,
        occurred_at=payload.occurred_at,
        description=payload.description,
        is_anomaly=is_anomaly,
        extra_data=payload.metadata,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return await db.scalar(
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.id == transaction.id)
    )


async def list_transactions(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    transaction_type: str | None = None,
) -> tuple[list[Transaction], int]:
    query = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
    )
    count_query = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)

    if start_date:
        query = query.where(Transaction.occurred_at >= start_date)
        count_query = count_query.where(Transaction.occurred_at >= start_date)
    if end_date:
        query = query.where(Transaction.occurred_at <= end_date)
        count_query = count_query.where(Transaction.occurred_at <= end_date)
    if category_id:
        query = query.where(Transaction.category_id == category_id)
        count_query = count_query.where(Transaction.category_id == category_id)
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
        count_query = count_query.where(Transaction.transaction_type == transaction_type)

    total = await db.scalar(count_query)
    items = (await db.scalars(query.offset((page - 1) * page_size).limit(page_size))).all()
    return items, total or 0


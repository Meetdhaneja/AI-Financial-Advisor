from __future__ import annotations

import csv
import io
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category, Goal, RecurringTransaction, Transaction, User
from app.schemas.planning import GoalCreate, RecurringTransactionCreate
from app.services.ml.analyzer import detect_transaction_anomaly


async def create_goal(db: AsyncSession, user: User, payload: GoalCreate) -> Goal:
    goal = Goal(user_id=user.id, **payload.model_dump())
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


async def list_goals(db: AsyncSession, user_id: int) -> list[Goal]:
    return (await db.scalars(select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc()))).all()


async def create_recurring_transaction(db: AsyncSession, user: User, payload: RecurringTransactionCreate) -> RecurringTransaction:
    recurring = RecurringTransaction(user_id=user.id, **payload.model_dump())
    db.add(recurring)
    await db.commit()
    await db.refresh(recurring)
    return recurring


async def list_recurring_transactions(db: AsyncSession, user_id: int) -> list[RecurringTransaction]:
    return (
        await db.scalars(
            select(RecurringTransaction)
            .where(RecurringTransaction.user_id == user_id)
            .order_by(RecurringTransaction.created_at.desc())
        )
    ).all()


async def import_transactions_from_csv(db: AsyncSession, user: User, content: bytes) -> tuple[int, int]:
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    category_map = {
        category.name.lower(): category
        for category in (await db.scalars(select(Category))).all()
    }
    imported = 0
    anomaly_count = 0

    for row in reader:
        category_name = (row.get("category") or row.get("Category") or "").strip()
        category = category_map.get(category_name.lower())
        if not category:
            continue
        try:
            amount = float(row.get("amount") or row.get("Amount") or 0)
            transaction_type = (row.get("transaction_type") or row.get("type") or row.get("Type") or category.type).strip()
            occurred_raw = row.get("occurred_at") or row.get("date") or row.get("Date")
            if not occurred_raw:
                continue
            occurred_at = date.fromisoformat(occurred_raw.strip())
        except (TypeError, ValueError):
            continue
        description = (row.get("description") or row.get("Description") or "").strip() or None
        anomaly = detect_transaction_anomaly(amount, category.name, transaction_type)
        transaction = Transaction(
            user_id=user.id,
            category_id=category.id,
            amount=amount,
            transaction_type=transaction_type,
            occurred_at=occurred_at,
            description=description,
            is_anomaly=anomaly["is_anomaly"],
            extra_data={"source": "csv_import"},
        )
        db.add(transaction)
        imported += 1
        anomaly_count += 1 if anomaly["is_anomaly"] else 0

    await db.commit()
    return imported, anomaly_count

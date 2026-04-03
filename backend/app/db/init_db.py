from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.models import Category


SYSTEM_CATEGORIES = [
    ("Salary", "income"),
    ("Freelance", "income"),
    ("Rent", "expense"),
    ("Groceries", "expense"),
    ("Transportation", "expense"),
    ("Gym", "expense"),
    ("Utilities", "expense"),
    ("Healthcare", "expense"),
    ("Investments", "expense"),
    ("Savings", "income"),
    ("EMI/Loans", "expense"),
    ("Dining & Entertainment", "expense"),
    ("Shopping & Wants", "expense"),
]


async def init_db(session: AsyncSession, db_engine: AsyncEngine | None = None) -> None:
    if db_engine is None:
        from app.db.session import engine as db_engine  # local import keeps tests decoupled from asyncpg

    async with db_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    existing_categories = await session.scalars(select(Category))
    if existing_categories.first():
        return

    for name, category_type in SYSTEM_CATEGORIES:
        session.add(Category(name=name, type=category_type, is_system=True))
    await session.commit()

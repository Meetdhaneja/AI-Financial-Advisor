from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache
from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models import Category, User
from app.schemas.common import PaginatedResponse
from app.schemas.planning import CsvImportResponse
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.finance.planning import import_transactions_from_csv
from app.services.finance.transactions import create_transaction, list_transactions
from app.services.ml.analyzer import detect_transaction_anomaly


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=201)
async def add_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> TransactionResponse:
    category = await db.scalar(select(Category).where(Category.id == payload.category_id))
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    anomaly_result = detect_transaction_anomaly(
        amount=payload.amount,
        category_name=category.name,
        transaction_type=payload.transaction_type,
    )
    transaction = await create_transaction(
        db=db,
        user=current_user,
        payload=payload,
        is_anomaly=anomaly_result["is_anomaly"],
    )
    await cache.delete_prefix(f"summary:{current_user.id}:")
    await cache.delete(f"prediction:{current_user.id}", f"recommendations:{current_user.id}")
    return TransactionResponse(
        id=transaction.id,
        category_id=transaction.category_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        occurred_at=transaction.occurred_at,
        description=transaction.description,
        is_anomaly=transaction.is_anomaly,
        metadata=transaction.extra_data,
        created_at=transaction.created_at,
        category=transaction.category,
    )


@router.get("", response_model=PaginatedResponse)
async def get_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    transaction_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> PaginatedResponse:
    items, total = await list_transactions(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        transaction_type=transaction_type,
    )
    return PaginatedResponse(
        items=[
            TransactionResponse(
                id=item.id,
                category_id=item.category_id,
                amount=item.amount,
                transaction_type=item.transaction_type,
                occurred_at=item.occurred_at,
                description=item.description,
                is_anomaly=item.is_anomaly,
                metadata=item.extra_data,
                created_at=item.created_at,
                category=item.category,
            ).model_dump()
            for item in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db_session)) -> list[dict]:
    categories = (await db.scalars(select(Category).order_by(Category.type.asc(), Category.name.asc()))).all()
    return [
        {
            "id": category.id,
            "name": category.name,
            "type": category.type,
            "is_system": category.is_system,
            "created_at": category.created_at.isoformat(),
        }
        for category in categories
    ]


@router.post("/import-csv", response_model=CsvImportResponse)
async def import_csv_transactions(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> CsvImportResponse:
    content = await file.read()
    imported_count, anomaly_count = await import_transactions_from_csv(db, current_user, content)
    await cache.delete_prefix(f"summary:{current_user.id}:")
    await cache.delete(f"prediction:{current_user.id}", f"recommendations:{current_user.id}")
    return CsvImportResponse(
        imported_count=imported_count,
        anomaly_count=anomaly_count,
        message="CSV import completed successfully.",
    )

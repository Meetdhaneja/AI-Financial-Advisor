from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TransactionCreate(BaseModel):
    category_id: int
    amount: float = Field(gt=0)
    transaction_type: str
    occurred_at: date
    description: str | None = None
    metadata: dict | None = None


class CategoryResponse(ORMModel):
    id: int
    name: str
    type: str
    is_system: bool
    created_at: datetime


class TransactionResponse(ORMModel):
    id: int
    category_id: int
    amount: float
    transaction_type: str
    occurred_at: date
    description: str | None = None
    is_anomaly: bool
    metadata: dict | None = None
    created_at: datetime
    category: CategoryResponse


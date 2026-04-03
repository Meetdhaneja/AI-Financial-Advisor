from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class GoalCreate(BaseModel):
    name: str
    goal_type: str
    target_amount: float = Field(gt=0)
    current_amount: float = 0
    target_months: int | None = None
    notes: str | None = None


class GoalResponse(ORMModel):
    id: int
    name: str
    goal_type: str
    target_amount: float
    current_amount: float
    target_months: int | None = None
    notes: str | None = None
    created_at: datetime


class RecurringTransactionCreate(BaseModel):
    category_id: int
    name: str
    amount: float = Field(gt=0)
    transaction_type: str
    frequency: str = "monthly"
    day_of_month: int = Field(default=1, ge=1, le=28)


class RecurringTransactionResponse(ORMModel):
    id: int
    category_id: int
    name: str
    amount: float
    transaction_type: str
    frequency: str
    day_of_month: int
    is_active: bool
    created_at: datetime


class CsvImportResponse(BaseModel):
    imported_count: int
    anomaly_count: int
    message: str


class ScenarioRequest(BaseModel):
    income_change: float = 0
    expense_change: float = 0
    savings_change: float = 0
    category_adjustments: dict[str, float] | None = None


class ScenarioResponse(BaseModel):
    projected_income: float
    projected_expenses: float
    projected_savings: float
    projected_savings_rate: float
    message: str

from datetime import date

from pydantic import BaseModel


class CategoryBreakdownItem(BaseModel):
    category: str
    amount: float
    transaction_type: str


class FinanceSummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_cashflow: float
    savings_rate: float
    financial_health_score: float
    anomaly_count: int
    category_breakdown: list[CategoryBreakdownItem]
    monthly_trends: list[dict]
    budget_progress: list[dict]
    plain_english_insights: list[str]
    what_changed: list[str]


class SummaryQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

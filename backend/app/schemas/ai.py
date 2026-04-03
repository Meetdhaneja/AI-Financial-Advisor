from pydantic import BaseModel, ConfigDict


class PredictionRequest(BaseModel):
    lookback_months: int = 6


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_amount: float
    confidence_band: list[float]
    top_factors: list[str]
    model_version: str


class SpendingAnalysisRequest(BaseModel):
    lookback_months: int = 6


class SpendingAnalysisResponse(BaseModel):
    risk_level: str
    risk_score: float
    overspending_signals: list[str]
    category_flags: list[str]
    overspending_categories: list[dict]
    attention_areas: list[str]


class AnomalyDetectionRequest(BaseModel):
    amount: float
    category_name: str
    transaction_type: str


class AnomalyDetectionResponse(BaseModel):
    is_anomaly: bool
    score: float
    reason: str


class BudgetRecommendationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    budget_plan: dict[str, float]
    emergency_fund_target: float
    investment_allocation: dict[str, float]
    custom_budget_used: bool
    overspending_categories: list[dict]
    attention_areas: list[str]
    next_actions: list[str]
    model_version: str


class RecommendationItem(BaseModel):
    id: int
    recommendation_type: str
    title: str
    message: str
    payload: dict
    priority: int
    created_at: str

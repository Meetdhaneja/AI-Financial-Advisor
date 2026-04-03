from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import cache
from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models import Recommendation, Transaction, User
from app.schemas.ai import (
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    BudgetRecommendationResponse,
    PredictionRequest,
    PredictionResponse,
    SpendingAnalysisRequest,
    SpendingAnalysisResponse,
)
from app.schemas.planning import GoalCreate, GoalResponse, RecurringTransactionCreate, RecurringTransactionResponse, ScenarioRequest, ScenarioResponse
from app.services.finance.planning import create_goal, create_recurring_transaction, list_goals, list_recurring_transactions
from app.services.ml.analyzer import analyze_spending_behavior, detect_transaction_anomaly
from app.services.ml.predictor import build_prediction_payload
from app.services.recommendations.engine import build_budget_recommendation


router = APIRouter(prefix="/ai", tags=["ai"])


async def _load_user_transactions(db: AsyncSession, user_id: int) -> list[Transaction]:
    query = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.occurred_at.asc())
    )
    return (await db.scalars(query)).all()


@router.post("/predict-expense", response_model=PredictionResponse)
async def predict_expense(
    _: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> PredictionResponse:
    cache_key = f"prediction:{current_user.id}"
    cached = await cache.get_json(cache_key)
    if cached:
        return PredictionResponse(**cached)

    transactions = await _load_user_transactions(db, current_user.id)
    payload = build_prediction_payload(current_user, transactions)
    response = {
        "predicted_amount": payload["predicted_amount"],
        "confidence_band": payload["confidence_band"],
        "top_factors": payload["top_factors"],
        "model_version": payload["model_version"],
    }
    await cache.set_json(cache_key, response, expire_seconds=300)
    return PredictionResponse(**response)


@router.post("/analyze-spending", response_model=SpendingAnalysisResponse)
async def analyze_spending(
    _: SpendingAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> SpendingAnalysisResponse:
    transactions = await _load_user_transactions(db, current_user.id)
    return SpendingAnalysisResponse(**analyze_spending_behavior(current_user, transactions))


@router.post("/detect-anomaly", response_model=AnomalyDetectionResponse)
async def detect_anomaly(payload: AnomalyDetectionRequest) -> AnomalyDetectionResponse:
    return AnomalyDetectionResponse(**detect_transaction_anomaly(payload.amount, payload.category_name, payload.transaction_type))


@router.get("/recommend-budget", response_model=BudgetRecommendationResponse)
async def recommend_budget(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> BudgetRecommendationResponse:
    cache_key = f"recommendations:{current_user.id}"
    cached = await cache.get_json(cache_key)
    if cached:
        return BudgetRecommendationResponse(**cached)

    transactions = await _load_user_transactions(db, current_user.id)
    payload = build_budget_recommendation(current_user, transactions)
    recommendation = Recommendation(
        user_id=current_user.id,
        recommendation_type="budget",
        title="Monthly Budget Plan",
        message="AI-generated monthly budget recommendation.",
        payload=payload,
        priority=1,
    )
    db.add(recommendation)
    await db.commit()
    await cache.set_json(cache_key, payload, expire_seconds=300)
    return BudgetRecommendationResponse(**payload)


@router.get("/recommendations")
async def list_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    items = (
        await db.scalars(
            select(Recommendation)
            .where(Recommendation.user_id == current_user.id)
            .order_by(Recommendation.created_at.desc())
        )
    ).all()
    return [
        {
            "id": item.id,
            "recommendation_type": item.recommendation_type,
            "title": item.title,
            "message": item.message,
            "payload": item.payload,
            "priority": item.priority,
            "created_at": item.created_at.isoformat(),
        }
        for item in items
    ]


@router.get("/goals", response_model=list[GoalResponse])
async def get_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[GoalResponse]:
    return await list_goals(db, current_user.id)


@router.post("/goals", response_model=GoalResponse, status_code=201)
async def add_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> GoalResponse:
    return await create_goal(db, current_user, payload)


@router.get("/recurring", response_model=list[RecurringTransactionResponse])
async def get_recurring_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[RecurringTransactionResponse]:
    return await list_recurring_transactions(db, current_user.id)


@router.post("/recurring", response_model=RecurringTransactionResponse, status_code=201)
async def add_recurring_transaction(
    payload: RecurringTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> RecurringTransactionResponse:
    return await create_recurring_transaction(db, current_user, payload)


@router.post("/simulate-scenario", response_model=ScenarioResponse)
async def simulate_scenario(
    payload: ScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ScenarioResponse:
    transactions = await _load_user_transactions(db, current_user.id)
    latest_month = max((item.occurred_at.replace(day=1) for item in transactions), default=None)
    relevant_transactions = [
        item for item in transactions if latest_month is None or item.occurred_at.replace(day=1) == latest_month
    ]
    summary = {
        "income": sum(item.amount for item in relevant_transactions if item.transaction_type == "income"),
        "expense": sum(item.amount for item in relevant_transactions if item.transaction_type == "expense"),
    }
    baseline_income = summary["income"] or float(current_user.monthly_income_default or 0.0)
    projected_income = max(baseline_income + payload.income_change, 0)
    projected_expenses = max(summary["expense"] + payload.expense_change, 0)
    if payload.category_adjustments:
        projected_expenses += sum(payload.category_adjustments.values())
    projected_savings = max(projected_income - projected_expenses + payload.savings_change, 0)
    projected_savings_rate = projected_savings / projected_income if projected_income else 0
    message = (
        "This scenario improves your monthly position."
        if projected_savings_rate >= 0.2
        else "This scenario keeps savings tight, so you may want to reduce discretionary spending further."
    )
    return ScenarioResponse(
        projected_income=round(projected_income, 2),
        projected_expenses=round(projected_expenses, 2),
        projected_savings=round(projected_savings, 2),
        projected_savings_rate=round(projected_savings_rate, 3),
        message=message,
    )

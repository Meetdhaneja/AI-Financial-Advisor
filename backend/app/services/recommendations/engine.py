from __future__ import annotations

from app.models import Transaction, User
from app.services.ml.analyzer import analyze_spending_behavior
from app.services.ml.predictor import build_prediction_payload
from app.services.ml.preprocessing import transactions_to_monthly_frame


def build_budget_recommendation(user: User, transactions: list[Transaction]) -> dict:
    prediction = build_prediction_payload(user, transactions)
    analysis = analyze_spending_behavior(user, transactions)
    monthly_frame = transactions_to_monthly_frame(transactions, user.monthly_income_default)

    latest_income = (
        float(monthly_frame.iloc[-1]["Income"])
        if not monthly_frame.empty and "Income" in monthly_frame.columns
        else float(user.monthly_income_default or 0.0)
    )
    predicted_expense = prediction["predicted_amount"]
    risk_profile = user.risk_profile or "medium"
    custom_budget_target = float(user.monthly_budget_target or 0.0)

    emergency_multiplier = {"low": 4, "medium": 6, "high": 8}.get(risk_profile, 6)
    emergency_fund_target = predicted_expense * emergency_multiplier
    leftover = max(latest_income - predicted_expense, 0.0)
    savings_share = float(user.preferred_savings_rate) if user.preferred_savings_rate is not None else (0.2 if analysis["risk_level"] == "high" else 0.3)
    investment_share = {"low": 0.2, "medium": 0.35, "high": 0.5}.get(risk_profile, 0.35)
    planning_base = custom_budget_target if custom_budget_target > 0 else predicted_expense

    budget_plan = {
        "essentials": round(planning_base * 0.6, 2),
        "discretionary": round(planning_base * (0.15 if analysis["risk_level"] == "high" else 0.2), 2),
        "savings": round(leftover * savings_share, 2),
        "investments": round(leftover * investment_share, 2),
    }
    category_budget_overrides = user.category_budget_preferences or {}
    if category_budget_overrides:
        budget_plan["custom_category_total"] = round(sum(float(value) for value in category_budget_overrides.values()), 2)
    investment_allocation = {
        "fixed_income": 60.0 if risk_profile == "low" else 35.0,
        "index_funds": 30.0 if risk_profile == "low" else 45.0,
        "equities": 10.0 if risk_profile == "low" else 20.0,
    }
    if risk_profile == "high":
        investment_allocation = {"fixed_income": 20.0, "index_funds": 40.0, "equities": 40.0}

    next_actions = [
        "Review the highest-spend categories before the next billing cycle.",
        "Build or maintain an emergency-fund bucket until the target is reached.",
    ]
    if analysis["risk_level"] != "low":
        next_actions.append("Cap discretionary spending next month to reduce overspending risk.")
    if "EMI/Loans" in analysis["category_flags"]:
        next_actions.append("Revisit debt obligations and test affordability against predicted expenses.")
    if analysis["overspending_categories"]:
        next_actions.append(
            f"Bring down {analysis['overspending_categories'][0]['category']} first because it is furthest above your plan."
        )

    return {
        "budget_plan": budget_plan,
        "emergency_fund_target": round(emergency_fund_target, 2),
        "investment_allocation": investment_allocation,
        "custom_budget_used": custom_budget_target > 0 or bool(category_budget_overrides),
        "overspending_categories": analysis["overspending_categories"],
        "attention_areas": analysis["attention_areas"],
        "next_actions": next_actions,
        "model_version": prediction["model_version"],
    }

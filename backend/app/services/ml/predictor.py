from __future__ import annotations

from datetime import date

from app.models import Transaction, User
from app.services.ml.preprocessing import next_month_date, transactions_to_monthly_rows


FEATURE_COLUMNS = [
    "Income",
    "Total Expenditure",
    "Savings",
    "Investments",
    "Essentials",
    "Discretionary",
    "Future",
    "ExpenseRatio",
    "SavingsRatio",
    "InvestmentRatio",
    "ExpenseLag1",
    "SavingsLag1",
    "ExpenseRolling3",
    "IncomeRolling3",
    "DiscretionaryRolling3",
    "HealthSpikeFlag",
    "HasEMI",
    "MonthNum",
    "Quarter",
]


def build_prediction_payload(user: User, transactions: list[Transaction]) -> dict:
    monthly_rows = transactions_to_monthly_rows(transactions, user.monthly_income_default)
    if len(monthly_rows) < 2:
        baseline = float(user.monthly_budget_target or user.monthly_income_default or 0.0) * 0.65
        if baseline <= 0:
            baseline = 25000.0
        return {
            "predicted_amount": round(float(baseline), 2),
            "confidence_band": [round(float(baseline * 0.9), 2), round(float(baseline * 1.1), 2)],
            "top_factors": ["recent_income", "baseline_rule", "insufficient_user_history"],
            "model_version": "rule_based_v1",
            "period_month": date.today().replace(day=1).isoformat(),
            "features": {},
        }

    latest = monthly_rows[-1]
    recent_rows = monthly_rows[-3:]
    average_recent_expense = sum(float(item["Total Expenditure"]) for item in recent_rows) / len(recent_rows)
    expense_momentum = float(latest["Total Expenditure"]) - float(latest["ExpenseLag1"])
    discretionary_pressure = max(float(latest["Discretionary"]) - float(latest["DiscretionaryRolling3"]), 0.0)
    predicted = average_recent_expense + expense_momentum * 0.35 + discretionary_pressure * 0.2
    predicted = max(predicted, average_recent_expense * 0.85)

    confidence = max(predicted * 0.08, 1000.0)
    top_factors = sorted(
        [
            ("expense_ratio", float(latest["ExpenseRatio"])),
            ("essentials", float(latest["Essentials"])),
            ("discretionary", float(latest["Discretionary"])),
            ("recent_trend", expense_momentum),
        ],
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    return {
        "predicted_amount": round(predicted, 2),
        "confidence_band": [round(predicted - confidence, 2), round(predicted + confidence, 2)],
        "top_factors": [name for name, _ in top_factors[:3]],
        "model_version": "rule_based_v1",
        "period_month": next_month_date(date.fromisoformat(str(latest["Month"]))).isoformat(),
        "features": {column: float(latest[column]) for column in FEATURE_COLUMNS},
    }

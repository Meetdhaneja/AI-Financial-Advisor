from __future__ import annotations

from collections import defaultdict

from app.models import Transaction, User
from app.services.ml.preprocessing import transactions_to_monthly_rows


def analyze_spending_behavior(user: User, transactions: list[Transaction]) -> dict:
    monthly_rows = transactions_to_monthly_rows(transactions, user.monthly_income_default)

    if not monthly_rows:
        return {
            "risk_level": "low",
            "risk_score": 0.2,
            "overspending_signals": ["No user history yet; using conservative low-risk baseline."],
            "category_flags": [],
            "overspending_categories": [],
            "attention_areas": ["Add a few months of transactions to unlock personalized overspending coaching."],
        }

    latest = monthly_rows[-1]
    discretionary_drift = max(float(latest["Discretionary"]) - float(latest["DiscretionaryRolling3"]), 0.0)
    probability = min(
        1.0,
        max(
            0.05,
            float(latest["ExpenseRatio"]) * 0.65
            + (0.2 if discretionary_drift > 1000 else 0.0)
            + (0.15 if float(latest["HasEMI"]) else 0.0)
            + (0.1 if float(latest["HealthSpikeFlag"]) else 0.0),
        ),
    )

    if probability >= 0.75:
        risk_level = "high"
    elif probability >= 0.45:
        risk_level = "medium"
    else:
        risk_level = "low"

    signals = []
    if latest["ExpenseRatio"] > 0.8:
        signals.append("Expenses are consuming more than 80% of income.")
    if float(latest["Discretionary"]) > float(latest["DiscretionaryRolling3"]) * 1.15:
        signals.append("Discretionary spending is above the recent rolling average.")
    if float(latest["HasEMI"]) == 1:
        signals.append("Debt obligations are present and reduce flexibility.")
    if not signals:
        signals.append("Spending pattern is stable relative to recent history.")

    recent_rows = monthly_rows[-3:] if len(monthly_rows) >= 3 else monthly_rows
    category_flags = []
    for name in ["Groceries", "Healthcare", "Dining & Entertainment", "Shopping & Wants", "EMI/Loans"]:
        recent_average = sum(float(item.get(name, 0.0)) for item in recent_rows) / max(len(recent_rows), 1)
        if recent_average and float(latest.get(name, 0.0)) > recent_average * 1.2:
            category_flags.append(name)

    user_budgets = user.category_budget_preferences or {}
    overspending_categories = []
    for name in [
        "Rent",
        "Groceries",
        "Transportation",
        "Utilities",
        "Healthcare",
        "Dining & Entertainment",
        "Shopping & Wants",
        "EMI/Loans",
    ]:
        current_amount = float(latest.get(name, 0.0))
        preferred_budget = float(user_budgets.get(name, 0.0)) if user_budgets.get(name) is not None else 0.0
        rolling_reference = sum(float(item.get(name, 0.0)) for item in recent_rows) / max(len(recent_rows), 1)
        threshold = preferred_budget if preferred_budget > 0 else rolling_reference * 1.1
        if current_amount > threshold and threshold > 0:
            overspending_categories.append(
                {
                    "category": name,
                    "current": round(current_amount, 2),
                    "target": round(threshold, 2),
                    "difference": round(current_amount - threshold, 2),
                }
            )

    overspending_categories.sort(key=lambda item: item["difference"], reverse=True)
    attention_areas = []
    if overspending_categories:
        top = overspending_categories[0]
        attention_areas.append(
            f"{top['category']} is the biggest overspending area right now at Rs {top['current']:.0f} versus a target of Rs {top['target']:.0f}."
        )
    if latest["ExpenseRatio"] > 0.75:
        attention_areas.append("Your total expenses are taking a large share of income, so focus on non-essential categories first.")
    if latest["SavingsRatio"] < (user.preferred_savings_rate or 0.2):
        attention_areas.append("Your savings pace is below your preferred target, so tighten monthly spending caps or increase auto-saving.")
    if not attention_areas:
        attention_areas.append("Your current monthly spending is close to plan. Keep monitoring the top categories for drift.")

    return {
        "risk_level": risk_level,
        "risk_score": round(probability, 3),
        "overspending_signals": signals,
        "category_flags": category_flags,
        "overspending_categories": overspending_categories[:5],
        "attention_areas": attention_areas,
    }


def detect_transaction_anomaly(amount: float, category_name: str, transaction_type: str) -> dict:
    category_baselines = defaultdict(
        lambda: 2500.0,
        {
            "Rent": 12000.0,
            "Groceries": 4500.0,
            "Transportation": 2500.0,
            "Utilities": 2200.0,
            "Healthcare": 1800.0,
            "Dining & Entertainment": 3000.0,
            "Shopping & Wants": 2800.0,
            "EMI/Loans": 6500.0,
            "Investments": 5000.0,
            "Savings": 6000.0,
            "Salary": 45000.0,
            "Freelance": 15000.0,
        },
    )
    baseline = category_baselines[category_name]
    multiplier = 1.7 if transaction_type == "expense" else 2.2
    score = (amount - baseline) / max(baseline, 1.0)
    is_anomaly = amount > baseline * multiplier
    reason = (
        f"Transaction is well above the usual range for {category_name}."
        if is_anomaly
        else "Transaction sits within the expected category range."
    )
    return {"is_anomaly": is_anomaly, "score": round(score, 4), "reason": reason}

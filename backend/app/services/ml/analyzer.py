from __future__ import annotations

import pandas as pd

from app.models import Transaction, User
from app.services.ml.model_loader import load_artifact
from app.services.ml.predictor import FEATURE_COLUMNS
from app.services.ml.preprocessing import make_realtime_features, transactions_to_monthly_frame


def analyze_spending_behavior(user: User, transactions: list[Transaction]) -> dict:
    classifier = load_artifact("overspending_classifier.joblib")
    metadata = load_artifact("model_metadata.joblib")
    monthly_frame = transactions_to_monthly_frame(transactions, user.monthly_income_default)

    if monthly_frame.empty:
        return {
            "risk_level": "low",
            "risk_score": 0.2,
            "overspending_signals": ["No user history yet; using conservative low-risk baseline."],
            "category_flags": [],
            "overspending_categories": [],
            "attention_areas": ["Add a few months of transactions to unlock personalized overspending coaching."],
        }

    feature_frame = make_realtime_features(monthly_frame)
    latest = feature_frame.iloc[-1]
    input_frame = pd.DataFrame([{column: latest[column] for column in FEATURE_COLUMNS}])
    probability = float(classifier.predict_proba(input_frame)[0][1])

    if probability >= 0.75:
        risk_level = "high"
    elif probability >= 0.45:
        risk_level = "medium"
    else:
        risk_level = "low"

    signals = []
    if latest["ExpenseRatio"] > 0.8:
        signals.append("Expenses are consuming more than 80% of income.")
    if latest["Discretionary"] > latest["DiscretionaryRolling3"] * 1.15:
        signals.append("Discretionary spending is above the recent rolling average.")
    if latest["HasEMI"] == 1:
        signals.append("Debt obligations are present and reduce flexibility.")
    if not signals:
        signals.append("Spending pattern is stable relative to recent history.")

    category_flags = [
        name
        for name in ["Groceries", "Healthcare", "Dining & Entertainment", "Shopping & Wants", "EMI/Loans"]
        if float(latest.get(name, 0.0)) > metadata["category_alert_thresholds"].get(name, float("inf"))
    ]

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
        rolling_reference = float(feature_frame[name].rolling(3, min_periods=1).mean().iloc[-1]) if name in feature_frame else current_amount
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
    detector = load_artifact("anomaly_detector.joblib")
    metadata = load_artifact("model_metadata.joblib")
    category_index = metadata["anomaly_category_map"].get(category_name, 0)
    transaction_flag = 1 if transaction_type == "expense" else 0
    input_frame = pd.DataFrame([{"amount": amount, "category_idx": category_index, "transaction_flag": transaction_flag}])
    prediction = int(detector.predict(input_frame)[0])
    score = float(detector.score_samples(input_frame)[0])
    category_median = metadata["category_medians"].get(category_name, 0.0)
    z_score = ((amount - category_median) / category_median) if category_median else 0.0
    is_anomaly = prediction == -1 or z_score > 1.25
    reason = (
        f"Transaction is materially above the category median ({category_median:.2f})."
        if is_anomaly
        else "Transaction sits within the expected category range."
    )
    return {"is_anomaly": is_anomaly, "score": round(score, 4), "reason": reason}

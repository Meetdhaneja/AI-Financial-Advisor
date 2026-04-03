from __future__ import annotations

from datetime import date

import pandas as pd

from app.models import Transaction, User
from app.services.ml.model_loader import load_artifact
from app.services.ml.preprocessing import make_realtime_features, next_month_date, transactions_to_monthly_frame


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
    regressor = load_artifact("expense_regressor.joblib")
    metadata = load_artifact("model_metadata.joblib")

    monthly_frame = transactions_to_monthly_frame(transactions, user.monthly_income_default)
    if monthly_frame.empty or len(monthly_frame) < 2:
        baseline = metadata["baseline_prediction"]
        return {
            "predicted_amount": round(float(baseline), 2),
            "confidence_band": [round(float(baseline * 0.9), 2), round(float(baseline * 1.1), 2)],
            "top_factors": ["baseline_model", "insufficient_user_history", "seed_dataset"],
            "model_version": metadata["model_version"],
            "period_month": date.today().replace(day=1).isoformat(),
            "features": {},
        }

    feature_frame = make_realtime_features(monthly_frame)
    latest = feature_frame.iloc[-1]
    prediction_input = pd.DataFrame([{column: latest[column] for column in FEATURE_COLUMNS}])
    predicted = float(regressor.predict(prediction_input)[0])

    confidence = max(predicted * 0.1, 1500.0)
    top_factors = sorted(
        [
            ("expense_ratio", float(latest["ExpenseRatio"])),
            ("essentials", float(latest["Essentials"])),
            ("discretionary", float(latest["Discretionary"])),
            ("income", float(latest["Income"])),
        ],
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    return {
        "predicted_amount": round(predicted, 2),
        "confidence_band": [round(predicted - confidence, 2), round(predicted + confidence, 2)],
        "top_factors": [name for name, _ in top_factors[:3]],
        "model_version": metadata["model_version"],
        "period_month": next_month_date(latest["Month"].date()).isoformat(),
        "features": {column: float(latest[column]) for column in FEATURE_COLUMNS},
    }


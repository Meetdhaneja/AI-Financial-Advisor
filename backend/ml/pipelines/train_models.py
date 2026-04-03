from __future__ import annotations

import re
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression


MODEL_VERSION = "v1.0.0"


def _normalize_columns(columns: list[str]) -> list[str]:
    normalized = []
    for column in columns:
        cleaned = column.replace("â‚¹", "INR").replace("₹", "INR")
        cleaned = re.sub(r"\s*\((?:INR|\?)\)", "", cleaned)
        normalized.append(cleaned.strip())
    return normalized


def load_seed_dataset(data_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(data_path)
    frame.columns = _normalize_columns(list(frame.columns))
    frame["Month"] = pd.to_datetime(frame["Month"])
    return frame


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    dataset = frame.copy().sort_values("Month")
    dataset["Essentials"] = dataset[["Rent", "Groceries", "Utilities", "Transportation", "Healthcare", "EMI/Loans"]].sum(axis=1)
    dataset["Discretionary"] = dataset[["Dining & Entertainment", "Shopping & Wants", "Gym"]].sum(axis=1)
    dataset["Future"] = dataset[["Savings", "Investments"]].sum(axis=1)
    dataset["ExpenseRatio"] = dataset["Total Expenditure"] / dataset["Income"]
    dataset["SavingsRatio"] = dataset["Savings"] / dataset["Income"]
    dataset["InvestmentRatio"] = dataset["Investments"] / dataset["Income"]
    dataset["ExpenseLag1"] = dataset["Total Expenditure"].shift(1).fillna(dataset["Total Expenditure"])
    dataset["SavingsLag1"] = dataset["Savings"].shift(1).fillna(dataset["Savings"])
    dataset["ExpenseRolling3"] = dataset["Total Expenditure"].rolling(3, min_periods=1).mean()
    dataset["IncomeRolling3"] = dataset["Income"].rolling(3, min_periods=1).mean()
    dataset["DiscretionaryRolling3"] = dataset["Discretionary"].rolling(3, min_periods=1).mean()
    dataset["HealthSpikeFlag"] = (
        dataset["Healthcare"] > dataset["Healthcare"].rolling(3, min_periods=1).mean() * 1.2
    ).astype(int)
    dataset["HasEMI"] = (dataset["EMI/Loans"] > 0).astype(int)
    dataset["MonthNum"] = dataset["Month"].dt.month
    dataset["Quarter"] = dataset["Month"].dt.quarter
    dataset["OverspendingLabel"] = (
        (dataset["ExpenseRatio"] >= 0.8)
        | (dataset["Discretionary"] > dataset["DiscretionaryRolling3"] * 1.15)
    ).astype(int)
    dataset["NextMonthExpense"] = dataset["Total Expenditure"].shift(-1)
    return dataset


def train_and_save_models() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    data_path = base_dir / "data" / "monthly_spending_dataset_2020_2025.csv"
    artifact_dir = base_dir / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    dataset = engineer_features(load_seed_dataset(data_path))
    model_frame = dataset.dropna(subset=["NextMonthExpense"]).copy()
    feature_columns = [
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

    X = model_frame[feature_columns]
    y_reg = model_frame["NextMonthExpense"]
    y_cls = model_frame["OverspendingLabel"]

    regressor = RandomForestRegressor(n_estimators=200, random_state=42)
    regressor.fit(X, y_reg)

    benchmark = LinearRegression()
    benchmark.fit(X, y_reg)

    classifier = RandomForestClassifier(n_estimators=200, random_state=42)
    classifier.fit(X, y_cls)

    category_columns = [
        "Groceries",
        "Rent",
        "Transportation",
        "Gym",
        "Utilities",
        "Healthcare",
        "Investments",
        "Savings",
        "EMI/Loans",
        "Dining & Entertainment",
        "Shopping & Wants",
    ]
    anomaly_category_map = {name: idx for idx, name in enumerate(category_columns, start=1)}
    anomaly_rows = []
    category_medians = {}
    for category in category_columns:
        category_medians[category] = float(dataset[category].median())
        for _, row in dataset.iterrows():
            anomaly_rows.append(
                {
                    "amount": row[category],
                    "category_idx": anomaly_category_map[category],
                    "transaction_flag": 0 if category == "Savings" else 1,
                }
            )
    anomaly_detector = IsolationForest(random_state=42, contamination=0.08)
    anomaly_detector.fit(pd.DataFrame(anomaly_rows))

    metadata = {
        "model_version": MODEL_VERSION,
        "feature_columns": feature_columns,
        "baseline_prediction": float(y_reg.mean()),
        "category_alert_thresholds": {
            category: float(dataset[category].quantile(0.85))
            for category in ["Groceries", "Healthcare", "Dining & Entertainment", "Shopping & Wants", "EMI/Loans"]
        },
        "anomaly_category_map": anomaly_category_map,
        "category_medians": category_medians,
    }

    joblib.dump(regressor, artifact_dir / "expense_regressor.joblib")
    joblib.dump(benchmark, artifact_dir / "expense_regressor_benchmark.joblib")
    joblib.dump(classifier, artifact_dir / "overspending_classifier.joblib")
    joblib.dump(anomaly_detector, artifact_dir / "anomaly_detector.joblib")
    joblib.dump(metadata, artifact_dir / "model_metadata.joblib")


if __name__ == "__main__":
    train_and_save_models()

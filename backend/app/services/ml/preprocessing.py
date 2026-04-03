from __future__ import annotations

from collections import defaultdict
from datetime import date

import pandas as pd

from app.models import Transaction


def transactions_to_monthly_frame(
    transactions: list[Transaction],
    monthly_income_default: float | None,
) -> pd.DataFrame:
    monthly_buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for transaction in transactions:
        month_key = transaction.occurred_at.replace(day=1).isoformat()
        category_name = transaction.category.name if transaction.category else "Unknown"
        monthly_buckets[month_key][category_name] += transaction.amount
        if transaction.transaction_type == "income":
            monthly_buckets[month_key]["Income"] += transaction.amount
        else:
            monthly_buckets[month_key]["Total Expenditure"] += transaction.amount

    rows = []
    ordered_columns = [
        "Rent",
        "Groceries",
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
    for month, values in sorted(monthly_buckets.items()):
        row = {"Month": month}
        for column in ordered_columns:
            row[column] = values.get(column, 0.0)
        row["Income"] = values.get("Income", monthly_income_default or 0.0)
        row["Total Expenditure"] = values.get("Total Expenditure", 0.0)
        rows.append(row)

    return pd.DataFrame(rows)


def make_realtime_features(monthly_frame: pd.DataFrame) -> pd.DataFrame:
    if monthly_frame.empty:
        return pd.DataFrame()

    frame = monthly_frame.copy()
    frame["Month"] = pd.to_datetime(frame["Month"])
    frame = frame.sort_values("Month")
    frame["Essentials"] = frame[["Rent", "Groceries", "Utilities", "Transportation", "Healthcare", "EMI/Loans"]].sum(axis=1)
    frame["Discretionary"] = frame[["Dining & Entertainment", "Shopping & Wants", "Gym"]].sum(axis=1)
    frame["Future"] = frame[["Savings", "Investments"]].sum(axis=1)
    frame["ExpenseRatio"] = frame["Total Expenditure"] / frame["Income"].replace(0, 1)
    frame["SavingsRatio"] = frame["Savings"] / frame["Income"].replace(0, 1)
    frame["InvestmentRatio"] = frame["Investments"] / frame["Income"].replace(0, 1)
    frame["ExpenseLag1"] = frame["Total Expenditure"].shift(1).fillna(frame["Total Expenditure"])
    frame["SavingsLag1"] = frame["Savings"].shift(1).fillna(frame["Savings"])
    frame["ExpenseRolling3"] = frame["Total Expenditure"].rolling(3, min_periods=1).mean()
    frame["IncomeRolling3"] = frame["Income"].rolling(3, min_periods=1).mean()
    frame["DiscretionaryRolling3"] = frame["Discretionary"].rolling(3, min_periods=1).mean()
    frame["HealthSpikeFlag"] = (
        frame["Healthcare"] > frame["Healthcare"].rolling(3, min_periods=1).mean() * 1.2
    ).astype(int)
    frame["HasEMI"] = (frame["EMI/Loans"] > 0).astype(int)
    frame["MonthNum"] = frame["Month"].dt.month
    frame["Quarter"] = frame["Month"].dt.quarter
    return frame


def next_month_date(input_date: date) -> date:
    month = input_date.month + 1
    year = input_date.year
    if month > 12:
        month = 1
        year += 1
    return date(year, month, 1)


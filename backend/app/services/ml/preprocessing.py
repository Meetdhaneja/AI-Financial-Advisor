from __future__ import annotations

from collections import defaultdict
from datetime import date

from app.models import Transaction


TRACKED_COLUMNS = [
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


def transactions_to_monthly_rows(
    transactions: list[Transaction],
    monthly_income_default: float | None,
) -> list[dict[str, float | str]]:
    monthly_buckets: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for transaction in transactions:
        month_key = transaction.occurred_at.replace(day=1).isoformat()
        category_name = transaction.category.name if transaction.category else "Unknown"
        monthly_buckets[month_key][category_name] += transaction.amount
        if transaction.transaction_type == "income":
            monthly_buckets[month_key]["Income"] += transaction.amount
        else:
            monthly_buckets[month_key]["Total Expenditure"] += transaction.amount

    rows: list[dict[str, float | str]] = []
    for month, values in sorted(monthly_buckets.items()):
        row: dict[str, float | str] = {"Month": month}
        for column in TRACKED_COLUMNS:
            row[column] = values.get(column, 0.0)
        row["Income"] = values.get("Income", monthly_income_default or 0.0)
        row["Total Expenditure"] = values.get("Total Expenditure", 0.0)
        row["Essentials"] = sum(float(row[name]) for name in ["Rent", "Groceries", "Utilities", "Transportation", "Healthcare", "EMI/Loans"])
        row["Discretionary"] = sum(float(row[name]) for name in ["Dining & Entertainment", "Shopping & Wants", "Gym"])
        row["Future"] = sum(float(row[name]) for name in ["Savings", "Investments"])
        income = float(row["Income"]) or 1.0
        row["ExpenseRatio"] = float(row["Total Expenditure"]) / income
        row["SavingsRatio"] = float(row["Savings"]) / income
        row["InvestmentRatio"] = float(row["Investments"]) / income
        row["HasEMI"] = 1.0 if float(row["EMI/Loans"]) > 0 else 0.0
        rows.append(row)

    for index, row in enumerate(rows):
        prev_row = rows[index - 1] if index > 0 else row
        rolling_slice = rows[max(0, index - 2) : index + 1]
        healthcare_average = sum(float(item["Healthcare"]) for item in rolling_slice) / len(rolling_slice)
        row["ExpenseLag1"] = float(prev_row["Total Expenditure"])
        row["SavingsLag1"] = float(prev_row["Savings"])
        row["ExpenseRolling3"] = sum(float(item["Total Expenditure"]) for item in rolling_slice) / len(rolling_slice)
        row["IncomeRolling3"] = sum(float(item["Income"]) for item in rolling_slice) / len(rolling_slice)
        row["DiscretionaryRolling3"] = sum(float(item["Discretionary"]) for item in rolling_slice) / len(rolling_slice)
        row["HealthSpikeFlag"] = 1.0 if float(row["Healthcare"]) > healthcare_average * 1.2 else 0.0
        month_date = date.fromisoformat(str(row["Month"]))
        row["MonthNum"] = float(month_date.month)
        row["Quarter"] = float(((month_date.month - 1) // 3) + 1)

    return rows


def next_month_date(input_date: date) -> date:
    month = input_date.month + 1
    year = input_date.year
    if month > 12:
        month = 1
        year += 1
    return date(year, month, 1)

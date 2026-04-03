from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


CATEGORY_COLUMNS = [
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

EXPENSE_COLUMNS = [column for column in CATEGORY_COLUMNS if column != "Savings"]
ESSENTIAL_COLUMNS = [
    "Rent",
    "Groceries",
    "Utilities",
    "Transportation",
    "Healthcare",
    "EMI/Loans",
]
DISCRETIONARY_COLUMNS = ["Dining & Entertainment", "Shopping & Wants", "Gym"]
FUTURE_COLUMNS = ["Investments", "Savings"]


@dataclass(frozen=True)
class MonthlyRecord:
    month: date
    values: dict[str, float]

    def get(self, key: str) -> float:
        return self.values[key]


def normalize_column_name(column: str) -> str:
    """Normalize rupee labels and strip the unit from headers."""
    cleaned = column.replace("\u20b9", "INR").replace("₹", "INR").replace("â‚¹", "INR")
    cleaned = re.sub(r"\s*\((?:INR|\?)\)", "", cleaned)
    return cleaned.strip()


def load_monthly_records(csv_path: str | Path) -> list[MonthlyRecord]:
    path = Path(csv_path)
    records: list[MonthlyRecord] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed: dict[str, float] = {}
            month_value: date | None = None
            for raw_key, raw_value in row.items():
                key = normalize_column_name(raw_key)
                if key == "Month":
                    month_value = date.fromisoformat(raw_value)
                else:
                    parsed[key] = float(raw_value)

            if month_value is None:
                raise ValueError("Month column missing from dataset row.")

            records.append(MonthlyRecord(month=month_value, values=parsed))

    return records


def rolling_mean(records: Iterable[MonthlyRecord], key: str) -> float:
    values = [record.get(key) for record in records]
    return sum(values) / len(values) if values else 0.0


def percentage_change(current: float, baseline: float) -> float | None:
    if baseline == 0:
        return None
    return (current - baseline) / baseline


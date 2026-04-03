from __future__ import annotations

import csv
from pathlib import Path

from .data_utils import (
    CATEGORY_COLUMNS,
    DISCRETIONARY_COLUMNS,
    ESSENTIAL_COLUMNS,
    EXPENSE_COLUMNS,
    FUTURE_COLUMNS,
    load_monthly_records,
    percentage_change,
)


def _safe_ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _bucket_total(record, columns: list[str]) -> float:
    return sum(record.get(column) for column in columns)


def build_feature_rows(csv_path: str | Path) -> list[dict[str, float | int | str]]:
    records = load_monthly_records(csv_path)
    rows: list[dict[str, float | int | str]] = []

    for index, record in enumerate(records):
        previous = records[index - 1] if index > 0 else None
        trailing_3 = records[max(0, index - 3) : index]

        income = record.get("Income")
        total_expenditure = record.get("Total Expenditure")
        savings = record.get("Savings")
        investments = record.get("Investments")
        essentials = _bucket_total(record, ESSENTIAL_COLUMNS)
        discretionary = _bucket_total(record, DISCRETIONARY_COLUMNS)
        future = _bucket_total(record, FUTURE_COLUMNS)
        surplus_before_savings = income - total_expenditure

        feature_row: dict[str, float | int | str] = {
            "month": record.month.isoformat(),
            "year": record.month.year,
            "month_num": record.month.month,
            "quarter": ((record.month.month - 1) // 3) + 1,
            "income": income,
            "total_expenditure": total_expenditure,
            "savings": savings,
            "investments": investments,
            "essentials_total": essentials,
            "discretionary_total": discretionary,
            "future_total": future,
            "surplus_before_savings": surplus_before_savings,
            "expense_ratio": _safe_ratio(total_expenditure, income),
            "savings_ratio": _safe_ratio(savings, income),
            "investment_ratio": _safe_ratio(investments, income),
            "future_ratio": _safe_ratio(future, income),
            "essentials_ratio": _safe_ratio(essentials, income),
            "discretionary_ratio": _safe_ratio(discretionary, income),
            "rent_share_of_expense": _safe_ratio(record.get("Rent"), total_expenditure),
            "groceries_share_of_expense": _safe_ratio(record.get("Groceries"), total_expenditure),
            "investment_share_of_expense": _safe_ratio(investments, total_expenditure),
            "healthcare_share_of_expense": _safe_ratio(record.get("Healthcare"), total_expenditure),
            "has_emi": 1 if record.get("EMI/Loans") > 0 else 0,
        }

        for category in CATEGORY_COLUMNS:
            slug = (
                category.lower()
                .replace(" & ", "_")
                .replace("/", "_")
                .replace(" ", "_")
            )
            value = record.get(category)
            feature_row[f"{slug}"] = value
            if category != "Savings":
                feature_row[f"{slug}_expense_share"] = _safe_ratio(value, total_expenditure)
            feature_row[f"{slug}_income_share"] = _safe_ratio(value, income)

            if previous is not None:
                prev_value = previous.get(category)
                feature_row[f"{slug}_lag1"] = prev_value
                feature_row[f"{slug}_mom_change"] = value - prev_value
                pct_change = percentage_change(value, prev_value)
                feature_row[f"{slug}_mom_change_pct"] = pct_change if pct_change is not None else 0.0
            else:
                feature_row[f"{slug}_lag1"] = 0.0
                feature_row[f"{slug}_mom_change"] = 0.0
                feature_row[f"{slug}_mom_change_pct"] = 0.0

            if trailing_3:
                trailing_mean = sum(item.get(category) for item in trailing_3) / len(trailing_3)
                feature_row[f"{slug}_rolling3_mean"] = trailing_mean
                feature_row[f"{slug}_vs_rolling3"] = value - trailing_mean
            else:
                feature_row[f"{slug}_rolling3_mean"] = 0.0
                feature_row[f"{slug}_vs_rolling3"] = 0.0

        if previous is not None:
            feature_row["income_lag1"] = previous.get("Income")
            feature_row["income_mom_change"] = income - previous.get("Income")
            feature_row["expenditure_lag1"] = previous.get("Total Expenditure")
            feature_row["expenditure_mom_change"] = total_expenditure - previous.get("Total Expenditure")
            expenditure_pct_change = percentage_change(total_expenditure, previous.get("Total Expenditure"))
            feature_row["expenditure_mom_change_pct"] = expenditure_pct_change if expenditure_pct_change is not None else 0.0
        else:
            feature_row["income_lag1"] = 0.0
            feature_row["income_mom_change"] = 0.0
            feature_row["expenditure_lag1"] = 0.0
            feature_row["expenditure_mom_change"] = 0.0
            feature_row["expenditure_mom_change_pct"] = 0.0

        if trailing_3:
            trailing_exp_mean = sum(item.get("Total Expenditure") for item in trailing_3) / len(trailing_3)
            trailing_income_mean = sum(item.get("Income") for item in trailing_3) / len(trailing_3)
            trailing_savings_mean = sum(item.get("Savings") for item in trailing_3) / len(trailing_3)
            feature_row["expenditure_rolling3_mean"] = trailing_exp_mean
            feature_row["income_rolling3_mean"] = trailing_income_mean
            feature_row["savings_rolling3_mean"] = trailing_savings_mean
            feature_row["expenditure_vs_rolling3"] = total_expenditure - trailing_exp_mean
            feature_row["income_vs_rolling3"] = income - trailing_income_mean
            feature_row["savings_vs_rolling3"] = savings - trailing_savings_mean
        else:
            feature_row["expenditure_rolling3_mean"] = 0.0
            feature_row["income_rolling3_mean"] = 0.0
            feature_row["savings_rolling3_mean"] = 0.0
            feature_row["expenditure_vs_rolling3"] = 0.0
            feature_row["income_vs_rolling3"] = 0.0
            feature_row["savings_vs_rolling3"] = 0.0

        rows.append(feature_row)

    for index, feature_row in enumerate(rows):
        next_expenditure = rows[index + 1]["total_expenditure"] if index + 1 < len(rows) else ""
        next_savings = rows[index + 1]["savings"] if index + 1 < len(rows) else ""
        next_income = rows[index + 1]["income"] if index + 1 < len(rows) else ""
        feature_row["target_next_month_expenditure"] = next_expenditure
        feature_row["target_next_month_savings"] = next_savings
        feature_row["target_next_month_income"] = next_income

    return rows


def write_feature_dataset(input_csv_path: str | Path, output_csv_path: str | Path) -> Path:
    rows = build_feature_rows(input_csv_path)
    output_path = Path(output_csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    input_path = root / "_dataset_extract" / "monthly_spending_dataset_2020_2025.csv"
    output_path = root / "generated" / "ml_features_monthly_spending.csv"
    write_feature_dataset(input_path, output_path)
    print(output_path)


if __name__ == "__main__":
    main()


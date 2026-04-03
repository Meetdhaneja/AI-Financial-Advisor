from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .data_utils import (
    CATEGORY_COLUMNS,
    DISCRETIONARY_COLUMNS,
    ESSENTIAL_COLUMNS,
    EXPENSE_COLUMNS,
    FUTURE_COLUMNS,
    MonthlyRecord,
    load_monthly_records,
    percentage_change,
    rolling_mean,
)


@dataclass
class Insight:
    kind: str
    title: str
    message: str
    value: float | None = None
    change_pct: float | None = None


def _bucket_total(record: MonthlyRecord, columns: list[str]) -> float:
    return sum(record.get(column) for column in columns)


def _format_currency(value: float) -> str:
    return f"₹{value:,.0f}"


def _format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _top_category(record: MonthlyRecord, columns: list[str]) -> tuple[str, float]:
    pairs = [(column, record.get(column)) for column in columns]
    return max(pairs, key=lambda item: item[1])


def generate_monthly_insights(
    records: list[MonthlyRecord],
    month_index: int = -1,
    comparison_window: int = 3,
) -> list[Insight]:
    if not records:
        return []

    resolved_index = month_index if month_index >= 0 else len(records) + month_index
    if resolved_index < 0 or resolved_index >= len(records):
        raise IndexError("month_index is out of range.")

    current = records[resolved_index]
    previous = records[resolved_index - 1] if resolved_index > 0 else None
    trailing_records = records[max(0, resolved_index - comparison_window) : resolved_index]

    total_expenditure = current.get("Total Expenditure")
    income = current.get("Income")
    savings = current.get("Savings")
    investments = current.get("Investments")
    essentials = _bucket_total(current, ESSENTIAL_COLUMNS)
    discretionary = _bucket_total(current, DISCRETIONARY_COLUMNS)
    future = _bucket_total(current, FUTURE_COLUMNS)
    surplus = income - total_expenditure - savings
    expense_ratio = total_expenditure / income if income else 0.0
    savings_ratio = savings / income if income else 0.0
    investment_ratio = investments / income if income else 0.0

    insights: list[Insight] = [
        Insight(
            kind="health",
            title="Budget Health",
            message=(
                f"In {current.month.isoformat()}, spending used {_format_percent(expense_ratio)} "
                f"of income, leaving {_format_currency(income - total_expenditure)} before savings."
            ),
            value=expense_ratio,
        ),
        Insight(
            kind="allocation",
            title="Future Allocation",
            message=(
                f"You allocated {_format_currency(future)} toward savings and investments, which is "
                f"{_format_percent((future / income) if income else 0.0)} of income."
            ),
            value=future,
        ),
        Insight(
            kind="mix",
            title="Spending Mix",
            message=(
                f"Essentials were {_format_currency(essentials)} and discretionary spend was "
                f"{_format_currency(discretionary)}."
            ),
            value=essentials,
        ),
    ]

    top_category, top_value = _top_category(current, EXPENSE_COLUMNS)
    insights.append(
        Insight(
            kind="driver",
            title="Largest Cost Driver",
            message=(
                f"The biggest expenditure category was {top_category} at {_format_currency(top_value)}, "
                f"or {_format_percent(top_value / total_expenditure if total_expenditure else 0.0)} of spending."
            ),
            value=top_value,
        )
    )

    if previous is not None:
        expenditure_change = percentage_change(total_expenditure, previous.get("Total Expenditure"))
        if expenditure_change is not None:
            direction = "up" if expenditure_change >= 0 else "down"
            insights.append(
                Insight(
                    kind="trend",
                    title="Month-on-Month Expenditure",
                    message=(
                        f"Total expenditure is {direction} {_format_percent(abs(expenditure_change))} "
                        f"from the previous month."
                    ),
                    value=total_expenditure,
                    change_pct=expenditure_change,
                )
            )

        for category in ["Groceries", "Healthcare", "EMI/Loans", "Investments", "Savings"]:
            change = percentage_change(current.get(category), previous.get(category))
            if change is None:
                continue
            if abs(change) >= 0.15:
                direction = "increased" if change > 0 else "decreased"
                insights.append(
                    Insight(
                        kind="category_change",
                        title=f"{category} Shift",
                        message=(
                            f"{category} {direction} by {_format_percent(abs(change))} versus last month, "
                            f"reaching {_format_currency(current.get(category))}."
                        ),
                        value=current.get(category),
                        change_pct=change,
                    )
                )

    if trailing_records:
        trailing_exp_mean = rolling_mean(trailing_records, "Total Expenditure")
        trailing_savings_mean = rolling_mean(trailing_records, "Savings")
        exp_change = percentage_change(total_expenditure, trailing_exp_mean)
        savings_change = percentage_change(savings, trailing_savings_mean)

        if exp_change is not None and abs(exp_change) >= 0.10:
            direction = "above" if exp_change > 0 else "below"
            insights.append(
                Insight(
                    kind="anomaly",
                    title="Expenditure vs Recent Trend",
                    message=(
                        f"This month's expenditure is {_format_percent(abs(exp_change))} {direction} "
                        f"the recent {comparison_window}-month average."
                    ),
                    value=total_expenditure,
                    change_pct=exp_change,
                )
            )

        if savings_change is not None and abs(savings_change) >= 0.10:
            direction = "higher" if savings_change > 0 else "lower"
            insights.append(
                Insight(
                    kind="savings_trend",
                    title="Savings Momentum",
                    message=(
                        f"Savings are {_format_percent(abs(savings_change))} {direction} than the recent "
                        f"{comparison_window}-month average."
                    ),
                    value=savings,
                    change_pct=savings_change,
                )
            )

    if expense_ratio >= 0.90:
        insights.append(
            Insight(
                kind="alert",
                title="High Spending Pressure",
                message="Spending is above 90% of income, so cash flow is tight this month.",
                value=expense_ratio,
            )
        )
    elif expense_ratio <= 0.65:
        insights.append(
            Insight(
                kind="positive",
                title="Strong Cash Flow Month",
                message="Spending is comfortably below 65% of income, giving you room for goals or buffers.",
                value=expense_ratio,
            )
        )

    if savings_ratio >= 0.15 and investment_ratio >= 0.12:
        insights.append(
            Insight(
                kind="positive",
                title="Healthy Wealth Building",
                message="Both savings and investments are taking a meaningful share of income this month.",
                value=savings_ratio + investment_ratio,
            )
        )

    if current.get("EMI/Loans") > 0:
        insights.append(
            Insight(
                kind="debt",
                title="Debt Commitment",
                message=(
                    f"EMI/Loans contributed {_format_currency(current.get('EMI/Loans'))} this month, so debt "
                    "should be included in affordability planning."
                ),
                value=current.get("EMI/Loans"),
            )
        )

    if surplus < 0:
        insights.append(
            Insight(
                kind="alert",
                title="Savings Overstretch",
                message=(
                    "Savings allocation exceeds the amount left after expenditure, so this month may need "
                    "rebalancing between saving and liquidity."
                ),
                value=surplus,
            )
        )

    return insights


def insights_to_dicts(insights: list[Insight]) -> list[dict[str, object]]:
    return [asdict(insight) for insight in insights]


def generate_insights_for_csv(csv_path: str | Path, month_index: int = -1) -> list[dict[str, object]]:
    records = load_monthly_records(csv_path)
    return insights_to_dicts(generate_monthly_insights(records, month_index=month_index))


def main() -> None:
    dataset_path = Path(__file__).resolve().parents[1] / "_dataset_extract" / "monthly_spending_dataset_2020_2025.csv"
    insights = generate_insights_for_csv(dataset_path)
    print(json.dumps(insights, indent=2))


if __name__ == "__main__":
    main()


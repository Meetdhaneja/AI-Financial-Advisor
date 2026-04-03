from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Goal, Transaction, User


async def build_finance_summary(
    db: AsyncSession,
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    user = await db.scalar(select(User).where(User.id == user_id))
    query = (
        select(Transaction)
        .options(selectinload(Transaction.category))
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.occurred_at.asc())
    )
    if start_date:
        query = query.where(Transaction.occurred_at >= start_date)
    if end_date:
        query = query.where(Transaction.occurred_at <= end_date)

    transactions = (await db.scalars(query)).all()
    total_income = 0.0
    total_expenses = 0.0
    anomaly_count = 0
    category_totals: dict[tuple[str, str], float] = defaultdict(float)
    monthly: dict[str, dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    monthly_categories: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for transaction in transactions:
        month_key = transaction.occurred_at.replace(day=1).isoformat()
        category_name = transaction.category.name if transaction.category else "Unknown"
        category_totals[(category_name, transaction.transaction_type)] += transaction.amount
        monthly[month_key][transaction.transaction_type] += transaction.amount
        if transaction.transaction_type == "expense":
            monthly_categories[month_key][category_name] += transaction.amount

        if transaction.transaction_type == "income":
            total_income += transaction.amount
        else:
            total_expenses += transaction.amount
        if transaction.is_anomaly:
            anomaly_count += 1

    ordered_months = sorted(monthly.items(), key=lambda item: item[0])
    latest_month, latest_values = ordered_months[-1] if ordered_months else (None, {"income": 0.0, "expense": 0.0})
    previous_month, previous_values = ordered_months[-2] if len(ordered_months) > 1 else (None, {"income": 0.0, "expense": 0.0})
    rolling_three = ordered_months[-4:-1] if len(ordered_months) >= 4 else ordered_months[:-1]
    rolling_expense_avg = (
        sum(item[1]["expense"] for item in rolling_three) / len(rolling_three)
        if rolling_three
        else latest_values["expense"]
    )

    latest_categories = monthly_categories.get(latest_month or "", {})
    previous_categories = monthly_categories.get(previous_month or "", {})
    user_budgets = (user.category_budget_preferences or {}) if user else {}
    budget_progress = []
    for category, current_amount in sorted(latest_categories.items(), key=lambda item: item[1], reverse=True):
        budget_target = float(user_budgets.get(category, 0.0)) if user_budgets.get(category) is not None else 0.0
        progress = (current_amount / budget_target) if budget_target else 0.0
        budget_progress.append(
            {
                "category": category,
                "current": round(current_amount, 2),
                "target": round(budget_target, 2),
                "progress": round(progress, 3),
                "status": "over" if budget_target and current_amount > budget_target else "within",
            }
        )

    changed_categories = []
    for category, current_amount in latest_categories.items():
        previous_amount = previous_categories.get(category, 0.0)
        if previous_amount == 0 and current_amount > 0:
            delta_pct = 1.0
        elif previous_amount == 0:
            delta_pct = 0.0
        else:
            delta_pct = (current_amount - previous_amount) / previous_amount
        changed_categories.append((category, current_amount, previous_amount, delta_pct))
    changed_categories.sort(key=lambda item: abs(item[3]), reverse=True)

    plain_english_insights = []
    if latest_values["expense"] > rolling_expense_avg:
        plain_english_insights.append(
            f"Your spending this month is {((latest_values['expense'] - rolling_expense_avg) / max(rolling_expense_avg, 1)) * 100:.0f}% above your recent 3-month average."
        )
    else:
        plain_english_insights.append("Your spending this month is stable compared with your recent average.")
    if changed_categories:
        top_change = changed_categories[0]
        direction = "above" if top_change[3] >= 0 else "below"
        plain_english_insights.append(
            f"{top_change[0]} is {abs(top_change[3]) * 100:.0f}% {direction} last month."
        )
    if budget_progress:
        over_budget = [item for item in budget_progress if item["status"] == "over"]
        if over_budget:
            plain_english_insights.append(
                f"You are over budget in {len(over_budget)} categories, led by {over_budget[0]['category']}."
            )

    what_changed = []
    if latest_month:
        what_changed.append(
            f"Total expenses in {latest_month} were Rs {latest_values['expense']:.0f} compared with Rs {previous_values['expense']:.0f} last month."
        )
    for category, current_amount, previous_amount, delta_pct in changed_categories[:3]:
        what_changed.append(
            f"{category} moved from Rs {previous_amount:.0f} to Rs {current_amount:.0f}, a change of {delta_pct * 100:.0f}%."
        )

    goals = (await db.scalars(select(Goal).where(Goal.user_id == user_id))).all()
    emergency_progress = 0.0
    emergency_goal = next((goal for goal in goals if goal.goal_type == "emergency_fund"), None)
    if emergency_goal and emergency_goal.target_amount:
        emergency_progress = emergency_goal.current_amount / emergency_goal.target_amount

    savings_rate = (total_income - total_expenses) / total_income if total_income else 0.0
    debt_load = latest_categories.get("EMI/Loans", 0.0) / max(latest_values["income"], 1) if latest_month else 0.0
    overspending_frequency = (
        len([item for item in budget_progress if item["status"] == "over"]) / max(len(budget_progress), 1)
        if budget_progress
        else 0.0
    )
    financial_health_score = max(
        0.0,
        min(
            100.0,
            (
                savings_rate * 45
                + (1 - min(debt_load, 1.0)) * 20
                + (1 - overspending_frequency) * 20
                + min(emergency_progress, 1.0) * 15
            ),
        ),
    )

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cashflow": total_income - total_expenses,
        "savings_rate": savings_rate,
        "financial_health_score": round(financial_health_score, 1),
        "anomaly_count": anomaly_count,
        "category_breakdown": [
            {"category": category, "amount": amount, "transaction_type": transaction_type}
            for (category, transaction_type), amount in sorted(
                category_totals.items(), key=lambda item: item[1], reverse=True
            )
        ],
        "monthly_trends": [
            {"month": month, **values} for month, values in sorted(monthly.items(), key=lambda item: item[0])
        ],
        "budget_progress": budget_progress[:8],
        "plain_english_insights": plain_english_insights,
        "what_changed": what_changed,
    }

import pytest


async def _bootstrap_user_history(client):
    payload = {
        "email": "ai@example.com",
        "password": "Password123",
        "full_name": "AI User",
        "monthly_income_default": 90000,
        "risk_profile": "high",
    }
    await client.post("/api/v1/auth/register", json=payload)
    login = await client.post("/api/v1/auth/login/json", json={"email": payload["email"], "password": payload["password"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    categories = (await client.get("/api/v1/transactions/categories")).json()
    salary = next(item for item in categories if item["name"] == "Salary")
    rent = next(item for item in categories if item["name"] == "Rent")
    dining = next(item for item in categories if item["name"] == "Dining & Entertainment")

    for month in ["2025-01-01", "2025-02-01", "2025-03-01"]:
        await client.post(
            "/api/v1/transactions",
            json={"category_id": salary["id"], "amount": 90000, "transaction_type": "income", "occurred_at": month},
            headers=headers,
        )
        await client.post(
            "/api/v1/transactions",
            json={"category_id": rent["id"], "amount": 18000, "transaction_type": "expense", "occurred_at": month},
            headers=headers,
        )
        await client.post(
            "/api/v1/transactions",
            json={"category_id": dining["id"], "amount": 12000, "transaction_type": "expense", "occurred_at": month},
            headers=headers,
        )
    return headers


@pytest.mark.asyncio
async def test_prediction_and_budget_endpoints(client):
    headers = await _bootstrap_user_history(client)
    prediction = await client.post("/api/v1/ai/predict-expense", json={}, headers=headers)
    assert prediction.status_code == 200
    assert prediction.json()["predicted_amount"] > 0

    analysis = await client.post("/api/v1/ai/analyze-spending", json={}, headers=headers)
    assert analysis.status_code == 200
    assert analysis.json()["risk_level"] in {"low", "medium", "high"}

    recommendation = await client.get("/api/v1/ai/recommend-budget", headers=headers)
    assert recommendation.status_code == 200
    assert "budget_plan" in recommendation.json()


@pytest.mark.asyncio
async def test_goals_recurring_and_simulator(client):
    headers = await _bootstrap_user_history(client)
    goal_response = await client.post(
        "/api/v1/ai/goals",
        json={
            "name": "Emergency Fund",
            "goal_type": "emergency_fund",
            "target_amount": 300000,
            "current_amount": 75000,
            "target_months": 12,
        },
        headers=headers,
    )
    assert goal_response.status_code == 201

    categories = (await client.get("/api/v1/transactions/categories")).json()
    rent = next(item for item in categories if item["name"] == "Rent")
    recurring_response = await client.post(
        "/api/v1/ai/recurring",
        json={
            "category_id": rent["id"],
            "name": "Monthly Rent",
            "amount": 18000,
            "transaction_type": "expense",
            "frequency": "monthly",
            "day_of_month": 5,
        },
        headers=headers,
    )
    assert recurring_response.status_code == 201

    scenario_response = await client.post(
        "/api/v1/ai/simulate-scenario",
        json={"income_change": 10000, "expense_change": -2000, "savings_change": 1500},
        headers=headers,
    )
    assert scenario_response.status_code == 200
    assert scenario_response.json()["projected_income"] > 0

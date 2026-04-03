import pytest


async def _get_token(client):
    payload = {
        "email": "finance@example.com",
        "password": "Password123",
        "full_name": "Finance User",
        "monthly_income_default": 70000,
        "risk_profile": "medium",
    }
    await client.post("/api/v1/auth/register", json=payload)
    login = await client.post("/api/v1/auth/login/json", json={"email": payload["email"], "password": payload["password"]})
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_create_and_list_transactions(client):
    token = await _get_token(client)
    categories = await client.get("/api/v1/transactions/categories")
    expense_category = next(item for item in categories.json() if item["name"] == "Groceries")
    income_category = next(item for item in categories.json() if item["name"] == "Salary")

    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/v1/transactions",
        json={
            "category_id": income_category["id"],
            "amount": 80000,
            "transaction_type": "income",
            "occurred_at": "2025-01-01",
            "description": "Monthly salary",
        },
        headers=headers,
    )
    create_response = await client.post(
        "/api/v1/transactions",
        json={
            "category_id": expense_category["id"],
            "amount": 6500,
            "transaction_type": "expense",
            "occurred_at": "2025-01-03",
            "description": "Groceries",
        },
        headers=headers,
    )
    assert create_response.status_code == 201

    list_response = await client.get("/api/v1/transactions", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 2

    summary_response = await client.get("/api/v1/finance/summary", headers=headers)
    assert summary_response.status_code == 200
    assert summary_response.json()["total_income"] == 80000


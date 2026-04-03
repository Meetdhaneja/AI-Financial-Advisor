import pytest


@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    register_payload = {
        "email": "user@example.com",
        "password": "Password123",
        "full_name": "Demo User",
        "monthly_income_default": 65000,
        "risk_profile": "medium",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    assert register_response.json()["email"] == register_payload["email"]

    login_response = await client.post(
        "/api/v1/auth/login/json",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test that the health endpoint returns 200 OK."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "IntelPulse API"


@pytest.mark.asyncio
async def test_user_signup_and_login(client):
    """Test user registration and subsequent login to receive JWT."""
    user_payload = {
        "email": "testuser@intelpulse.com",
        "password": "testpassword123"
    }

    # 1. Signup
    signup_res = await client.post("/api/v1/auth/signup", json=user_payload)
    assert signup_res.status_code == 201
    assert signup_res.json()["email"] == "testuser@intelpulse.com"

    # 2. Login
    login_data = {
        "username": "testuser@intelpulse.com",
        "password": "testpassword123"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_analytics_protected_route(client):
    """Test that /analytics/analyze requires authentication."""
    # Attempting request without token should fail with 401 Unauthorized
    response = await client.post("/api/v1/analytics/analyze", json={"ticker": "AAPL", "days": 30})
    assert response.status_code == 401
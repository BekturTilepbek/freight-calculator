import pytest


class TestAuthRegistration:
    async def test_register_new_user(self, client):
        """Успешная регистрация возвращает токен и данные пользователя."""
        r = await client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "secret123",
            "full_name": "New User",
        })
        assert r.status_code == 201
        data = r.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser@test.com"
        assert data["user"]["role"] == "dispatcher"  # дефолтная роль

    async def test_register_duplicate_email_fails(self, client):
        """Повторная регистрация с тем же email возвращает 409."""
        payload = {
            "email": "dup@test.com",
            "password": "secret123",
            "full_name": "Dup User",
        }
        await client.post("/api/v1/auth/register", json=payload)
        r = await client.post("/api/v1/auth/register", json=payload)
        assert r.status_code == 409

    async def test_register_invalid_email_rejected(self, client):
        """Невалидный формат email отклоняется на этапе валидации."""
        r = await client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "secret123",
            "full_name": "X",
        })
        assert r.status_code == 422


class TestAuthLogin:
    async def test_login_with_valid_credentials(self, client, dispatcher_user):
        r = await client.post("/api/v1/auth/login", json={
            "email": "dispatcher@test.com",
            "password": "disp_pass",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    async def test_login_with_wrong_password(self, client, dispatcher_user):
        r = await client.post("/api/v1/auth/login", json={
            "email": "dispatcher@test.com",
            "password": "WRONG",
        })
        assert r.status_code == 401

    async def test_login_with_nonexistent_user(self, client):
        r = await client.post("/api/v1/auth/login", json={
            "email": "ghost@test.com",
            "password": "any",
        })
        assert r.status_code == 401


class TestProtectedEndpoints:
    async def test_access_without_token_fails(self, client):
        r = await client.get("/api/v1/orders")
        assert r.status_code == 401

    async def test_access_with_invalid_token_fails(self, client):
        r = await client.get(
            "/api/v1/orders",
            headers={"Authorization": "Bearer not-a-real-token"},
        )
        assert r.status_code == 401

    async def test_access_with_valid_token_succeeds(self, client, dispatcher_headers):
        r = await client.get("/api/v1/orders", headers=dispatcher_headers)
        assert r.status_code == 200

    async def test_me_returns_current_user(self, client, dispatcher_headers):
        r = await client.get("/api/v1/auth/me", headers=dispatcher_headers)
        assert r.status_code == 200
        assert r.json()["email"] == "dispatcher@test.com"
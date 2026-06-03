def test_register_login_and_me(client):
    register = client.post(
        "/api/auth/register",
        json={"email": "new@lumin.dev", "username": "new_user", "password": "password123", "role": "student"},
    )
    assert register.status_code == 201
    assert register.json()["role"]["name"] == "student"

    login = client.post("/api/auth/login", json={"username": "new_user", "password": "password123"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "new_user"

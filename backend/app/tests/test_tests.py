def auth_headers(client, role="teacher", username="teacher_one"):
    client.post(
        "/api/auth/register",
        json={"email": f"{username}@lumin.dev", "username": username, "password": "password123", "role": role},
    )
    token = client.post("/api/auth/login", json={"username": username, "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_teacher_can_create_test_and_student_can_attempt(client):
    teacher_headers = auth_headers(client)
    create = client.post(
        "/api/tests",
        headers=teacher_headers,
        json={
            "title": "Python Basics",
            "description": "Core syntax",
            "category_id": 1,
            "questions": [
                {
                    "body": "What is list comprehension?",
                    "kind": "single_choice",
                    "points": 10,
                    "answers": [{"body": "A compact list construction syntax", "is_correct": True}, {"body": "A database index", "is_correct": False}],
                }
            ],
        },
    )
    assert create.status_code == 201
    test = create.json()
    question = test["questions"][0]
    correct = [answer["id"] for answer in question["answers"] if answer["is_correct"]]

    student_headers = auth_headers(client, role="student", username="student_one")
    result = client.post(f"/api/tests/{test['id']}/attempts", headers=student_headers, json={"answers": {str(question["id"]): correct}, "duration_seconds": 12})
    assert result.status_code == 200
    assert result.json()["percent"] == 100

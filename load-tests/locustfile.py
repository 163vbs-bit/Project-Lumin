from locust import HttpUser, between, task


class LuminUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post("/api/auth/login", json={"username": "demo_student", "password": "password123"})
        self.token = response.json().get("access_token", "")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_tests(self):
        self.client.get("/api/tests?limit=12", headers=self.headers)

    @task(2)
    def dashboard(self):
        self.client.get("/api/analytics/dashboard", headers=self.headers)

    @task(1)
    def leaderboard(self):
        self.client.get("/api/users/leaderboard", headers=self.headers)

from locust import HttpUser, task, between


class AIUser(HttpUser):

    wait_time = between(1, 3)

    @task
    def submit_chat(self):

        response = self.client.post(
            "/api/chat/",
            json={
                "user_id": "load-test-user",
                "message": "Calculate 25 * 40",
            },
        )

        if response.status_code != 202:
            response.failure(
                f"Unexpected status: {response.status_code}"
            )
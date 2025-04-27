from locust import HttpUser, task, between
import json

class StoryUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    @task(1)
    def generate_story(self):
        payload = {
            "theme": "comedy",
            "source": "all"
        }
        self.client.post("/generate", json=payload)
    
    @task(2)
    def check_health(self):
        self.client.get("/") 
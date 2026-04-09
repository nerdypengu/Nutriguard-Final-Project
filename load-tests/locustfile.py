import uuid
import random
from locust import HttpUser, task, between

class NutriGuardUser(HttpUser):
    wait_time = between(1, 4)

    def on_start(self):
        """
        Sign up a new unique user to get a JWT token.
        This provides a unique user session for each simulated worker user.
        """
        self.email = f"loadtest_{uuid.uuid4()}@example.com"
        password = "password123"
        self.pending_jobs = {}  # Store job_id -> timestamp for tracking
        
        # 1. Sign up to create the user account (we ignore the response since the token might be missing)
        self.client.post("/api/auth/signup", json={
            "email": self.email,
            "password": password
        }, name="/api/auth/signup")
        
        # 2. Sign in with the exact same credentials to properly grab the JWT token
        response = self.client.post("/api/auth/signin", json={
            "email": self.email,
            "password": password
        }, name="/api/auth/signin")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                
                # Keep token headers for subsequent requests
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def view_all_foods(self):
        """Simulate user browsing the food library"""
        if self.token:
            self.client.get("/api/food/", name="/api/food/")

    @task(2)
    def search_food(self):
        """Simulate user searching for specific foods"""
        if self.token:
            queries = ["ayam", "nasi", "telur", "sapi", "susu", "pisang", "roti"]
            query = random.choice(queries)
            self.client.get(f"/api/food/search/by-name?name={query}", name="/api/food/search/by-name")

    @task(1)
    def process_meal_chat(self):
        """Simulate user asking the chat AI about a meal"""
        if self.token and self.user_id:
            messages = [
                "Berapa kalori dalam 100g ayam goreng?",
                "Apakah nasi padang sehat?",
                "Saya makan 1 porsi sate ayam, berapa nutrisinya?",
                "Berapa protein di 2 butir telur rebus?",
                "Tolong analisa kandungan 1 mangkok salad buah."
            ]
            response = self.client.post("/api/meal-processing/chat", json={
                "user_id": self.user_id,
                "message": random.choice(messages)
            }, name="/api/meal-processing/chat")
            
            # Store job_id for polling
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                if job_id:
                    import time
                    self.pending_jobs[job_id] = time.time()

    @task(2)
    def check_meal_processing_result(self):
        """Poll the status of pending meal processing jobs"""
        if self.token and self.pending_jobs:
            # Get a job_id from pending jobs
            job_id = random.choice(list(self.pending_jobs.keys()))
            
            response = self.client.get(
                f"/api/meal-processing/status/{job_id}",
                name="/api/meal-processing/status"
            )
            
            # If completed, remove from pending jobs
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status in ["COMPLETED", "FAILED"]:
                    self.pending_jobs.pop(job_id, None)
            elif response.status_code == 404:
                # Job not found, remove from pending
                self.pending_jobs.pop(job_id, None)

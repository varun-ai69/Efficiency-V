import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

async def run_test():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Register a test user
        register_payload = {
            "email": "testprofile@example.com",
            "password": "password123",
            "full_name": "Test User",
            "role": "patient"
        }
        res = await client.post("/api/v1/auth/register", json=register_payload)
        
        # If user exists, try logging in
        if res.status_code == 400:
            res = await client.post("/api/v1/auth/login", json={"email": "testprofile@example.com", "password": "password123"})
            token = res.json()["access_token"]
        else:
            token = res.json()["access_token"]
            
        print("Logged in, token received.")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create profile
        profile_data = {
            "age": 30,
            "gender": 1,
            "race": 0,
            "lang": 0,
            "insurance_status": 1,
            "height_m": 1.75,
            "weight_kg": 75.0,
            "previous_ed_visits": 0,
            "previous_admissions": 0,
            "diabetes": 0.0,
            "asthma": 1.0,
            "takes_inhaler": 1.0
        }
        
        res = await client.post("/api/v1/profile", json=profile_data, headers=headers)
        print(f"Create Profile Status: {res.status_code}")
        print(res.json())
        
        # Get profile
        res = await client.get("/api/v1/profile/me", headers=headers)
        print(f"Get Profile Status: {res.status_code}")
        print(res.json())

if __name__ == "__main__":
    asyncio.run(run_test())

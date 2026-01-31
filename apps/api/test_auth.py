"""
Test script for auth endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_register():
    """Test user registration"""
    print("\n1. Testing POST /auth/register...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "password123",
            "role": "seeker"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["access_token"]
    return None


def test_login():
    """Test user login"""
    print("\n2. Testing POST /auth/login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "password123"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_get_me(token):
    """Test GET /auth/me with token"""
    print("\n3. Testing GET /auth/me...")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_me_invalid_token():
    """Test GET /auth/me with invalid token"""
    print("\n4. Testing GET /auth/me with invalid token...")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("=" * 60)
    print("EPIC 3 - Authentication Testing")
    print("=" * 60)
    
    # Test registration
    token = test_register()
    
    if token:
        # Test protected endpoint with token from registration
        test_get_me(token)
    
    # Test login
    token = test_login()
    
    if token:
        # Test protected endpoint with token from login
        test_get_me(token)
    
    # Test invalid token
    test_get_me_invalid_token()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)

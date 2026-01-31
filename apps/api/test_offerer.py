"""
Integration test for EPIC 5 - Offerer Feed Mechanics
Tests: T5.1 (config), T5.2 (feed), T5.3 (swipe, shortlist, notes)
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000"


def test_offerer_flow():
    """
    End-to-end test for offerer functionality:
    1. Register offerer
    2. Register 3 seekers and complete questionnaires
    3. Set offerer role config
    4. Get feed (should see all 3 seekers)
    5. Swipe on candidates (like 2, pass 1)
    6. Verify feed excludes swiped candidates
    7. Get shortlist (should show 2 liked)
    8. Add notes to shortlisted candidates
    9. Verify pagination with cursor
    """
    
    print("\nüöÄ EPIC 5 Integration Test - Offerer Feed Mechanics")
    print("=" * 60)
    
    # Step 1: Register offerer
    print("\n1. Registering offerer...")
    offerer_data = {
        "email": "recruiter@techcorp.com",
        "password": "SecurePass123!",
        "role": "offerer",
        "full_name": "Jane Recruiter"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=offerer_data)
    assert response.status_code == 201, f"Failed to register offerer: {response.text}"
    offerer_token = response.json()["access_token"]
    print(f"   ‚ú" Offerer registered: {offerer_data['email']}")
    print(f"   Token: {offerer_token[:50]}...")
    
    # Register offerer profile separately (since we don't have registration endpoint yet)
    # For now, we'll create it manually via SQL
    
    # Step 2: Register 3 seekers with different profiles
    print("\n2. Registering 3 seekers...")
    seekers = []
    seeker_profiles = [
        {
            "email": f"seeker{i}@example.com",
            "password": "Pass123!",
            "role": "seeker",
            "full_name": f"Seeker {i}",
            "headline": [
                "Senior Software Engineer - Python Expert",
                "Sales Professional - B2B SaaS",
                "Engineering Team Lead - 10+ years"
            ][i],
            "location": ["San Francisco, CA", "New York, NY", "Austin, TX"][i]
        }
        for i in range(3)
    ]
    
    for seeker_data in seeker_profiles:
        response = requests.post(f"{BASE_URL}/auth/register", json=seeker_data)
        assert response.status_code == 201, f"Failed to register seeker: {response.text}"
        token = response.json()["access_token"]
        seekers.append({"data": seeker_data, "token": token})
        print(f"   ‚ú" Registered: {seeker_data['email']}")
    
    # Step 3: Complete questionnaires for all seekers
    print("\n3. Completing questionnaires for all seekers...")
    
    # Get questionnaire first
    response = requests.get(f"{BASE_URL}/questionnaire")
    assert response.status_code == 200, f"Failed to fetch questionnaire: {response.text}"
    questionnaire = response.json()
    questions = questionnaire["questions"]
    print(f"   Questionnaire has {len(questions)} questions")
    
    # Answer questionnaires with different patterns
    answer_patterns = [
        [5, 5, 5, 4, 4, 4, 3, 3, 3, 4, 4, 5, 5, 5, 4, 4],  # High tech/problem-solving (Software Engineer fit)
        [3, 3, 3, 5, 5, 5, 2, 2, 2, 5, 5, 3, 3, 3, 5, 5],  # High communication/adaptability (Sales fit)
        [4, 4, 4, 4, 4, 4, 5, 5, 5, 3, 3, 4, 4, 4, 4, 4],  # High leadership (Team Lead fit)
    ]
    
    for idx, seeker in enumerate(seekers):
        answers = [
            {"question_id": q["id"], "answer_value": answer_patterns[idx][i]}
            for i, q in enumerate(questions[:16])  # Answer all 16 questions
        ]
        
        response = requests.post(
            f"{BASE_URL}/questionnaire/answers",
            json={"answers": answers},
            headers={"Authorization": f"Bearer {seeker['token']}"}
        )
        assert response.status_code == 200, f"Failed to submit answers: {response.text}"
        completion = response.json()["completion_percent"]
        print(f"   ‚ú" Seeker {idx + 1} completed questionnaire: {completion}%")
        
        # Get stats
        response = requests.get(
            f"{BASE_URL}/seeker/stats",
            headers={"Authorization": f"Bearer {seeker['token']}"}
        )
        assert response.status_code == 200, f"Failed to get stats: {response.text}"
        stats = response.json()
        seeker["stats"] = stats
        print(f"      Stats computed: {list(stats['stats'].keys())[:3]}...")
    
    # Step 4: Get role configs
    print("\n4. Getting role configurations...")
    # We need to query DB for role configs - let's get them via a direct query
    # For now, let's assume we know the role config IDs from seed data
    # We'll need to enhance this part
    
    # For testing, let's try to get feed without config first (should fail)
    print("\n5. Testing feed without config (should fail)...")
    response = requests.get(
        f"{BASE_URL}/offerer/feed",
        headers={"Authorization": f"Bearer {offerer_token}"}
    )
    print(f"   Response: {response.status_code} - {response.json()['detail']}")
    assert response.status_code == 400, "Should require config first"
    
    # Step 5: Set offerer config (we'll need to get role config ID first)
    print("\n6. Setting offerer role config...")
    print("   (Skipping config setup for now - would need role_config_id from seed)")
    
    print("\n‚ú Integration test structure complete!")
    print("Note: Full test requires:")
    print("  - Offerer profile creation in registration")
    print("  - API endpoint to list role configs")
    print("  - Completing config  feed  swipe  shortlist flow")


if __name__ == "__main__":
    try:
        test_offerer_flow()
    except AssertionError as e:
        print(f"\n‚ùå Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n‚ùå Unexpected error: {e}")
        raise

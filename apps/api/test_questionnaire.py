"""
Integration test for questionnaire and scoring endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_questionnaire_flow():
    """Test the complete questionnaire and scoring flow"""
    print("\n" + "=" * 60)
    print("EPIC 4 - Questionnaire + Scoring Integration Test")
    print("=" * 60)
    
    # 1. Register a seeker
    print("\n1. Registering seeker...")
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "seeker_test@example.com",
            "password": "password123",
            "role": "seeker"
        }
    )
    print(f"Status: {register_response.status_code}")
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get questionnaire
    print("\n2. Fetching questionnaire...")
    questionnaire_response = requests.get(
        f"{BASE_URL}/questionnaire",
        headers=headers
    )
    print(f"Status: {questionnaire_response.status_code}")
    questionnaire = questionnaire_response.json()
    print(f"Questionnaire: {questionnaire['title']}")
    print(f"Total questions: {len(questionnaire['questions'])}")
    
    # 3. Submit answers (first batch)
    print("\n3. Submitting first batch of answers...")
    questions = questionnaire["questions"]
    first_batch = [
        {"question_id": questions[0]["id"], "value": 4},
        {"question_id": questions[1]["id"], "value": 5},
        {"question_id": questions[2]["id"], "value": 3},
    ]
    
    submit_response = requests.post(
        f"{BASE_URL}/questionnaire/answers",
        headers=headers,
        json={"answers": first_batch}
    )
    print(f"Status: {submit_response.status_code}")
    print(f"Response: {json.dumps(submit_response.json(), indent=2)}")
    
    # 4. Submit more answers (autosave test)
    print("\n4. Submitting more answers (testing autosave)...")
    second_batch = [
        {"question_id": questions[3]["id"], "value": 5},
        {"question_id": questions[4]["id"], "value": 4},
        {"question_id": questions[5]["id"], "value": 5},
    ]
    
    submit_response2 = requests.post(
        f"{BASE_URL}/questionnaire/answers",
        headers=headers,
        json={"answers": second_batch}
    )
    print(f"Status: {submit_response2.status_code}")
    print(f"Response: {json.dumps(submit_response2.json(), indent=2)}")
    
    # 5. Complete all remaining questions
    print("\n5. Completing remaining questions...")
    remaining_questions = questions[6:]
    remaining_answers = [
        {"question_id": q["id"], "value": 4} for q in remaining_questions
    ]
    
    submit_response3 = requests.post(
        f"{BASE_URL}/questionnaire/answers",
        headers=headers,
        json={"answers": remaining_answers}
    )
    print(f"Status: {submit_response3.status_code}")
    completion_data = submit_response3.json()
    print(f"Response: {json.dumps(completion_data, indent=2)}")
    
    # 6. Get computed stats
    print("\n6. Getting computed stats...")
    stats_response = requests.get(
        f"{BASE_URL}/seeker/stats",
        headers=headers,
        params={"include_fit_scores": "true"}
    )
    print(f"Status: {stats_response.status_code}")
    stats = stats_response.json()
    print(f"\nAttribute Stats:")
    for attr, score in stats["stats"].items():
        print(f"  {attr}: {score}")
    
    if stats.get("fit_scores"):
        print(f"\nFit Scores by Role:")
        for role, score in stats["fit_scores"].items():
            print(f"  {role}: {score}")
    
    # 7. Test answer update (autosave)
    print("\n7. Testing answer update (autosave)...")
    update_answer = [
        {"question_id": questions[0]["id"], "value": 5}  # Update first answer
    ]
    
    update_response = requests.post(
        f"{BASE_URL}/questionnaire/answers",
        headers=headers,
        json={"answers": update_answer}
    )
    print(f"Status: {update_response.status_code}")
    print(f"Response: {json.dumps(update_response.json(), indent=2)}")
    
    # 8. Get updated stats
    print("\n8. Getting updated stats...")
    updated_stats_response = requests.get(
        f"{BASE_URL}/seeker/stats",
        headers=headers
    )
    print(f"Status: {updated_stats_response.status_code}")
    updated_stats = updated_stats_response.json()
    print(f"\nUpdated Stats:")
    for attr, score in updated_stats["stats"].items():
        print(f"  {attr}: {score}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_questionnaire_flow()

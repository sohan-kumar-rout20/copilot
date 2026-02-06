"""Test cases for the FastAPI application endpoints"""

import sys
from pathlib import Path
import pytest

# Ensure src is on path so we can import the app module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Develop tennis skills and compete in matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu", "ryan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and visual arts techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["maya@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in school concerts",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["james@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM concepts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["nina@mergington.edu", "david@mergington.edu"]
        }
    }
    
    yield
    
    # Restore initial state
    activities.clear()
    activities.update(initial_state)


# Tests for GET /activities
class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_participants_list_is_present(self, client, reset_activities):
        """Test that participants list is returned"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert isinstance(chess_club["participants"], list)
        assert "michael@mergington.edu" in chess_club["participants"]


# Tests for POST /activities/{activity_name}/signup
class TestSignUpActivity:
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newemail@mergington.edu",
            method="POST"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        activities_data = client.get("/activities").json()
        assert "newemail@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_non_existent_activity(self, client, reset_activities):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/Non Existent Activity/signup?email=test@mergington.edu",
            method="POST"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu",
            method="POST"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        email = "newstudent@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}",
            method="POST"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}",
            method="POST"
        )
        assert response2.status_code == 200
        
        # Verify both signups worked
        activities_data = client.get("/activities").json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


# Tests for DELETE /activities/{activity_name}/unregister
class TestUnregisterActivity:
    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_data = client.get("/activities").json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_non_existent_activity(self, client, reset_activities):
        """Test unregister from activity that doesn't exist"""
        response = client.delete(
            "/activities/Non Existent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test unregister for a student not registered in the activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_reduces_participant_count(self, client, reset_activities):
        """Test that unregistering reduces the participant count"""
        # Get initial count
        activities_data = client.get("/activities").json()
        initial_count = len(activities_data["Programming Class"]["participants"])
        
        # Unregister a participant
        response = client.delete(
            "/activities/Programming Class/unregister?email=emma@mergington.edu"
        )
        assert response.status_code == 200
        
        # Check new count
        activities_data = client.get("/activities").json()
        new_count = len(activities_data["Programming Class"]["participants"])
        assert new_count == initial_count - 1


# Integration tests
class TestIntegration:
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test the complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity = "Tennis Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}",
            method="POST"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_data = client.get("/activities").json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_data = client.get("/activities").json()
        assert email not in activities_data[activity]["participants"]
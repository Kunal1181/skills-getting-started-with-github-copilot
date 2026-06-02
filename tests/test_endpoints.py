"""Integration tests for the FastAPI activities management application using AAA pattern"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client: TestClient):
        """Test that GET / redirects to /static/index.html"""
        # Arrange: No setup needed
        # Act: Make request to root endpoint
        response = client.get("/", follow_redirects=False)
        # Assert: Verify redirect response
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_dict(self, client: TestClient):
        """Test that GET /activities returns all activities as a dict"""
        # Arrange: Activities are pre-populated in conftest reset_activities
        # Act: Request all activities
        response = client.get("/activities")
        # Assert: Verify response status and content
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 3
        assert "Test Activity 1" in data
        assert "Test Activity 2" in data
        assert "Full Activity" in data

    def test_get_activities_returns_correct_structure(self, client: TestClient):
        """Test that each activity has the correct schema"""
        # Arrange: Activities pre-loaded
        # Act: Get activities
        response = client.get("/activities")
        # Assert: Verify each activity has required fields
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_includes_participants(self, client: TestClient):
        """Test that activities include current participants"""
        # Arrange: Activities with participants set in conftest
        # Act: Get activities
        response = client.get("/activities")
        # Assert: Verify participants are included
        data = response.json()
        assert data["Test Activity 2"]["participants"] == ["existing@test.com"]
        assert data["Full Activity"]["participants"] == ["full@test.com"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_adds_participant(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test successful signup adds student to activity"""
        # Arrange: Use available activity and new student email
        activity_name = sample_activities["available"]
        email = test_emails["student1"]
        
        # Act: Signup for activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify success response and participant added
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added to activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test that duplicate signup returns 400 Bad Request"""
        # Arrange: Activity already has a participant
        activity_name = sample_activities["with_participant"]
        email = test_emails["existing"]
        
        # Act: Try to signup with already-registered email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 400 error
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test that signup to nonexistent activity returns 404"""
        # Arrange: Use nonexistent activity name
        activity_name = sample_activities["nonexistent"]
        email = test_emails["student1"]
        
        # Act: Try to signup for activity that doesn't exist
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_at_capacity_returns_400(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test that signup to full activity returns 400"""
        # Arrange: Use activity at max capacity
        activity_name = sample_activities["full"]
        email = test_emails["student2"]
        
        # Act: Try to signup for activity at capacity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 400 error due to capacity
        assert response.status_code == 400
        data = response.json()
        assert "capacity" in data["detail"]

    def test_signup_missing_email_returns_422(self, client: TestClient, sample_activities: dict):
        """Test that signup without email parameter returns 422"""
        # Arrange: Prepare request without email parameter
        activity_name = sample_activities["available"]
        
        # Act: Make signup request without email
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert: Verify 422 validation error
        assert response.status_code == 422

    def test_signup_multiple_students_to_same_activity(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test that multiple different students can signup to same activity"""
        # Arrange: Activity with capacity for 2 students
        activity_name = sample_activities["available"]
        email1 = test_emails["student1"]
        email2 = test_emails["student2"]
        
        # Act: First student signups
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        # Second student signups
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        
        # Assert: Both signups succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both participants are in activity
        activities_response = client.get("/activities")
        activity_data = activities_response.json()[activity_name]
        assert email1 in activity_data["participants"]
        assert email2 in activity_data["participants"]
        assert len(activity_data["participants"]) == 2


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_success(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test successful removal of participant from activity"""
        # Arrange: Activity has a participant to remove
        activity_name = sample_activities["with_participant"]
        email = test_emails["existing"]
        
        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify success response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Removed {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activity_data = activities_response.json()[activity_name]
        assert email not in activity_data["participants"]

    def test_remove_from_nonexistent_activity_returns_404(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test that removing from nonexistent activity returns 404"""
        # Arrange: Use nonexistent activity
        activity_name = sample_activities["nonexistent"]
        email = test_emails["student1"]
        
        # Act: Try to remove from nonexistent activity
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_remove_nonexistent_participant_returns_400(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test that removing non-participant returns 400"""
        # Arrange: Activity exists but email is not a participant
        activity_name = sample_activities["available"]
        email = test_emails["student1"]
        
        # Act: Try to remove student who never signed up
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert: Verify 400 error
        assert response.status_code == 400
        data = response.json()
        assert "not found" in data["detail"]

    def test_remove_missing_email_returns_422(self, client: TestClient, sample_activities: dict):
        """Test that remove without email parameter returns 422"""
        # Arrange: Prepare request without email parameter
        activity_name = sample_activities["with_participant"]
        
        # Act: Make delete request without email
        response = client.delete(f"/activities/{activity_name}/participants")
        
        # Assert: Verify 422 validation error
        assert response.status_code == 422

    def test_remove_then_readd_same_participant(self, client: TestClient, sample_activities: dict, test_emails: dict):
        """Test that a participant can be removed and re-added to same activity"""
        # Arrange: Activity with participant
        activity_name = sample_activities["with_participant"]
        email = test_emails["existing"]
        
        # Act: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        # Then re-add the same participant
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Both operations succeed
        assert remove_response.status_code == 200
        assert signup_response.status_code == 200
        
        # Verify participant is back in activity
        activities_response = client.get("/activities")
        activity_data = activities_response.json()[activity_name]
        assert email in activity_data["participants"]

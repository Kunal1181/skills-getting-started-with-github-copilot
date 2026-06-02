"""Pytest configuration and fixtures for the FastAPI test suite"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean test state before each test"""
    # Arrange: Clear all participants and set up test data
    activities.clear()
    activities.update({
        "Test Activity 1": {
            "description": "Test activity for signup",
            "schedule": "Monday, 3:00 PM",
            "max_participants": 2,
            "participants": []
        },
        "Test Activity 2": {
            "description": "Another test activity",
            "schedule": "Tuesday, 4:00 PM",
            "max_participants": 3,
            "participants": ["existing@test.com"]
        },
        "Full Activity": {
            "description": "Activity at max capacity",
            "schedule": "Wednesday, 2:00 PM",
            "max_participants": 1,
            "participants": ["full@test.com"]
        }
    })
    yield
    # Cleanup after test
    activities.clear()


@pytest.fixture
def client():
    """Provide a TestClient instance for making test API calls"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provide easy access to test activity names and test data"""
    return {
        "available": "Test Activity 1",
        "with_participant": "Test Activity 2",
        "full": "Full Activity",
        "nonexistent": "Nonexistent Activity"
    }


@pytest.fixture
def test_emails():
    """Provide test email addresses for consistent test data"""
    return {
        "student1": "student1@test.com",
        "student2": "student2@test.com",
        "student3": "student3@test.com",
        "existing": "existing@test.com",
        "full_participant": "full@test.com"
    }

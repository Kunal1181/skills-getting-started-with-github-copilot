"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
import os
from pathlib import Path


# Pydantic models for request/response validation
class ActivityDetail(BaseModel):
    """Model representing a single activity with all details"""
    description: str
    schedule: str
    max_participants: int
    participants: list[str]


class Activity(BaseModel):
    """Model for complete activity information"""
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: list[str]


class SignupResponse(BaseModel):
    """Response model for signup operations"""
    message: str


class RemoveResponse(BaseModel):
    """Response model for participant removal"""
    message: str

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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
    "Soccer Team": {
        "description": "Join the school soccer team for practice and matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Practice swimming techniques and compete in meets",
        "schedule": "Wednesdays and Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["noah@mergington.edu", "mia@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media art projects",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Work on acting, stagecraft, and performance pieces",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["amelia@mergington.edu", "ethan@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argument skills in competitions",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["oliver@mergington.edu", "charlotte@mergington.edu"]
    },
    "Science Club": {
        "description": "Investigate experiments and explore scientific concepts",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["jack@mergington.edu", "sophia@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities() -> dict[str, ActivityDetail]:
    """Get all available activities with their details"""
    return activities


@app.post("/activities/{activity_name}/signup", response_model=SignupResponse)
def signup_for_activity(activity_name: str, email: str) -> SignupResponse:
    """Sign up a student for an activity"""
    # Arrange: Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

    # Check if activity is at capacity
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is at maximum capacity")

    # Act: Add student
    activity["participants"].append(email)
    # Assert: Return confirmation
    return SignupResponse(message=f"Signed up {email} for {activity_name}")


@app.delete("/activities/{activity_name}/participants", response_model=RemoveResponse)
def remove_participant(activity_name: str, email: str) -> RemoveResponse:
    """Remove a student from an activity"""
    # Arrange: Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    # Validate participant exists in activity
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Participant not found in this activity")

    # Act: Remove student
    activity["participants"].remove(email)
    # Assert: Return confirmation
    return RemoveResponse(message=f"Removed {email} from {activity_name}")

"""Tests for the POST /activities/{activity_name}/signup endpoint"""

import pytest


def test_signup_success(client):
    """Test successful signup for an activity"""
    response = client.post("/activities/Tennis%20Club/signup?email=test@mergington.edu")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Tennis Club" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "test@mergington.edu" in activities["Tennis Club"]["participants"]


def test_signup_activity_not_found(client):
    """Test signup fails when activity doesn't exist"""
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client):
    """Test signup fails when student is already registered"""
    # michael@mergington.edu is already in Chess Club
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_multiple_students_same_activity(client):
    """Test multiple students can sign up for the same activity"""
    # Sign up first student
    response1 = client.post("/activities/Tennis%20Club/signup?email=student1@mergington.edu")
    assert response1.status_code == 200
    
    # Sign up second student
    response2 = client.post("/activities/Tennis%20Club/signup?email=student2@mergington.edu")
    assert response2.status_code == 200
    
    # Verify both are in participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    participants = activities["Tennis Club"]["participants"]
    assert "student1@mergington.edu" in participants
    assert "student2@mergington.edu" in participants
    assert len(participants) == 2


def test_signup_same_student_different_activities(client):
    """Test a student can sign up for multiple activities"""
    email = "multisport@mergington.edu"
    
    # Sign up for Tennis Club
    response1 = client.post(f"/activities/Tennis%20Club/signup?email={email}")
    assert response1.status_code == 200
    
    # Sign up for Basketball Team
    response2 = client.post(f"/activities/Basketball%20Team/signup?email={email}")
    assert response2.status_code == 200
    
    # Verify student is in both activities
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities["Tennis Club"]["participants"]
    assert email in activities["Basketball Team"]["participants"]


def test_signup_participant_count_increases(client):
    """Test that participant count increases after signup"""
    activities_before = client.get("/activities").json()
    initial_count = len(activities_before["Tennis Club"]["participants"])
    
    # Sign up new participant
    client.post("/activities/Tennis%20Club/signup?email=newstudent@mergington.edu")
    
    activities_after = client.get("/activities").json()
    final_count = len(activities_after["Tennis Club"]["participants"])
    
    assert final_count == initial_count + 1


def test_signup_different_activity_names(client):
    """Test signup works for activities with spaces in names"""
    # Test with "Programming Class" (has space) - should succeed as capacity allows
    response = client.post("/activities/Programming%20Class/signup?email=newprog@mergington.edu")
    assert response.status_code == 200
    
    # Test with "Basketball Team"
    response = client.post("/activities/Basketball%20Team/signup?email=newbasket@mergington.edu")
    assert response.status_code == 200
    
    activities = client.get("/activities").json()
    assert "newprog@mergington.edu" in activities["Programming Class"]["participants"]
    assert "newbasket@mergington.edu" in activities["Basketball Team"]["participants"]


def test_signup_preserves_existing_participants(client):
    """Test that signup preserves existing participants"""
    activities_before = client.get("/activities").json()
    chess_participants_before = activities_before["Chess Club"]["participants"].copy()
    
    # Sign up for a different activity
    client.post("/activities/Tennis%20Club/signup?email=newstudent@mergington.edu")
    
    activities_after = client.get("/activities").json()
    chess_participants_after = activities_after["Chess Club"]["participants"]
    
    # Verify Chess Club participants are unchanged
    assert chess_participants_before == chess_participants_after

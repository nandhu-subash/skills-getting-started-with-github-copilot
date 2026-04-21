"""Tests for the GET /activities endpoint"""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activity data"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Verify we have all 9 activities
    assert len(activities) == 9
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    assert "Tennis Club" in activities
    assert "Basketball Team" in activities
    assert "Drama Club" in activities
    assert "Art Studio" in activities
    assert "Science Club" in activities
    assert "Debate Team" in activities


def test_get_activities_returns_correct_structure(client):
    """Test that each activity has the required fields"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Verify types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_participant_counts(client):
    """Test that participant counts are accurate"""
    response = client.get("/activities")
    activities = response.json()
    
    # Verify initial participant counts
    assert len(activities["Chess Club"]["participants"]) == 2
    assert len(activities["Programming Class"]["participants"]) == 2
    assert len(activities["Gym Class"]["participants"]) == 2
    assert len(activities["Tennis Club"]["participants"]) == 0
    assert len(activities["Basketball Team"]["participants"]) == 0
    assert len(activities["Drama Club"]["participants"]) == 0
    assert len(activities["Art Studio"]["participants"]) == 0
    assert len(activities["Science Club"]["participants"]) == 0
    assert len(activities["Debate Team"]["participants"]) == 0


def test_get_activities_participant_emails(client):
    """Test that participant emails are stored correctly"""
    response = client.get("/activities")
    activities = response.json()
    
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
    assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
    assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]
    assert "john@mergington.edu" in activities["Gym Class"]["participants"]
    assert "olivia@mergington.edu" in activities["Gym Class"]["participants"]

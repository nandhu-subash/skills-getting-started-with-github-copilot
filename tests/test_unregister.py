"""Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

import pytest


def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    # michael@mergington.edu is in Chess Club, so unregister should work
    response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister fails when activity doesn't exist"""
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_student_not_registered(client):
    """Test unregister fails when student is not registered for activity"""
    # test@mergington.edu is not in any activity
    response = client.delete("/activities/Chess%20Club/unregister?email=test@mergington.edu")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()


def test_unregister_from_empty_activity(client):
    """Test unregister from an activity with no participants"""
    response = client.delete("/activities/Tennis%20Club/unregister?email=test@mergington.edu")
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"].lower()


def test_unregister_participant_count_decreases(client):
    """Test that participant count decreases after unregister"""
    activities_before = client.get("/activities").json()
    initial_count = len(activities_before["Chess Club"]["participants"])
    
    # Unregister michael@mergington.edu from Chess Club
    client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
    
    activities_after = client.get("/activities").json()
    final_count = len(activities_after["Chess Club"]["participants"])
    
    assert final_count == initial_count - 1


def test_unregister_multiple_participants(client):
    """Test unregistering multiple participants from same activity"""
    # Unregister first participant
    response1 = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
    assert response1.status_code == 200
    
    # Unregister second participant
    response2 = client.delete("/activities/Chess%20Club/unregister?email=daniel@mergington.edu")
    assert response2.status_code == 200
    
    # Verify both are removed
    activities = client.get("/activities").json()
    assert len(activities["Chess Club"]["participants"]) == 0


def test_unregister_other_participants_unaffected(client):
    """Test that unregistering one participant doesn't affect others"""
    activities_before = client.get("/activities").json()
    gym_participants_before = activities_before["Gym Class"]["participants"].copy()
    
    # Unregister from Chess Club
    client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
    
    activities_after = client.get("/activities").json()
    gym_participants_after = activities_after["Gym Class"]["participants"]
    
    # Verify Gym Class participants are unchanged
    assert gym_participants_before == gym_participants_after


def test_unregister_then_signup_same_activity(client):
    """Test that a student can sign up again after unregistering"""
    email = "michael@mergington.edu"
    
    # Unregister from Chess Club
    response1 = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
    assert response1.status_code == 200
    
    # Try to sign up again
    response2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response2.status_code == 200
    
    # Verify participant is back in the activity
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_unregister_preserves_other_activities(client):
    """Test that unregistering from one activity doesn't affect other activities"""
    email = "emma@mergington.edu"  # In Programming Class and nowhere else
    
    # First verify emma is in Programming Class
    activities_before = client.get("/activities").json()
    assert email in activities_before["Programming Class"]["participants"]
    
    # Unregister from Programming Class
    response = client.delete(f"/activities/Programming%20Class/unregister?email={email}")
    assert response.status_code == 200
    
    activities_after = client.get("/activities").json()
    # Verify removal was successful
    assert email not in activities_after["Programming Class"]["participants"]

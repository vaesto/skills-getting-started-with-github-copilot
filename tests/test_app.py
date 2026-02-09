import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import activities


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert data["Basketball Team"]["description"] == "Competitive basketball practice and games"


def test_get_activities_structure(client):
    """Test that activities have required fields"""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]


def test_signup_for_activity_not_found(client):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/NonExistent%20Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_student(client):
    """Test that a student cannot sign up twice for the same activity"""
    # First signup should succeed
    response1 = client.post(
        "/activities/Basketball%20Team/signup?email=duplicate@mergington.edu"
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        "/activities/Basketball%20Team/signup?email=duplicate@mergington.edu"
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    # First signup
    client.post("/activities/Tennis%20Club/signup?email=unregister@mergington.edu")
    
    # Then unregister
    response = client.delete(
        "/activities/Tennis%20Club/signup?email=unregister@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]


def test_unregister_not_registered(client):
    """Test unregistering a student who is not registered"""
    response = client.delete(
        "/activities/Drama%20Club/signup?email=notregistered@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_activity_not_found(client):
    """Test unregistering from non-existent activity"""
    response = client.delete(
        "/activities/NonExistent/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_participants_list_updates(client):
    """Test that participants list updates after signup"""
    # Get initial participant count
    response1 = client.get("/activities")
    initial_count = len(response1.json()["Art Studio"]["participants"])
    
    # Sign up a new participant
    client.post("/activities/Art%20Studio/signup?email=newart@mergington.edu")
    
    # Check participant count increased
    response2 = client.get("/activities")
    new_count = len(response2.json()["Art Studio"]["participants"])
    
    assert new_count == initial_count + 1
    assert "newart@mergington.edu" in response2.json()["Art Studio"]["participants"]


def test_participants_list_updates_on_unregister(client):
    """Test that participants list updates after unregistration"""
    # Sign up first
    client.post("/activities/Robotics%20Club/signup?email=robot@mergington.edu")
    
    # Get participant count
    response1 = client.get("/activities")
    count_with_signup = len(response1.json()["Robotics Club"]["participants"])
    
    # Unregister
    client.delete("/activities/Robotics%20Club/signup?email=robot@mergington.edu")
    
    # Check participant count decreased
    response2 = client.get("/activities")
    count_after_unregister = len(response2.json()["Robotics Club"]["participants"])
    
    assert count_after_unregister == count_with_signup - 1
    assert "robot@mergington.edu" not in response2.json()["Robotics Club"]["participants"]

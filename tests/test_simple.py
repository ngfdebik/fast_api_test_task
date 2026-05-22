import pytest
from fastapi import status

def test_create_department_direct(client):
    response = client.post(
        "/departments/",
        json={"name": "Direct Test", "parent_id": None}
    )
    print(f"\nStatus: {response.status_code}")
    print(f"Response body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Direct Test"
    assert "id" in data

def test_create_department_with_parent(client):
    parent_response = client.post(
        "/departments/",
        json={"name": "Parent Dept", "parent_id": None}
    )
    assert parent_response.status_code == 200
    parent_id = parent_response.json()["id"]
    
    child_response = client.post(
        "/departments/",
        json={"name": "Child Dept", "parent_id": parent_id}
    )
    assert child_response.status_code == 200
    data = child_response.json()
    assert data["name"] == "Child Dept"
    assert data["parent_id"] == parent_id

def test_get_department_with_new_structure(client):
    create_response = client.post(
        "/departments/",
        json={"name": "Structure Test", "parent_id": None}
    )
    dept_id = create_response.json()["id"]
    
    response = client.get(f"/departments/{dept_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "department" in data
    assert data["department"]["name"] == "Structure Test"
    assert "children" in data
    assert "employees" in data
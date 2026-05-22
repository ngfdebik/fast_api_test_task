import pytest
from fastapi import status

class TestCreateDepartmentFixed:
    
    def test_create_department_success(self, client):
        response = client.post(
            "/departments/",
            json={"name": "New Department", "parent_id": None}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Department"
        assert data["parent_id"] is None
        assert "id" in data
    
    def test_create_department_with_parent_success(self, client):
        parent_response = client.post(
            "/departments/",
            json={"name": "Parent Department", "parent_id": None}
        )
        assert parent_response.status_code == 200
        parent_id = parent_response.json()["id"]
        
        response = client.post(
            "/departments/",
            json={"name": "Child Department", "parent_id": parent_id}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Child Department"
        assert data["parent_id"] == parent_id
    
    def test_create_department_parent_not_found(self, client):
        response = client.post(
            "/departments/",
            json={"name": "Department", "parent_id": 99999}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestGetDepartmentFixed:
    
    def test_get_department_success(self, client):
        create_response = client.post(
            "/departments/",
            json={"name": "Test Department", "parent_id": None}
        )
        assert create_response.status_code == 200
        dept_id = create_response.json()["id"]
        
        response = client.get(f"/departments/{dept_id}?depth=1&include_employees=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "department" in data
        assert data["department"]["id"] == dept_id
        assert data["department"]["name"] == "Test Department"
        assert "children" in data
        assert "employees" in data
    
    def test_get_department_not_found(self, client):
        response = client.get("/departments/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestDeleteDepartmentFixed:
    
    def test_delete_department_cascade_success(self, client):
        create_response = client.post(
            "/departments/",
            json={"name": "To Delete", "parent_id": None}
        )
        assert create_response.status_code == 200
        dept_id = create_response.json()["id"]
        
        response = client.delete(f"/departments/{dept_id}?mode=cascade")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        get_response = client.get(f"/departments/{dept_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
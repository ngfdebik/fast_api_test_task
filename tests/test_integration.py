class TestIntegration:
    
    def test_full_department_hierarchy_flow(self, client):
        
        root_response = client.post(
            "/departments/",
            json={"name": "Root Department", "parent_id": None}
        )
        assert root_response.status_code == 200
        root_id = root_response.json()["id"]
        
        child_response = client.post(
            "/departments/",
            json={"name": "Child Department", "parent_id": root_id}
        )
        assert child_response.status_code == 200
        child_id = child_response.json()["id"]
        
        get_response = client.get(f"/departments/{root_id}?depth=2&include_employees=true")
        assert get_response.status_code == 200
        data = get_response.json()
        
        assert "department" in data
        assert data["department"]["name"] == "Root Department"
        assert data["department"]["id"] == root_id
        
        assert "children" in data
        assert len(data["children"]) == 1
        
        child_data = data["children"][0]
        assert "department" in child_data
        assert child_data["department"]["name"] == "Child Department"
        assert child_data["department"]["parent_id"] == root_id
    
    def test_get_department_with_depth(self, client):
        
        dept1 = client.post("/departments/", json={"name": "Level 1", "parent_id": None})
        dept1_id = dept1.json()["id"]
        
        dept2 = client.post("/departments/", json={"name": "Level 2", "parent_id": dept1_id})
        dept2_id = dept2.json()["id"]
        
        dept3 = client.post("/departments/", json={"name": "Level 3", "parent_id": dept2_id})
        
        response = client.get(f"/departments/{dept1_id}?depth=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["children"]) == 1
        assert data["children"][0]["children"] == []
        
        response = client.get(f"/departments/{dept1_id}?depth=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["children"]) == 1
        assert len(data["children"][0]["children"]) == 1
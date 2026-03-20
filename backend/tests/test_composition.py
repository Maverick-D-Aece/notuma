from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_page_layout():
    response = client.get("/api/v1/composition/page/test-page")
    assert response.status_code == 200
    assert response.json()["pageId"] == "test-page"

def test_save_page_layout():
    response = client.post(
        "/api/v1/composition/page/save",
        json={"pageId": "test-page", "layout": {"version": "5.3.0", "objects": []}}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_render_page():
    response = client.post(
        "/api/v1/composition/page/render",
        json={"pageId": "test-page"}
    )
    assert response.status_code == 200
    assert "taskId" in response.json()

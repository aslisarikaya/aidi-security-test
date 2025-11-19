from src.server import app


def test_index_route():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "bitcoin" in data
    assert "usd" in data["bitcoin"]
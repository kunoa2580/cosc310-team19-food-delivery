def test_get_restaurants_list(client):
    
    response = client.get("/restaurants")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 3
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Green Bowl Cafe"
    assert data[1]["id"] == 2
    assert data[2]["id"] == 3

def test_get_restaurants_empty(client, tmp_path):
    (tmp_path / "restaurants.json").write_text(
        "[]", encoding="utf-8"
    )
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert response.json() == []

def test_get_restaurants_by_id(client):
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    response = response.json()
    assert response["id"] == 1

def test_get_by_cuisine(client):
    response = client.get("/restaurants/filtered-by-Italian-type")
    assert response.status_code == 200
    response = response.json()
    assert response == [{
    "id": 2,
    "name": "Cedar & Co.",
    "address": "45 Oak Avenue, Burnaby, BC",
    "phone_number": "604-555-0102",
    "email": "contact@cedarco.ca",
    "website": "https://cedarco.ca",
    "cuisine_type": "Italian",
    "opening_hours": "Tue-Sun: 11:30 AM - 10:00 PM",
    "rating": 4.5,
    "availability": True
  }]

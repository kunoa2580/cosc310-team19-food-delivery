def test_create_restaurant_good(client):
    response = client.post(
        "/restaurants",
        json={
            "name": "Test Restaurant",
            "address": "123 Test Street",
            "phone_number": "250-555-0100",
            "email": "test@example.com",
            "website": "https://example.com",
            "cuisine_type": "Italian",
            "opening_hours": "11:00-21:00",
            "rating": 4.5,
            "availability": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 4
    assert data["name"] == "Test Restaurant"
    saved = client.get("/restaurants/4")
    assert saved.status_code == 200
    assert saved.json() == data


def test_create_restaurant_conflict(client):
    before = client.get("/restaurants").json()
    response = client.post(
        "/restaurants",
        json={
            "name": "Green Bowl Cafe",
            "address": "123 Test Street",
            "phone_number": "250-555-0100",
            "email": "test@example.com",
            "website": "https://example.com",
            "cuisine_type": "Italian",
            "opening_hours": "11:00-21:00",
            "rating": 4.5,
            "availability": True
        }
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "A restaurant with the name Green Bowl Cafe already exists"
    }
    after = client.get("/restaurants").json()
    assert after == before


def test_create_restaurant_invalid(client):
    before = client.get("/restaurants").json()
    response = client.post("/restaurants", json={"name": "Incomplete Restaurant"})
    assert response.status_code == 422
    after = client.get("/restaurants").json()
    assert after == before


def test_update_restaurant_good(client):
    changes = {
        "name": "Updated Restaurant",
        "address": "456 New Street",
        "phone_number": "250-555-0199",
        "email": "new@example.com",
        "website": "https://new.example.com",
        "cuisine_type": "Chinese",
        "opening_hours": "12:00-22:00",
        "rating": 0.0,
        "availability": False
    }
    response = client.patch("/restaurants/1", json=changes)
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == changes["address"]
    assert data["opening_hours"] == changes["opening_hours"]
    assert data["availability"] == False
    saved = client.get("/restaurants/1")
    assert saved.status_code == 200
    assert saved.json() == data


def test_update_restaurant_one_field(client):
    before = client.get("/restaurants/1").json()
    response = client.patch("/restaurants/1", json={"address": "456 New Street"})
    assert response.status_code == 200
    expected = before
    expected["address"] = "456 New Street"
    assert response.json() == expected
    saved = client.get("/restaurants/1")
    assert saved.json() == expected


def test_update_restaurant_same_name(client):
    before = client.get("/restaurants/1").json()
    response = client.patch("/restaurants/1", json={"name": "Green Bowl Cafe"})
    assert response.status_code == 200
    assert response.json() == before


def test_update_restaurant_empty(client):
    before = client.get("/restaurants/1").json()
    response = client.patch("/restaurants/1", json={})
    assert response.status_code == 200
    assert response.json() == before


def test_update_restaurant_conflict(client):
    before = client.get("/restaurants").json()
    response = client.patch(
        "/restaurants/1",
        json={"name": "Cedar & Co.", "address": "Should Not Be Saved"}
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "A restaurant with the name Cedar & Co. already exists"
    }
    after = client.get("/restaurants").json()
    assert after == before


def test_update_restaurant_not_found(client):
    before = client.get("/restaurants").json()
    response = client.patch("/restaurants/999", json={"address": "456 New Street"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant with id 999 was not found."}
    after = client.get("/restaurants").json()
    assert after == before


def test_update_restaurant_invalid(client):
    before = client.get("/restaurants/1").json()
    response = client.patch("/restaurants/1", json={"rating": "not a number"})
    assert response.status_code == 422
    after = client.get("/restaurants/1").json()
    assert after == before


def test_update_restaurant_null(client):
    before = client.get("/restaurants/1").json()

    response = client.patch(
        "/restaurants/1",
        json={"address": None}
    )

    assert response.status_code == 200
    assert response.json() == before

    after = client.get("/restaurants/1").json()
    assert after == before
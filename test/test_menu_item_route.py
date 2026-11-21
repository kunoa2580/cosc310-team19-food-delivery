def test_menu_route_get_by_id_good(client):
    response = client.get("/restaurant/1/menu-items/1")
    data = response.json()
    assert data["name"] == "Iced Peach Green Tea Lemonade"
    assert data["restaurant_id"] == 1
    assert data["item_id"] == 1


def test_menu_route_get_by_id_bad(client):
    response = client.get("/restaurant/999/menu-items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "No menu item 999 on restaurant 999"

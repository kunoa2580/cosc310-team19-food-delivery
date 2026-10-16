import json
import pytest
from app.repositories.restaurant_repository import RestaurantRepository


@pytest.fixture
def repo(tmp_path):
    data = [
        {"id": 1, "name": "Restaurant A"},
        {"id": 2, "name": "Restaurant B"}
    ]

    file = tmp_path / "restaurants.json"
    file.write_text(json.dumps(data), encoding="utf-8")

    return RestaurantRepository(data_path=str(file))


def test_restaurant_repo_list(repo):
    restaurants = repo.restaurant_repo_list()

    assert len(restaurants) == 2
    assert restaurants[0]["name"] == "Restaurant A"


def test_restaurant_repo_get_by_id(repo):
    restaurant = repo.restaurant_repo_get_by_id(1)

    assert restaurant is not None
    assert restaurant["id"] == 1
    assert restaurant["name"] == "Restaurant A"


def test_restaurant_repo_get_by_id_not_found(repo):
    restaurant = repo.restaurant_repo_get_by_id(999)

    assert restaurant is None

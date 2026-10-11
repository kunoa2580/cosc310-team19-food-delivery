import json
import os
from pathlib import Path
class RestaurantRepository:
    def __init__(self, data_path: str | None = None):
        self.data_path = data_path

    def _get_data_path(self) -> Path:
        if self.data_path is not None:
            return Path(self.data_path)

        data_dir = Path(
            os.getenv("COSC310_DATA_DIR", "data")
        )
        return data_dir / "restaurants.json"

    def _load(self) -> list[dict]:
        data_path = self._get_data_path()
        if not data_path.exists():
            return []

        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, restaurants: list[dict]) -> None:
        data_path = self._get_data_path()

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(restaurants, f, indent=2)

    def restaurant_repo_list(self) -> list[dict]:
        return self._load()

    def restaurant_repo_get_by_id(self, restaurant_id: int) -> dict | None:
        for restaurant in self._load():
            if restaurant["id"] == restaurant_id:
                return restaurant
        return None

    def restaurant_repo_create(self, restaurant_data: dict) -> dict:
        restaurants = self._load()

        next_id = max(
            (restaurant["id"] for restaurant in restaurants),
            default=0
        ) + 1

        restaurant = {
            "id": next_id,
            **restaurant_data
        }

        restaurants.append(restaurant)
        self._save(restaurants)

        return restaurant

    def restaurant_repo_delete_by_id(self, restaurant_id: int) -> bool:
        restaurants = self._load()

        for restaurant in restaurants:
            if restaurant["id"] == restaurant_id:
                restaurants.remove(restaurant)
                self._save(restaurants)
                return True

        return False
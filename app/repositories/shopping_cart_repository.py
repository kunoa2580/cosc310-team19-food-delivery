import json
import os


class shopping_cart_repository:

    def __init__(self, data_path: str | None = None):
        self.data_path = data_path


    def _get_data_path(self) -> str:
        if self.data_path is not None:
            return self.data_path

        data_dir = os.getenv("COSC310_DATA_DIR", "data")

        return os.path.join(data_dir, "shopping_cart.json")


    def _load(self) -> list[dict]:
        data_path = self._get_data_path()
        if not os.path.exists(data_path):
            return []

        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, records: list[dict]) -> None:
        data_path = self._get_data_path()

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)


    def add_item_to_cart_service_repo():
        pass
    def remove_item_from_cart_service_repo():
        pass
    def clear_cart_service_repo ():
        pass
    def get_cart_items_service_repo():
        pass
    def total_cart_price_service_repo():
        pass

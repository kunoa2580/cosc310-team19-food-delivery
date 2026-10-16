from pathlib import Path
import json
import os


# @TheTureFADED
class MenuItemRepository:
    """This class is for loading and saving updated data back the json file (DATABASE)
    branch: feature/menu-item-schema

    """

    # @TheTureFADED
    def __init__(self, data_path: str | None = None):
        """Defined where is the data path
        branch: feature/menu-item-schema

        """
        self.data_path = data_path

    # @TheTureFADED
    def _get_data_path(self) -> Path:

        if self.data_path is not None:
            return Path(self.data_path)

        data_dir = Path(os.getenv("COSC310_DATA_DIR", "data"))

        return data_dir / "menu_items.json"

    # @TheTureFADED
    def _load(self) -> list[dict]:
        data_path = self._get_data_path()
        if not data_path.exists():
            return []

        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # @TheTureFADED
    def _save(self, records: list[dict]) -> None:
        data_path = self._get_data_path()

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    # @TheTureFADED
    def menu_repo_list(self, restaurant_id: int) -> list[dict]:
        menu_items = self._load()
        menu_ = []
        for mi in menu_items:
            if mi["restaurant_id"] == restaurant_id:
                menu_.append(mi)
        return menu_

    # @TheTureFADED
    def menu_repo_get_by_id(self, restaurant_id: int, item_id: int) -> dict | None:
        menu_items = self.menu_repo_list(restaurant_id)
        item = None
        for i in menu_items:
            if i["item_id"] == item_id:
                item = i
                return item
        return item

    # @TheTureFADED
    def menu_repo_create(self, record: dict, restaurant_id: int) -> dict:
        menu_items = self._load()
        next_id = max((i["item_id"] for i in menu_items), default=0) + 1
        record = {**record, "item_id": next_id, "restaurant_id": restaurant_id}
        menu_items.append(record)
        self._save(menu_items)
        return record

    # @TheTureFADED
    def menu_repo_update(self, restaurant_id: int, item_id: int, changes: dict) -> dict | None:
        menu_items = self._load()
        for mi in menu_items:
            if mi["restaurant_id"] == restaurant_id and mi["item_id"] == item_id:
                mi.update(changes)
                self._save(menu_items)
                return mi
        return None

    # @TheTureFADED
    def menu_repo_delete(self, restaurant_id: int, item_id: int) -> bool:
        menu_items = self._load()

        for mi in menu_items:
            if mi["item_id"] == item_id and mi["restaurant_id"] == restaurant_id:
                menu_items.remove(mi)
                self._save(menu_items)
                return True
        return False

from pathlib import Path
import json
import os


class OrderRepository:
    """Loads and saves orders in orders.json."""

    def __init__(self, data_path: str | None = None):
        self.data_path = data_path

    def _get_data_path(self) -> Path:
        if self.data_path is not None:
            return Path(self.data_path)

        data_dir = Path(os.getenv("COSC310_DATA_DIR", "data"))

        return data_dir / "orders.json"

    def _load(self) -> list[dict]:
        data_path = self._get_data_path()
        if not data_path.exists():
            return []

        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, records: list[dict]) -> None:
        data_path = self._get_data_path()

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def order_repo_create(self, record: dict) -> dict:
        orders = self._load()
        next_id = max((o["order_id"] for o in orders), default=0) + 1
        record = {**record, "order_id": next_id}
        orders.append(record)
        self._save(orders)
        return record

    def order_repo_get_by_id(self, order_id: int) -> dict | None:
        for order in self._load():
            if order["order_id"] == order_id:
                return order
        return None
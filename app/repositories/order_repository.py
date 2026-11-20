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

    # US1 Checkout: save a new order. The id is the current largest id + 1,
    # so ids stay unique and keep increasing after a restart.
    def order_repo_create(self, record: dict) -> dict:
        orders = self._load()
        next_id = max((o["order_id"] for o in orders), default=0) + 1
        record = {**record, "order_id": next_id}
        orders.append(record)
        self._save(orders)
        return record

    # US2 View one order: find an order by id, or None if it does not exist.
    def order_repo_get_by_id(self, order_id: int) -> dict | None:
        for order in self._load():
            if order["order_id"] == order_id:
                return order
        return None

    # US3 Order history: all orders of one customer, oldest first (empty list if none).
    def order_repo_list_by_customer(self, customer_id: int) -> list[dict]:
        return [o for o in self._load() if o["customer_id"] == customer_id]
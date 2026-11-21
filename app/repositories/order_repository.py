from app.repositories.json_store import JsonStore


class OrderRepository:
    """Loads and saves orders in orders.json."""

    def __init__(self, data_path: str | None = None):
        self._store = JsonStore("orders.json", data_path)

    # US1 Checkout: save a new order. The id is the current largest id + 1,
    # so ids stay unique and keep increasing after a restart.
    def order_repo_create(self, record: dict) -> dict:
        orders = self._store.load()
        next_id = max((o["order_id"] for o in orders), default=0) + 1
        record = {**record, "order_id": next_id}
        orders.append(record)
        self._store.save(orders)
        return record

    # US2 View one order: find an order by id, or None if it does not exist.
    def order_repo_get_by_id(self, order_id: int) -> dict | None:
        for order in self._store.load():
            if order["order_id"] == order_id:
                return order
        return None

    # US3 Order history: all orders of one customer, oldest first (empty list if none).
    def order_repo_list_by_customer(self, customer_id: int) -> list[dict]:
        return [o for o in self._load() if o["customer_id"] == customer_id]

    def order_repo_has_reference(
        self, restaurant_id: int, item_id: int | None = None
    ) -> bool:
        for order in self._load():
            if order["restaurant_id"] != restaurant_id:
                continue
            if item_id is None or any(
                line["item_id"] == item_id for line in order["items"]
            ):
                return True
        return False

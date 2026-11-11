import json
from pathlib import Path

from app.repositories.order_repository import OrderRepository

sample = {
    "customer_id": 1,
    "restaurant_id": 1,
    "items": [{"item_id": 2, "name": "Iced Peach Black Tea Lemonade", "unit_price": 4.99, "quantity": 2}],
    "total": 9.98,
    "status": "placed",
    "created_at": "2026-11-10T00:00:00+00:00",
}


def test_order_repo_create_assigns_first_id():
    repo = OrderRepository()
    created = repo.order_repo_create(sample)
    assert created["order_id"] == 1
    assert created["customer_id"] == 1
    assert created["items"] == sample["items"]


def test_order_repo_create_ids_increase():
    repo = OrderRepository()
    first = repo.order_repo_create(sample)
    second = repo.order_repo_create(sample)
    assert second["order_id"] == first["order_id"] + 1


def test_order_repo_get_by_id():
    repo = OrderRepository()
    created = repo.order_repo_create(sample)
    assert repo.order_repo_get_by_id(created["order_id"]) == created


def test_order_repo_get_by_id_not_found():
    repo = OrderRepository()
    assert repo.order_repo_get_by_id(999) is None


def test_order_repo_persists_across_instances():
    created = OrderRepository().order_repo_create(sample)
    restarted = OrderRepository()
    assert restarted.order_repo_get_by_id(created["order_id"]) == created
    assert restarted.order_repo_create(sample)["order_id"] == created["order_id"] + 1


def test_order_repo_uses_injected_path(tmp_path):
    path = tmp_path / "custom_orders.json"
    repo = OrderRepository(data_path=str(path))
    repo.order_repo_create(sample)
    assert len(json.loads(path.read_text())) == 1


def test_order_repo_does_not_touch_committed_data():
    committed_file = Path(__file__).resolve().parents[1] / "data" / "orders.json"
    before = committed_file.read_text()
    OrderRepository().order_repo_create(sample)
    assert committed_file.read_text() == before
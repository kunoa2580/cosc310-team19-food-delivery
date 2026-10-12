
import json
from pathlib import Path

# the data path of the json file
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "menu_items.json"


def menu_repo_read_json() -> list[dict]:# read json file
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def menu_repo_list(restaurant_id: int) -> list[dict]:# list all of the items
    items = menu_repo_read_json()

    result = []

    for item in items:
        if item["restaurant_id"] == restaurant_id:
            result.append(item)

    return result


def menu_repo_get_by_id(restaurant_id: int, item_id: int) -> dict | None:# get the item by item id
    items = menu_repo_list(restaurant_id)

    for item in items:
        if item["item_id"] == item_id:
            return item

    return None

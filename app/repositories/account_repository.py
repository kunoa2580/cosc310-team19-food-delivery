"""JSON accounts with atomic replacement and serialized single-process updates."""
import json
import os
from pathlib import Path
from threading import RLock

account_lock = RLock()


class AccountRepository:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path

    def data_path(self) -> Path:
        return self.path or Path(os.getenv("COSC310_DATA_DIR", "data")) / "accounts.json"

    def list_accounts(self) -> list[dict]:
        with account_lock:
            path = self.data_path()
            if not path.exists():
                return []
            with path.open(encoding="utf-8") as source:
                return json.load(source)

    def get(self, account_id: int) -> dict | None:
        return next((a for a in self.list_accounts() if a["id"] == account_id), None)

    def save(self, accounts: list[dict]) -> None:
        with account_lock:
            path = self.data_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".tmp")
            with temporary.open("w", encoding="utf-8") as target:
                json.dump(accounts, target, indent=2)
            temporary.replace(path)


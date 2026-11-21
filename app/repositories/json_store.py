import json
import os
from pathlib import Path


class JsonStore:
    """Reads and writes one JSON file that holds a list of records."""

    def __init__(self, filename: str, data_path: str | Path | None = None):
        self.filename = filename
        self.data_path = data_path

    def path(self) -> Path:
        if self.data_path is not None:
            return Path(self.data_path)
        return Path(os.getenv("COSC310_DATA_DIR", "data")) / self.filename

    def load(self) -> list[dict]:
        path = self.path()
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            # Regression fix: an empty file means no records yet (it used to crash with a 500).
            return []
        return json.loads(text)

    def save(self, records: list[dict]) -> None:
        path = self.path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
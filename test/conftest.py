import shutil
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app

FIXTURE_DATA = Path(__file__).with_name("fixtures")


@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    monkeypatch.setenv("COSC310_DATA_DIR", str(tmp_path))
    for name in ("restaurants.json", "menu_items.json"):
        shutil.copyfile(FIXTURE_DATA / name, tmp_path / name)


@pytest.fixture
def client():
    return TestClient(app)


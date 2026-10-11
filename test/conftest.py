import fastapi
import shutil
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app

REAL_DATA = Path(__file__).resolve().parents[1] / "data"

@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    for name in ("restaurants.json", ):
        shutil.copy(REAL_DATA / name, tmp_path / name)

    monkeypatch.setenv("COSC310_DATA_DIR", str(tmp_path))

@pytest.fixture
def client():
    return TestClient(app)


# Tests for JsonStore, the shared JSON-file helper used by the repositories.
# They cover: missing file returns an empty list, save/load round trip,
# creating the parent folder, and how the file path is chosen
from app.repositories.json_store import JsonStore


def test_load_returns_empty_list_when_file_is_missing(tmp_path):
    store = JsonStore("things.json", data_path=tmp_path / "things.json")
    assert store.load() == []


def test_save_then_load_round_trips_records(tmp_path):
    store = JsonStore("things.json", data_path=tmp_path / "things.json")
    store.save([{"id": 1, "name": "a"}, {"id": 2, "name": "b"}])
    assert store.load() == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


def test_save_creates_missing_parent_folder(tmp_path):
    store = JsonStore("things.json", data_path=tmp_path / "nested" / "things.json")
    store.save([{"id": 1}])
    assert store.load() == [{"id": 1}]


def test_path_uses_env_dir_and_filename_when_no_explicit_path(tmp_path, monkeypatch):
    monkeypatch.setenv("COSC310_DATA_DIR", str(tmp_path))
    assert JsonStore("things.json").path() == tmp_path / "things.json"


def test_explicit_path_wins_over_env_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("COSC310_DATA_DIR", str(tmp_path / "ignored"))
    explicit = tmp_path / "mine.json"
    assert JsonStore("things.json", data_path=str(explicit)).path() == explicit


def test_env_dir_is_read_on_every_call(tmp_path, monkeypatch):
    store = JsonStore("things.json")
    monkeypatch.setenv("COSC310_DATA_DIR", str(tmp_path / "a"))
    first = store.path()
    monkeypatch.setenv("COSC310_DATA_DIR", str(tmp_path / "b"))
    assert store.path() != first



# Regression: an empty (0-byte) data file used to raise JSONDecodeError,
# so order history and checkout returned 500. An empty file now means no records.
def test_load_returns_empty_list_when_file_is_empty(tmp_path):
    path = tmp_path / "things.json"
    path.write_text("", encoding="utf-8")
    assert JsonStore("things.json", data_path=path).load() == []
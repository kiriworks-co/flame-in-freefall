"""Regression for the observed competing-bootstrap temporary-file collision."""
import json
from concurrent.futures import ThreadPoolExecutor

from src.storage import _write_json


def test_independent_json_writers_publish_only_complete_records(tmp_path):
    path = tmp_path / "state.json"
    values = [{"writer": i, "payload": str(i) * 10000} for i in range(12)]
    with ThreadPoolExecutor(max_workers=4) as workers:
        list(workers.map(lambda value: _write_json(path, value), values))
    assert json.loads(path.read_text(encoding="utf8")) in values
    assert sorted(p.name for p in tmp_path.iterdir()) == ["state.json"]

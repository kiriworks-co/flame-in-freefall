"""Synthetic fixtures for compatibility rules; these are not NASA measurements."""
from src.comparison import compare_tables


def entry(study, kind="condition", method=None, conditions=None):
    return {"study_id": study, "table": {
        "name": "Synthetic test table", "columns": ["time (s)", "diameter (mm)"],
        "rows": [[0, 1], [1, .8]], "evidence_kind": kind,
        "methodology": method, "conditions": conditions}}


def test_conditions_cannot_be_pooled_as_measurements():
    result = compare_tables([entry("TEST-A"), entry("TEST-B")])
    assert not result["compatible"]
    assert len(result["profiles"]) == 2


def test_measurements_require_same_method_and_conditions():
    result = compare_tables([entry("TEST-A", "measurement", "video", {"pressure": "1 atm"}),
                             entry("TEST-B", "measurement", "video", {"pressure": "2 atm"})])
    assert not result["compatible"]
    result = compare_tables([entry("TEST-A", "measurement", "video", {"pressure": "1 atm"}),
                             entry("TEST-B", "measurement", "video", {"pressure": "1 atm"})])
    assert result["compatible"]

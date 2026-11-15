"""Synthetic fixtures exercise dimensional invariants, not NASA measurements."""
import pytest

from src.units import (
    field_definition,
    gauge_to_absolute,
    normalize_quantity,
    observations_from_tables,
    partial_oxygen_pressure,
)


def test_absolute_atmosphere_and_velocity():
    result = normalize_quantity(1, "atm", "pressure", "absolute")
    assert result["normalized_value"] == pytest.approx(14.6959488)
    assert result["normalized_unit"] == "psia"
    assert normalize_quantity(1, "m/s", "velocity")["normalized_value"] == 100


def test_pressure_reference_never_guessed():
    assert normalize_quantity(1, "psi", "pressure")["normalized_value"] is None
    assert normalize_quantity(760, "mmHg", "pressure")["status"] == "reference_required"
    assert normalize_quantity(3, "psig", "pressure")["normalized_unit"] == "psig"
    assert gauge_to_absolute(3, 14.7)["value"] == pytest.approx(17.7)


def test_partial_pressure_is_derived():
    result = partial_oxygen_pressure(.21, 14.7)
    assert result["value"] == pytest.approx(3.087)
    assert result["evidence_kind"] == "derived"
    with pytest.raises(ValueError):
        partial_oxygen_pressure(21, 14.7)


def test_temperature_oxygen_ranges_and_uncertainty():
    assert normalize_quantity(25, "C", "temperature")["normalized_value"] == pytest.approx(298.15)
    assert normalize_quantity(21, "%", "oxygen")["normalized_value"] == pytest.approx(.21)
    assert normalize_quantity("2-7", "mm", "diameter")["status"] == "range"
    assert normalize_quantity("2.3 ± 0.1", "mm", "diameter")["uncertainty"] == .1
    assert normalize_quantity("unknown", "mm", "diameter")["status"] == "qualitative"


def test_nasa_headers_and_dimensional_mismatch():
    assert field_definition("O initial ambient composition; mole fraction")[:2] == ("oxygen", "mole fraction")
    assert field_definition("Initial CO2 % by vol")[0] is None
    assert normalize_quantity(.5, "mm", "rate")["normalized_value"] is None
    table = {"columns": ["Visible flame extinction diameter; mm", "Oxygen Mole Fraction"],
             "rows": [[.89, .21]], "source_rows": [19]}
    result = observations_from_tables([table], "mixed_conditions_and_reported_results")
    assert result[0]["evidence_kind"] == "reported_result"
    assert result[0]["row_number"] == 19
    assert result[1]["evidence_kind"] == "condition"

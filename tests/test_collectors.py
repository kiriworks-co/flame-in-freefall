"""Collector regression checks use retained real metadata, with no network."""
import copy
import json
from pathlib import Path

from scripts.fetch_psi_tables import discover_csvs, discover_pdfs, get_signed_url, version_of
from src.retrieval import structural_chunks

ROOT = Path(__file__).resolve().parents[1]


def test_current_geode_names_and_restrictions():
    manifest = json.loads((ROOT / "data/psi_downloads/PSI-69/source_manifest.json").read_text(encoding="utf-8"))
    original = manifest["downloaded_csvs"][0]["original_metadata"]
    found = discover_csvs({"files": [original]})
    assert found[0]["name"] == manifest["downloaded_csvs"][0]["filename"]
    restricted = copy.deepcopy(original)
    restricted["restrictedAccess"] = True
    assert discover_csvs({"files": [restricted]}) == []
    hidden = copy.deepcopy(original)
    hidden["visible"] = False
    assert discover_csvs({"files": [hidden]}) == []
    pdf = copy.deepcopy(manifest["downloaded_pdfs"][0]["original_metadata"])
    assert discover_pdfs({"files": [pdf]})
    pdf["restrictedAccess"] = True
    assert discover_pdfs({"files": [pdf]}) == []


def test_real_metadata_version_and_signed_url_parsing():
    metadata = json.loads((ROOT / "data/psi_downloads/PSI-69/metadata.json").read_text(encoding="utf-8"))
    assert version_of(metadata) == 5
    # Synthetic URL fixture, never used for a request or as a permanent citation.
    assert get_signed_url(b'{"url":"https://example.org/synthetic-fixture"}') == "https://example.org/synthetic-fixture"
    assert get_signed_url(b"javascript:example") is None


def test_local_upload_does_not_inherit_nasa_source_or_doi():
    # Synthetic metadata is deliberately placed under a real study association.
    exp = {"id": "synthetic-internal", "psi_id": "PSI-69",
           "source_url": "https://psi.nasa.gov/physci/repo/data/investigations/PSI-69",
           "doi": "10.60555/mbq8-0451"}
    doc = {"id": "synthetic-document", "name": "local.txt", "sha256": "a" * 64,
           "provenance": {"source": "local_upload", "evidence_kind": "unclassified"}}
    chunks = structural_chunks(exp, doc, {"pages": [{"page": 1, "text": "Synthetic local material."}]})
    assert chunks and all(not c["source_url"] and not c["doi"] for c in chunks)

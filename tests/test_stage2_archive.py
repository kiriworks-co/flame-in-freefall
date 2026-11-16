"""Archive boundaries use synthetic fixtures; real NASA integrity is checked separately."""
from __future__ import annotations

import io
import json
import stat
import zipfile
from pathlib import Path

import pytest

from scripts.import_stage2_archive import digest, members, write_original

ROOT = Path(__file__).resolve().parents[1]


def archive(entries, compression=zipfile.ZIP_STORED):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", compression) as handle:
        for name, payload in entries:
            handle.writestr(name, payload)
    return zipfile.ZipFile(io.BytesIO(data.getvalue()))


@pytest.mark.parametrize("name", ["../out.csv", "/out.csv", "C:/out.csv", r"..\out.csv",
                                  "file.csv:stream", "folder./out.csv", "NUL.txt", "COM1/file.csv"])
def test_stage2_archive_rejects_unsafe_windows_paths(name):
    with archive([(name, b"synthetic fixture")]) as handle:
        with pytest.raises(ValueError, match="Unsafe"):
            members(handle)


def test_stage2_archive_rejects_duplicate_paths_links_and_expansion():
    with archive([("A.csv", b"a"), ("a.csv", b"b")]) as handle:
        with pytest.raises(ValueError, match="Duplicate"):
            members(handle)
    link = zipfile.ZipInfo("link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with archive([(link, b"../escape")]) as handle:
        with pytest.raises(ValueError, match="non-regular"):
            members(handle)
    with archive([("bomb.txt", b"x" * 100_000)], zipfile.ZIP_DEFLATED) as handle:
        with pytest.raises(ValueError, match="ratio"):
            members(handle)


def test_stage2_original_replay_is_immutable(tmp_path):
    path = tmp_path / "nested" / "fixture.csv"
    write_original(path, b"synthetic original")
    write_original(path, b"synthetic original")
    with pytest.raises(ValueError, match="immutable"):
        write_original(path, b"changed fixture")
    assert path.read_bytes() == b"synthetic original"


@pytest.mark.integration
def test_all_stage2_sources_and_nested_metadata_retain_verified_hashes():
    for sid in ("PSI-62", "PSI-117", "PSI-159"):
        directory = ROOT / "data" / "psi_downloads" / sid
        manifest = json.loads((directory / "source_manifest.json").read_text(encoding="utf8"))
        groups = ("downloaded_csvs", "downloaded_pdfs", "downloaded_documents", "preserved_archives")
        records = [r for group in groups for r in manifest[group]]
        assert records and len({r["filename"] for r in records}) == len(records)
        assert manifest["doi"].startswith("10.")
        for record in records:
            payload = (directory / record["filename"]).read_bytes()
            assert len(payload) == record["size_bytes"]
            assert digest(payload) == record["sha256"]
            assert record["verification"] == "byte_identical_to_nasa_download"
            assert record["source_api_url"].startswith("https://psi.nasa.gov/")
            assert record["doi"] == manifest["doi"]
            if "parent_archive_filename" in record:
                with zipfile.ZipFile(directory / record["parent_archive_filename"]) as handle:
                    assert handle.read(record["nested_member"]) == payload
        # Metadata placeholders and contextual PDFs never become measured datasets.
        if sid == "PSI-62":
            assert not manifest["downloaded_csvs"] and not manifest["downloaded_pdfs"]
            assert all(r["classification"] == "metadata" for r in manifest["downloaded_documents"])

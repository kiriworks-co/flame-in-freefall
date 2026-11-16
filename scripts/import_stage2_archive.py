#!/usr/bin/env python3
"""Verify and import the supplied Stage 2 archive against public NASA PSI files.

Original bytes are immutable. ZIP members are inspected, never extractall'd;
every scientific file must match bytes obtained from the NASA download API.
Run with --verify-online for independent source verification. Subsequent offline
replays require the retained verification manifest and check its hashes again.
No API keys or expiring signed URLs are retained.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlencode, urlparse

try:
    from .fetch_psi_tables import BASE, get_json, get_signed_url, recursive_values, request_bytes, version_of
except ImportError:  # Direct `python scripts/import_stage2_archive.py` invocation.
    from fetch_psi_tables import BASE, get_json, get_signed_url, recursive_values, request_bytes, version_of

PROJECT = Path(__file__).resolve().parents[1]
IDS = ("PSI-62", "PSI-117", "PSI-159")
MAX_MEMBER = 32 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024
MAX_MEMBERS = 100
MAX_RATIO = 200


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    """Reject traversal, Windows alternate streams/devices, links and ZIP bombs."""
    infos = archive.infolist()
    if len(infos) > MAX_MEMBERS or sum(i.file_size for i in infos) > MAX_TOTAL:
        raise ValueError("Archive exceeds count or expanded-byte limit")
    names: set[str] = set()
    for item in infos:
        name = item.filename.replace("\\", "/")
        path = PurePosixPath(name)
        if (path.is_absolute() or re.match(r"^[A-Za-z]:", name) or ".." in path.parts
                or any(":" in p or p.rstrip(" .") != p for p in path.parts)
                or any(re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?", p) for p in path.parts)):
            raise ValueError("Unsafe archive member path")
        mode = item.external_attr >> 16
        if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode))):
            raise ValueError("Archive contains a non-regular member")
        if name.casefold() in names:
            raise ValueError("Duplicate archive member path")
        names.add(name.casefold())
        if item.flag_bits & 1 or item.file_size > MAX_MEMBER:
            raise ValueError("Encrypted or oversized archive member")
        if item.file_size / max(item.compress_size, 1) > MAX_RATIO:
            raise ValueError("Archive compression ratio exceeds limit")
    return [item for item in infos if not item.is_dir()]


def write_original(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError("Symlink destination refused")
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Existing immutable original differs: {path.name}")
    else:
        with path.open("xb") as output:
            output.write(data)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def file_nodes(tree: object) -> list[dict]:
    result = []
    if isinstance(tree, list):
        for node in tree:
            result.extend(file_nodes(node))
    elif isinstance(tree, dict):
        if tree.get("directory") is False and tree.get("visible", True) and not (
            tree.get("restricted") or tree.get("restrictedAccess")
        ):
            result.append(tree)
        for value in tree.values():
            if isinstance(value, (list, dict)):
                result.extend(file_nodes(value))
    return result


def stable_api(sid: str, filename: str, version: int) -> str:
    return f"{BASE}/studies/{sid}/download?" + urlencode(
        {"file": filename, "version": version, "redirect": "false"}
    )


def nasa_bytes(api: str) -> bytes:
    raw = request_bytes(api, max_bytes=1024 * 1024)
    signed = get_signed_url(raw)
    if not signed:
        raise ValueError("NASA API returned no HTTPS download URL")
    host = (urlparse(signed).hostname or "").lower()
    if urlparse(signed).scheme != "https" or not (host.endswith(".amazonaws.com") or host.endswith(".nasa.gov")):
        raise ValueError("NASA download redirect outside allowed hosts")
    return request_bytes(signed, max_bytes=MAX_MEMBER)


def column_roles(filename: str, content: bytes) -> list[dict]:
    """Roles come from explicit Expt/Sim/Model group markers in original CSVs.

    The source column index disambiguates repeated headers. Unmarked model-only
    trajectories are classified using the investigation's CFD approach and the
    publication-linked presentation; missing units are deliberately not inferred.
    """
    matrix = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
    if not matrix:
        return []
    headers = matrix[0]
    rows = matrix[1:]
    roles = ["unclassified"] * len(headers)
    if "Stable_Cool" in filename or "Oscillatory_Cool" in filename:
        roles = ["simulation"] * len(headers)
    elif "Burning_history" in filename:
        roles = ["reported_result" if i < 12 else "simulation" for i in range(len(headers))]
    elif "Radiance_Flame_Diameter" in filename:
        roles = ["reported_result" if i < 14 else "simulation" for i in range(len(headers))]
    elif "Three_Stage" in filename:
        roles = ["reported_result" if i < 26 else "simulation" for i in range(len(headers))]
    elif "Alkane_Extinction" in filename:
        roles = ["reported_result" if (i // 5) % 2 == 0 else "simulation" for i in range(len(headers))]
    elif "C12_Extinction_Diameter_vs_pressure" in filename:
        for i in range(len(headers)):
            roles[i] = "simulation" if i // 3 in {1, 3} else "reported_result"
    elif "MST_2024_Dext" in filename:
        roles = ["simulation" if i < 5 else "reported_result" for i in range(len(headers))]
    elif "MST_2024_Kavg" in filename:
        roles = ["reported_result" if i < 4 else "simulation" for i in range(len(headers))]
    elif filename.startswith("PSI-159"):
        for i, header in enumerate(headers):
            low = header.strip().lower()
            if any(term in low for term in ("cool flame?", "after test", "burn time", "self", "peak burner",
                                             "hot ignition", "color", "comments")):
                roles[i] = "reported_result"
            elif low.startswith(("tad", "zst")):
                roles[i] = "derived"
            elif low in {"day", "fuel", "test", "flame type", "tfp"}:
                roles[i] = "identifier_or_unclassified"
            else:
                roles[i] = "condition"
    return [{"header": h, "column_index": i, "role": roles[i],
             "source_marker": " | ".join(str(r[i]) for r in rows[:3] if i < len(r) and r[i])[:200]}
            for i, h in enumerate(headers)]


def import_archive(archive_path: Path, output: Path, verify_online: bool = False) -> dict:
    if archive_path.stat().st_size > MAX_TOTAL:
        raise ValueError("Compressed archive exceeds byte limit")
    archive_bytes = archive_path.read_bytes()
    audit = {"archive_filename": archive_path.name, "archive_sha256": digest(archive_bytes),
             "archive_size_bytes": len(archive_bytes), "members": [], "anomalies": [], "studies": {}}
    archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    inputs: dict[str, list[tuple[str, bytes]]] = {sid: [] for sid in IDS}
    for item in members(archive):
        content = archive.read(item)
        match = re.search(r"(?:PSI|PIS)-(62|117|159)(?:/|_)", item.filename)
        if not match:
            raise ValueError("Archive member has no allowed investigation identifier")
        sid = "PSI-" + match.group(1)
        audit["members"].append({"archive_member": item.filename, "sha256": digest(content), "size_bytes": len(content)})
        if item.filename.lower().endswith(".zip"):
            nested = zipfile.ZipFile(io.BytesIO(content))
            nested_members = members(nested)
            if not nested_members:
                target = f"archive_anomalies/empty_{digest(item.filename.encode())[:12]}.zip"
                write_original(output / sid / target, content)
                audit["anomalies"].append({"archive_member": item.filename, "preserved_as": f"{sid}/{target}",
                                           "sha256": digest(content), "reason": "Empty 22-byte ZIP; no scientific content"})
                continue
        inputs[sid].append((item.filename, content))
    for sid in IDS:
        destination = output / sid
        old_path = destination / "source_manifest.json"
        old = json.loads(old_path.read_text(encoding="utf8")) if old_path.exists() else {}
        if verify_online:
            metadata = get_json(f"{BASE}/studies/{sid}/metadata")
            version = version_of(metadata)
            if not version:
                history = get_json(f"{BASE}/repo/investigations/{sid}/versions")
                version = max(int(v) for v in recursive_values(history, {"version"}) if str(v).isdigit())
            obfuscation = next((str(v) for v in recursive_values(metadata, {"obfuscationcode", "obfuscation_code"})), "")
            tree = get_json(f"{BASE}/files/v2", {"folder": "", "fileType": "study", "studyId": sid,
                                                "version": version, "obfuscationcode": obfuscation})
            nodes = file_nodes(tree)
            write_json(destination / "metadata.json", metadata)
            # Retain only public file metadata; omit large raw-media listing from versioned artifacts.
            selected_nodes = [n for n in nodes if "/Raw Data/" not in n["key"]]
            write_json(destination / "public_file_inventory.json", {"study_version": version, "files": selected_nodes,
                       "omitted_raw_data_files": len(nodes) - len(selected_nodes)})
        else:
            if not old or old.get("archive_sha256") != audit["archive_sha256"]:
                raise ValueError("First import requires --verify-online for this exact archive")
            metadata = json.loads((destination / "metadata.json").read_text(encoding="utf8"))
            version = old["study_version"]
            nodes = json.loads((destination / "public_file_inventory.json").read_text(encoding="utf8"))["files"]
        study = metadata["studies"][0]
        comments = {c["name"]: c["value"] for c in study.get("comments", [])}
        manifest = {"investigation_id": sid, "title": study["title"], "doi": comments.get("DOI"),
                    "study_version": version, "metadata_source_url": f"{BASE}/studies/{sid}/metadata",
                    "archive_sha256": audit["archive_sha256"], "downloaded_csvs": [], "downloaded_pdfs": [],
                    "downloaded_documents": [], "preserved_archives": [], "status": "verified_originals_imported"}
        source_inputs = list(inputs[sid])
        # Empty uploaded PSI-159/Experimental table folder is supplemented from NASA.
        for node in nodes:
            if sid == "PSI-159" and "/Experimental table/" in node["key"] and node["key"].endswith(".csv"):
                name = PurePosixPath(node["key"]).name
                data = nasa_bytes(stable_api(sid, name, node["version"])) if verify_online else (destination / name).read_bytes()
                source_inputs.append(("NASA_API_SUPPLEMENT/" + name, data))
        for archive_member, content in source_inputs:
            supplied_name = PurePosixPath(archive_member).name
            normalized = re.sub(r" \(1\)(?=\.zip$)", "", supplied_name)
            matches = [n for n in nodes if PurePosixPath(n["key"]).name == normalized]
            # User copy dropped the second period in NASA's engineering PDF name.
            if not matches:
                matches = [n for n in nodes if PurePosixPath(n["key"]).name.replace("..pdf", ".pdf") == normalized]
            if len(matches) != 1:
                raise ValueError(f"NASA file listing does not uniquely identify {supplied_name}")
            node = matches[0]
            name = PurePosixPath(node["key"]).name
            api = stable_api(sid, name, node["version"])
            if len(content) != int(node["bytes_size"]):
                raise ValueError(f"NASA file size mismatch: {name}")
            if verify_online:
                verified = nasa_bytes(api)
                if digest(verified) != digest(content):
                    raise ValueError(f"NASA original SHA-256 mismatch: {name}")
                verified_at = datetime.now(timezone.utc).isoformat()
            else:
                prior = next((r for k in ("downloaded_csvs", "downloaded_pdfs", "downloaded_documents", "preserved_archives")
                              for r in old.get(k, []) if r.get("sha256") == digest(content)), None)
                if not prior or prior.get("verification") != "byte_identical_to_nasa_download":
                    raise ValueError("Offline replay lacks prior independent NASA byte verification")
                verified_at = prior["verified_utc"]
            write_original(destination / name, content)
            record = {"study_id": sid, "source": "NASA Physical Sciences Informatics", "filename": name,
                      "landing_page": f"https://psi.nasa.gov/physci/repo/data/investigations/{sid}",
                      "source_api_url": api, "doi": comments.get("DOI"), "sha256": digest(content),
                      "size_bytes": len(content), "study_version": version, "file_version": node["version"],
                      "verified_utc": verified_at, "retrieved_utc": verified_at,
                      "verification": "byte_identical_to_nasa_download", "archive_member": archive_member,
                      "original_metadata": node, "license": "No file-specific license exposed; retain NASA and author attribution.",
                      "units": "Only explicitly declared source units; unspecified units remain unresolved."}
            suffix = Path(name).suffix.lower()
            if suffix == ".zip":
                record.update(classification="metadata", media_type="application/zip",
                              classification_note="ISA-Tab metadata archive; not numerical experiment or model output.")
                manifest["preserved_archives"].append(record)
                nested = zipfile.ZipFile(io.BytesIO(content))
                for item in members(nested):
                    if not item.filename.endswith(".txt"):
                        raise ValueError("Unexpected ISA metadata archive content")
                    data = nested.read(item)
                    relative = "metadata/" + PurePosixPath(item.filename).name
                    write_original(destination / relative, data)
                    manifest["downloaded_documents"].append({**record, "filename": relative, "sha256": digest(data),
                        "size_bytes": len(data), "media_type": "text/plain", "parent_archive_sha256": digest(content),
                        "parent_archive_filename": name, "nested_member": item.filename,
                        "classification_note": "Original ISA-Tab metadata extracted byte-for-byte from verified NASA archive. "
                                               "s_ file contains placeholder 'Do not use this'; never a scientific sample."})
            elif suffix == ".pdf":
                record.update(classification="engineering_or_publication", media_type="application/pdf",
                              classification_note="Publication/engineering context; numeric assertions require page-specific evidence.")
                manifest["downloaded_pdfs"].append(record)
            elif suffix == ".xlsx":
                record.update(classification="metadata", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                              classification_note="Published data-file/figure map and conditions. XN2=74/85 and XO3=Balance "
                              "are retained verbatim; mixed fraction/percent conventions are unresolved.")
                manifest["downloaded_documents"].append(record)
            elif suffix == ".csv":
                simulation = "Stable_Cool" in name or "Oscillatory_Cool" in name
                record.update(classification=("mixed_conditions_and_reported_results" if sid == "PSI-159" else
                                              "simulation" if simulation else "mixed_experiment_and_simulation"),
                              media_type="text/csv", field_classification=column_roles(name, content),
                              classification_note=("Flight test catalog containing conditions, calculated Tad/Zst and "
                              "reported outcomes (cool flame, burn time, peak burner temperature, termination). "
                              "Not raw measured telemetry; respect field-level evidence roles." if sid == "PSI-159"
                              else "CFD model trajectories, not flight measurements." if simulation else
                              "Published analyzed data contain separate experimental and model series. "
                              "Expt/EXP/Experiment and Sim/Model/Simulation markers define column groups. "
                              "Columns in different groups are independent series; do not align by row as a common clock."))
                manifest["downloaded_csvs"].append(record)
            else:
                raise ValueError("Unsupported verified original format")
            print(sid, name, len(content), "NASA bytes verified" if verify_online else "verified replay", flush=True)
        manifest["availability_note"] = ("NASA exposes metadata only; no raw experimental, numerical model, or PDF files available."
                                         if sid == "PSI-62" else "Selected uploaded originals plus both public experimental tables."
                                         if sid == "PSI-159" else "All uploaded analyzed CSVs, ReadMe, presentations and ISA metadata.")
        write_json(old_path, manifest)
        audit["studies"][sid] = {"doi": manifest["doi"], "study_version": version,
            "documents": len(manifest["downloaded_csvs"]) + len(manifest["downloaded_pdfs"]) + len(manifest["downloaded_documents"]),
            "archives": len(manifest["preserved_archives"]), "availability_note": manifest["availability_note"]}
    write_json(output / "stage2_archive_audit.json", audit)
    return audit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=PROJECT / "data" / "psi_downloads")
    parser.add_argument("--verify-online", action="store_true")
    args = parser.parse_args()
    result = import_archive(args.archive, args.output, args.verify_online)
    print(json.dumps(result["studies"], indent=2))

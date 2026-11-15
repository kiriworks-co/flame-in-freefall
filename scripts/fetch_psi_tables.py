#!/usr/bin/env python3
"""Baixa CSVs Experimental table e, com --pdfs, um PDF pequeno por estudo.

Conector público Geode PSI validado em 2026-11-15. Preserva originais, versão,
DOI, SHA-256 e proveniência; nunca persiste a URL S3 temporária nem gera dados.
Endpoints públicos podem mudar: falhas não são substituídas por dados fictícios.
"""

import argparse
import csv
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse

BASE = "https://psi.nasa.gov/geode-py/ws"
PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_IDS = ["PSI-25", "PSI-26", "PSI-68", "PSI-69", "PSI-98", "PSI-99", "PSI-100", "PSI-101", "PSI-102"]
MAX_BYTES = 25 * 1024 * 1024
HEADERS = {
    "User-Agent": "PSI-Flame-Microgravity/1.0 (+NASA PSI educational research)",
    "Accept": "application/json,text/plain,*/*",
}


def request_bytes(url, data=None, max_bytes=MAX_BYTES):
    request = urllib.request.Request(
        url, data=data, headers={**HEADERS, **({"Content-Type": "application/json"} if data else {})}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                contents = response.read(max_bytes + 1)
            break
        except urllib.error.HTTPError as exc:
            if attempt == 2 or exc.code not in (429, 500, 502, 503, 504):
                raise
            retry_after = exc.headers.get("Retry-After", "")
            time.sleep(min(20, float(retry_after)) if retry_after.isdigit() else 2**attempt)
        except (TimeoutError, urllib.error.URLError):
            if attempt == 2:
                raise
            time.sleep(2**attempt)
    if len(contents) > max_bytes:
        raise ValueError("Download acima do limite de tamanho configurado")
    return contents


def get_json(url, payload=None):
    result = request_bytes(
        url, data=json.dumps(payload).encode("utf8") if payload is not None else None, max_bytes=8 * 1024 * 1024
    )
    return json.loads(result.decode("utf8"))


def recursive_values(value, names):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in names and isinstance(item, (int, str, float)):
                yield item
            yield from recursive_values(item, names)
    elif isinstance(value, list):
        for item in value:
            yield from recursive_values(item, names)


def version_of(metadata):
    candidates = []
    if isinstance(metadata, dict):
        candidates += [metadata.get("version")]
        if isinstance(metadata.get("studies"), dict):
            for val in metadata["studies"].values():
                if isinstance(val, dict):
                    candidates += [val.get("version")]
    for cand in candidates:
        if isinstance(cand, int) and cand >= 1:
            return cand
        if isinstance(cand, str) and cand.isdigit():
            return int(cand)
    return None


def discover_csvs(tree):
    """Filtra arquivos pequenos rotulados Experimental table, sem tentar ler dados científicos."""
    found = []

    def walk(node, category=""):
        if isinstance(node, list):
            for entry in node:
                walk(entry, category)
            return
        if not isinstance(node, dict):
            return
        label = " ".join(
            str(node.get(k) or "")
            for k in (
                "sortingCategory",
                "displayName",
                "key",
                "category",
                "categoryName",
                "type",
                "fileType",
                "folder",
                "name",
                "file_name",
                "fileName",
            )
        )
        next_category = category
        if "experimental table" in label.lower():
            next_category = "Experimental table"
        name = next(
            (
                str(node[k])
                for k in ("key", "fileName", "file_name", "filename", "name")
                if isinstance(node.get(k), str) and node[k].lower().endswith(".csv")
            ),
            None,
        )
        if (
            name
            and next_category == "Experimental table"
            and not node.get("restricted")
            and not node.get("restrictedAccess")
            and node.get("visible", True)
        ):
            found.append(
                {
                    "name": Path(name.replace("\\", "/")).name,
                    "version": node.get("version") or node.get("fileVersion"),
                    "raw_metadata": node,
                }
            )
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                walk(value, next_category)

    walk(tree)
    unique = {item["name"]: item for item in found}
    return list(unique.values())


def get_signed_url(raw):
    """A API costuma retornar uma URL temporária como texto ou JSON."""
    txt = raw.decode("utf8", "replace").strip().strip('"')
    if txt.startswith("https://"):
        return txt
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            for key in ("url", "downloadUrl", "signedUrl", "redirectUrl"):
                if isinstance(obj.get(key), str) and obj[key].startswith("https://"):
                    return obj[key]
    except ValueError:
        pass
    return None


def discover_pdfs(tree):
    """Small, public PSI engineering/publication documents, never large raw media."""
    found = []

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            key = str(node.get("key", ""))
            if (
                key.lower().endswith(".pdf")
                and not node.get("restricted")
                and not node.get("restrictedAccess")
                and node.get("visible", True)
                and 0 < float(node.get("bytes_size", 0)) <= 5 * 1024 * 1024
            ):
                found.append({"name": Path(key).name, "version": node.get("version"), "raw_metadata": node})
            for value in node.values():
                if isinstance(value, (dict, list)):
                    walk(value)

    walk(tree)

    def priority(item):
        key = str(item["raw_metadata"].get("key", "")).lower()
        rank = (
            0
            if "/reports/" in key
            else 1
            if "/science documents/" in key
            else 2
            if "requirements" in key
            else 3
            if "/engineering documents/" in key
            else 4
            if "/presentations/" in key
            else 5
        )
        return rank, float(item["raw_metadata"].get("bytes_size", 0))

    return sorted(found, key=priority)[:1]


def field_classification(data):
    """Conservative labels from published headers, retaining every original string."""
    headers = next(csv.reader(io.StringIO(data.decode("utf-8-sig", "replace"))), [])
    fields = []
    for header in headers:
        low = header.lower()
        if any(
            term in low
            for term in (
                "burning rate",
                "extinction diameter",
                "burn time",
                "test end",
                "final o2",
                "final co",
                "final ambient",
            )
        ):
            role = "reported_result"
        elif any(
            term in low
            for term in (
                "initial",
                "ambient",
                "fuel",
                "pressure",
                "oxygen",
                "o2",
                "flow",
                "temperature",
                "sample material",
            )
        ):
            role = "condition"
        else:
            role = "identifier_or_unclassified"
        warning = (
            "Published rate header declares only mm; dimensional interpretation unresolved. Do not normalize or compare as a rate."
            if "burning rate" in low and low.rstrip().endswith("; mm")
            else None
        )
        fields.append({"header": header, "role": role, "warning": warning})
    return fields


def download_investigation(study_id, output, include_pdfs=False):
    if not re.fullmatch(r"PSI-\d{1,6}", study_id):
        raise ValueError("Invalid ID")
    meta = get_json(f"{BASE}/studies/{study_id}/metadata")
    dest = output / study_id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf8")
    study = meta.get("studies", [{}])[0]
    comments = {item.get("name"): item.get("value") for item in study.get("comments", [])}
    doi = comments.get("DOI") or None
    version = version_of(meta)
    if not version:
        history = get_json(f"{BASE}/repo/investigations/{study_id}/versions")
        versions = [int(v) for v in recursive_values(history, {"version"}) if str(v).isdigit()]
        version = max(versions) if versions else None
    if version is None:
        raise RuntimeError("Sem versão da investigação; não selecionar versão por adivinhação")
    obs = next((str(v) for v in recursive_values(meta, {"obfuscationcode", "obfuscation_code"})), "")
    payload = {"folder": "", "fileType": "study", "studyId": study_id, "version": version, "obfuscationcode": obs}
    tree = get_json(f"{BASE}/files/v2", payload)
    candidates = discover_csvs(tree)
    if include_pdfs:
        candidates += discover_pdfs(tree)
    print(f"{study_id}: versao {version}, {len(candidates)} arquivo(s) selecionado(s)")
    records = []
    for entry in candidates:
        filename = entry["name"]
        fv = entry["version"] or version
        api = f"{BASE}/studies/{study_id}/download?" + urlencode({"file": filename, "version": fv, "redirect": "false"})
        raw = request_bytes(api, max_bytes=1024 * 1024)
        signed = get_signed_url(raw)
        if not signed:
            raise RuntimeError(f"{study_id} {filename}: NASA não retornou URL de download HTTPS")
        signed_host = (urlparse(signed).hostname or "").lower()
        if urlparse(signed).scheme != "https" or not (
            signed_host.endswith(".amazonaws.com") or signed_host.endswith(".nasa.gov")
        ):
            raise ValueError("URL de download fora dos hosts públicos NASA/S3 permitidos")
        data = request_bytes(signed)
        is_pdf = filename.lower().endswith(".pdf")
        if not data or (is_pdf and not data.startswith(b"%PDF-")) or (not is_pdf and b"\x00" in data[:256]):
            raise ValueError("Arquivo inesperado para o formato declarado")
        filepath = dest / filename
        if filepath.exists() and filepath.read_bytes() != data:
            raise RuntimeError(f"Arquivo existente divergente: {filepath}; não sobrescrever original")
        filepath.write_bytes(data)
        record = {
            "study_id": study_id,
            "source": "NASA Physical Sciences Informatics",
            "landing_page": f"https://psi.nasa.gov/physci/repo/data/investigations/{study_id}",
            "source_api_url": api,
            "filename": filename,
            "sha256": hashlib.sha256(data).hexdigest(),
            "size_bytes": len(data),
            "study_version": version,
            "file_version": fv,
            "retrieved_utc": datetime.now(timezone.utc).isoformat(),
            "original_metadata": entry["raw_metadata"],
            "doi": doi,
            "classification": "condition",
            "classification_note": "Experimental table: conditions/sample catalogue; not an independently validated measurement dataset.",
            "license": "No file-specific license exposed by metadata; consult NASA PSI terms and original attribution.",
            "media_type": "text/csv",
            "units": "Preserved as declared in the original column headers; no implicit units assigned.",
        }
        if is_pdf:
            record.update(
                classification="engineering_or_publication",
                media_type="application/pdf",
                classification_note="Official document linked from this PSI investigation; assertions require page-level inspection.",
            )
        else:
            record["field_classification"] = field_classification(data)
            if any(item["role"] == "reported_result" for item in record["field_classification"]):
                record.update(
                    classification="mixed_conditions_and_reported_results",
                    classification_note="Contains conditions and reported outcomes. Preserve header meanings and uncertain units; do not infer material risk rankings.",
                )
        records.append(record)
        print("  OK", filename, len(data), "bytes")
        time.sleep(0.7)
    manifest_path = dest / "source_manifest.json"
    old = json.loads(manifest_path.read_text(encoding="utf8")) if manifest_path.exists() else {}
    pdfs = list(
        {
            r["sha256"]: r
            for r in old.get("downloaded_pdfs", []) + [r for r in records if r["media_type"] == "application/pdf"]
        }.values()
    )
    (dest / "source_manifest.json").write_text(
        json.dumps(
            {
                "investigation_id": study_id,
                "title": study.get("title"),
                "doi": doi,
                "study_version": version,
                "metadata_source_url": f"{BASE}/studies/{study_id}/metadata",
                "downloaded_csvs": [r for r in records if r["media_type"] == "text/csv"],
                "downloaded_pdfs": pdfs,
                "status": "downloaded" if records else "no_csv_exposed",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf8",
    )
    return len(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+", default=DEFAULT_IDS)
    parser.add_argument("--output", type=Path, default=PROJECT / "data" / "psi_downloads")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--pdfs", action="store_true", help="Also download one small public PSI PDF per study (up to 5 MiB)."
    )
    args = parser.parse_args()
    if args.dry_run:
        print("Solicitadas:", ", ".join(args.ids))
        print("Destino:", args.output)
        print("Nenhum dado foi baixado (dry-run)")
    else:
        failure = []
        for study_id in args.ids:
            try:
                download_investigation(study_id, args.output, include_pdfs=args.pdfs)
            except Exception as exc:
                print("ERRO", study_id, ":", exc)
                failure.append(study_id)
            time.sleep(0.7)
        if failure:
            print(
                "Falhas:",
                ", ".join(failure),
                "— consulte o PSI oficial e baixe manualmente ou corrija o conector Geode.",
            )
            raise SystemExit(2)

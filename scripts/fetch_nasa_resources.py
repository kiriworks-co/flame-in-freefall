#!/usr/bin/env python3
"""Download PDFs NASA oficiais de modo conservador: nunca produz PDF sintético."""

import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

NASA_PDFS = {
    "researchers_guide": "https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf",
    "psi_database_guide": "https://assets.science.nasa.gov/content/dam/science/bps/bps-general/bps-data_osdr_psi/Complete_PSI_Database_Guide.pdf",
}
BASE = Path(__file__).resolve().parents[1] / "resources" / "official"
MAX_BYTES = 15 * 1024 * 1024


def download_pdf(key, url, directory=BASE):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (key + ".pdf")
    existing = target.read_bytes() if target.is_file() else None
    request = urllib.request.Request(url, headers={"User-Agent": "PSI-Flame-Microgravity-Research/1.0"})
    with urllib.request.urlopen(request, timeout=40) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or not data.startswith(b"%PDF-"):
        raise ValueError(f"Arquivo inválido/grande demais: {key}")
    if existing is not None and existing != data:
        raise ValueError(f"Original existente divergente; preservar versão anterior: {target}")
    if existing is None:
        target.write_bytes(data)
    (directory / (key + ".provenance.json")).write_text(
        json.dumps(
            {
                "source_url": url,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "status": "downloaded",
                "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "media_type": "application/pdf",
                "classification": "context",
                "license": "NASA publication; no separate file-specific license declared. Credit NASA and original authors; verify third-party content permissions.",
                "doi": None,
                "version": "Publication bytes as retrieved; SHA-256 identifies this copy.",
            },
            indent=2,
        ),
        encoding="utf8",
    )
    print("OK", target, f"({len(data)} bytes)")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--guide", action="store_true", help="Baixa o Researchers Guide de combustao (padrao)")
    parser.add_argument("--psi-manual", action="store_true", help="Baixa o manual PSI")
    opts = parser.parse_args()
    keys = ["researchers_guide"] if opts.guide or not opts.psi_manual else []
    if opts.psi_manual:
        keys.append("psi_database_guide")
    failed = []
    for key in keys:
        try:
            download_pdf(key, NASA_PDFS[key])
        except Exception as e:
            print("ERRO", key, ":", e)
            failed.append(key)
    if failed:
        raise SystemExit(2)

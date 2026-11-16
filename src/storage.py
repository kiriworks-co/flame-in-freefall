"""Persistência local, isolada por experimento, com verificação SHA-256, correções do usuário e reprocessamento."""

from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "experimentos"
CONFIG_DIR = PROJECT_DIR / "config"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower() or "experimento"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Independent workers must never truncate or rename one another's temporary file.
    # Keep the sibling name short on Windows: the destination may be a 64-char SHA.
    temporary = path.with_name(f".tmp-{uuid.uuid4().hex}")
    try:
        with temporary.open("x", encoding="utf-8") as output:
            json.dump(value, output, ensure_ascii=False, indent=2)
        for attempt in range(7):
            try:
                temporary.replace(path)
                break
            except PermissionError:
                # Windows can briefly deny replacement while a reader/rename holds
                # the destination. A real permission failure still propagates.
                if attempt == 6:
                    raise
                time.sleep(.01 * 2 ** attempt)
    finally:
        temporary.unlink(missing_ok=True)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def experiment_dir(experiment: dict[str, Any]) -> Path:
    """Resolve a pasta pelo ID e valida que ela permanece sob DATA_DIR."""
    root = DATA_DIR.resolve()
    candidate = (DATA_DIR / experiment["folder"]).resolve()
    if candidate.parent != root:
        raise ValueError("A pasta do experimento está fora do diretório de dados.")
    return candidate


def create_experiment(name: str, description: str = "") -> dict[str, Any]:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Informe um nome para o experimento.")
    experiment_id = uuid.uuid4().hex
    folder = f"{_slug(clean_name)}-{experiment_id[:8]}"
    record: dict[str, Any] = {
        "id": experiment_id, "folder": folder, "name": clean_name, "description": description.strip(),
        "created_at": utc_now(), "updated_at": utc_now(), "documents": [],
    }
    base = DATA_DIR / folder
    for child in ("originais", "extraidos"):
        (base / child).mkdir(parents=True, exist_ok=True)
    _write_json(base / "experimento.json", record)
    return record


def list_experiments() -> list[dict[str, Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    experiments: list[dict[str, Any]] = []
    for manifest in DATA_DIR.glob("*/experimento.json"):
        try:
            experiments.append(_read_json(manifest))
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(experiments, key=lambda item: item.get("updated_at", ""), reverse=True)


def save_experiment(experiment: dict[str, Any]) -> None:
    experiment["updated_at"] = utc_now()
    _write_json(experiment_dir(experiment) / "experimento.json", experiment)


def update_experiment(experiment: dict[str, Any], name: str, description: str) -> dict[str, Any]:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("O nome do experimento não pode ficar vazio.")
    experiment["name"] = clean_name
    experiment["description"] = description.strip()
    save_experiment(experiment)
    return experiment


def _safe_original_name(filename: str) -> str:
    basename = filename.replace("\\", "/").split("/")[-1].strip()
    basename = re.sub(r"[\x00-\x1f<>:\"|?*]", "_", basename)
    return basename[:180] or "documento"


def _record_for(base: Path, digest: str, filename: str, content: bytes, extraction: dict[str, Any], original_path: Path, extraction_path: Path) -> dict[str, Any]:
    return {
        "id": digest,
        "name": _safe_original_name(filename),
        "extension": Path(filename).suffix.lower(),
        "size_bytes": len(content),
        "sha256": digest,
        "uploaded_at": utc_now(),
        "status": extraction.get("status", "processado"),
        "original_path": str(original_path.relative_to(base)).replace("\\", "/"),
        "extraction_path": str(extraction_path.relative_to(base)).replace("\\", "/"),
        "warnings": extraction.get("warnings", []),
        "table_count": len(extraction.get("tables", [])),
        "page_count": len(extraction.get("pages", [])),
        "schema_version": extraction.get("schema_version", 1),
    }


def save_document(experiment: dict[str, Any], filename: str, content: bytes, extraction: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Guarda o original e a extração; retorna (registro, já_existia)."""
    digest = sha256_bytes(content)
    for known in experiment.get("documents", []):
        if known.get("sha256") == digest:
            if not verify_original(experiment, known):
                raise ValueError("O original existente não confere com o SHA-256; importação interrompida.")
            return known, True
    base = experiment_dir(experiment)
    # Compact archive names avoid Windows MAX_PATH on deeply nested workspaces.
    # The manifest retains the complete filename and full SHA-256; old paths
    # continue to work unchanged when reading existing manifests.
    original_path = base / "originais" / f"{digest[:24]}{Path(filename).suffix.lower()}"
    extraction_path = base / "extraidos" / f"{digest[:24]}.json"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    if original_path.exists():
        if original_path.read_bytes() != content:
            raise ValueError("Colisão de caminho do original; nenhum arquivo foi sobrescrito.")
    else:
        with original_path.open("xb") as original:
            original.write(content)
    record = _record_for(base, digest, filename, content, extraction, original_path, extraction_path)
    extraction["document"] = {"name": record["name"], "extension": record["extension"], "sha256": digest, "size_bytes": len(content)}
    _write_json(extraction_path, extraction)
    experiment.setdefault("documents", []).append(record)
    save_experiment(experiment)
    return record, False


def _safe_child(base: Path, relative_path: str) -> Path:
    candidate = (base / relative_path).resolve()
    if not candidate.is_relative_to(base.resolve()):
        raise ValueError("Caminho de documento inválido.")
    return candidate


def extraction_file(experiment: dict[str, Any], document: dict[str, Any]) -> Path:
    return _safe_child(experiment_dir(experiment), document["extraction_path"])


def load_extraction(experiment: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    return _read_json(extraction_file(experiment, document))


def read_original(experiment: dict[str, Any], document: dict[str, Any]) -> bytes:
    return _safe_child(experiment_dir(experiment), document["original_path"]).read_bytes()


def verify_original(experiment: dict[str, Any], document: dict[str, Any]) -> bool:
    return sha256_bytes(read_original(experiment, document)) == document.get("sha256")


def reextract_document(experiment: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    """Refaz a extração a partir do original (após atualização do extrator). O original não é alterado."""
    from .extractors import extract_document

    if not verify_original(experiment, document):
        raise ValueError(f"O original de '{document['name']}' não confere com o SHA-256 registrado.")
    content = read_original(experiment, document)
    extraction = extract_document(document["name"], content)
    extraction["document"] = {"name": document["name"], "extension": document["extension"], "sha256": document["sha256"], "size_bytes": len(content)}
    _write_json(extraction_file(experiment, document), extraction)
    document.update(
        status=extraction.get("status", "processado"), warnings=extraction.get("warnings", []),
        table_count=len(extraction.get("tables", [])), page_count=len(extraction.get("pages", [])),
        schema_version=extraction.get("schema_version", 1),
    )
    save_experiment(experiment)
    return extraction


# ----------------------------------------------------------------------------- correções do usuário

def table_key(document: dict[str, Any], table_index: int) -> str:
    return f"{document['sha256'][:16]}::{table_index}"


def _overrides_path(experiment: dict[str, Any]) -> Path:
    return experiment_dir(experiment) / "correcoes.json"


def load_overrides(experiment: dict[str, Any]) -> dict[str, Any]:
    path = _overrides_path(experiment)
    if not path.is_file():
        return {}
    try:
        return _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}


def save_overrides(experiment: dict[str, Any], key: str, overrides: dict[str, Any]) -> None:
    """Salva (ou remove, se vazio) as correções de uma tabela, sem tocar no original nem na extração."""
    everything = load_overrides(experiment)
    cleaned = {k: v for k, v in overrides.items() if v}
    if cleaned:
        everything[key] = cleaned
    else:
        everything.pop(key, None)
    _write_json(_overrides_path(experiment), everything)


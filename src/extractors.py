"""Extração local de texto, tabelas, legendas e metadados, com localização no documento original."""

from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path
from typing import Any

from .blocks import detect_blocks, is_filled, json_value, make_table
from .datasets import enrich_table, enrich_tables, tables_from_blocks
from .isa import is_placeholder, isa_pages, looks_like_isa, parse_isa
from .quantities import find_conditions, parse_number

SCHEMA_VERSION = 4
MAX_UPLOAD_BYTES = 30 * 1024 * 1024
MAX_ARCHIVE_BYTES = 120 * 1024 * 1024
MAX_GRID_CELLS = 1_000_000
LARGE_XLSX_BYTES = 20 * 1024 * 1024
PDF_MAX_TABLE_PAGES = 600

SUPPORTED_EXTENSIONS = {
    ".csv", ".tsv", ".dat", ".xls", ".xlsx", ".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".docx", ".txt",
}

_STRICT_NUMBER = re.compile(r"[-+]?(?:\d+[.,]?\d*|[.,]\d+)(?:[eE][-+]?\d+)?")


# ----------------------------------------------------------------------------- utilidades

def _decode(content: bytes) -> tuple[str, str]:
    try:
        return content.decode("utf-8-sig"), "utf-8-sig"
    except UnicodeDecodeError:
        return content.decode("cp1252", errors="replace"), "cp1252"


def _typed(cell: str) -> Any:
    """Converte valores numéricos, preservando identificadores com zeros à esquerda."""
    text = cell.strip()
    if not text:
        return None
    # Códigos de amostra, ensaio e Data ID podem usar zeros à esquerda. A conversão
    # silenciosa de "001" para 1 quebra sua identidade no catálogo.
    unsigned = text[1:] if text.startswith(("+", "-")) else text
    if len(unsigned) > 1 and unsigned.startswith("0") and unsigned.isdigit():
        return text
    if _STRICT_NUMBER.fullmatch(text):
        number = parse_number(text)
        if number is not None:
            return number
    return text


def _delimited_grid(source: str, delimiter: str | None = None) -> tuple[list[list[Any]], list[int], list[str]]:
    warnings: list[str] = []
    if delimiter is None:
        try:
            dialect = csv.Sniffer().sniff(source[:8192], delimiters=",;\t|")
        except csv.Error:
            warnings.append("O separador não foi detectado automaticamente; foi usada a vírgula.")
            dialect = csv.excel
    else:
        dialect = csv.excel_tab if delimiter == "\t" else csv.excel
        dialect = type("D", (dialect,), {"delimiter": delimiter})
    reader = csv.reader(io.StringIO(source, newline=""), dialect)
    grid: list[list[Any]] = []
    numbers: list[int] = []
    previous = 0
    for row in reader:
        if len(grid) * max(1, len(row)) > MAX_GRID_CELLS:
            raise ValueError("Tabela acima do limite de um milhão de células.")
        start = previous + 1
        previous = reader.line_num
        # Linhas em branco são mantidas: é o que separa blocos empilhados.
        grid.append([_typed(cell) for cell in row] if row else [])
        numbers.append(start)
    if not any(any(is_filled(v) for v in row) for row in grid):
        return [], [], warnings
    return grid, numbers, warnings


def _grid_to_result(
    grid: list[list[Any]], row_numbers: list[int], sheet_name: str, extra_warnings: list[str] | None = None
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    detected = detect_blocks(grid, row_numbers)
    tables = tables_from_blocks(sheet_name, detected)
    warnings = list(extra_warnings or []) + detected["warnings"]
    return tables, detected["sheet_titles"], warnings


def _search_text_for_tables(tables: list[dict[str, Any]]) -> str:
    parts = []
    for table in tables:
        parts.append(f"{table['name']} | " + " | ".join(table["columns"]))
    return "\n".join(parts)


def _guess_kind(rows: list[list[Any]]) -> str:
    cells = [v for row in rows for v in row if v is not None and str(v).strip()]
    if not cells:
        return "catalog"
    strings = sum(1 for v in cells if parse_number(v) is None)
    return "catalog" if strings / len(cells) >= 0.5 else "data"


def _wrap_generic_table(table: dict[str, Any], sheet: str, location_range: str = "") -> dict[str, Any]:
    table["block"] = {
        "sheet": sheet, "range": location_range, "label": None, "titles": [], "sheet_titles": [],
        "kind": _guess_kind(table["rows"]), "has_header": True,
    }
    table["params"] = {}
    return table


# ----------------------------------------------------------------------------- CSV / TSV / TXT

def _extract_delimited(content: bytes, delimiter: str | None, kind_label: str) -> dict[str, Any]:
    source, encoding = _decode(content)
    grid, numbers, warnings = _delimited_grid(source, delimiter)
    if not grid:
        raise ValueError("O arquivo não contém cabeçalho nem linhas de dados.")
    tables, titles, warnings = _grid_to_result(grid, numbers, kind_label, warnings)
    for table in tables:
        table["location"] = f"arquivo {kind_label}; {table['location'].split(', ', 1)[-1]}"
    if not tables:
        warnings.append("Nenhuma tabela com cabeçalho e dados foi localizada.")
    return {
        "status": "processado",
        "text": source,
        "pages": [{"page": 1, "location": f"arquivo {kind_label}", "text": source}],
        "tables": tables,
        "raw_matrix": {"rows": grid, "source_rows": numbers},
        "metadata": {"encoding": encoding, "rows": len(grid), "sheet_titles": titles},
        "warnings": warnings,
    }


def _looks_tabular(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()][:60]
    if len(lines) < 3:
        return False
    for delimiter in ("\t", ";", ","):
        counts = [len([c for c in line.split(delimiter) if c.strip()]) for line in lines]
        multi = sum(1 for count in counts if count >= 2)
        if multi / len(lines) >= 0.6 and max(counts) >= 2 and len(set(counts)) <= max(3, len(lines) // 3):
            return True
    return False


def _extract_txt(content: bytes) -> dict[str, Any]:
    text, encoding = _decode(content)
    if is_placeholder(text):
        return {
            "status": "processado", "text": text, "pages": [], "tables": [],
            "metadata": {"encoding": encoding, "placeholder": True},
            "warnings": ["Arquivo de amostras ISA-Tab vazio (placeholder 'Do not use this'); não contém dados."],
        }
    if looks_like_isa(text):
        parsed = parse_isa(text)
        tables: list[dict[str, Any]] = []
        if parsed["publications"]:
            keys = ["year", "title", "authors", "doi", "link", "status"]
            headers = ["Ano", "Título", "Autores", "DOI", "Link", "Situação"]
            rows = [[pub.get(k, "") or None for k in keys] for pub in parsed["publications"]]
            tables.append(_wrap_generic_table(make_table("Publicações (ISA)", "ISA > Estudo > Publicações", headers, rows, 1), "ISA"))
        if parsed["contacts"]:
            keys = ["sobrenome", "nome", "funcao", "afiliacao", "email", "orcid"]
            headers = ["Sobrenome", "Nome", "Função", "Afiliação", "E-mail", "ORCID"]
            rows = [[c.get(k, "") or None for k in keys] for c in parsed["contacts"]]
            tables.append(_wrap_generic_table(make_table("Contatos (ISA)", "ISA > Estudo > Contatos", headers, rows, 1), "ISA"))
        for table in tables:
            table["block"]["kind"] = "catalog"
            enrich_table(table)
        warnings = []
        if parsed["empty_sections"]:
            warnings.append(
                "Seções ISA sem conteúdo: " + ", ".join(parsed["empty_sections"])
                + ". Fatores, ensaios e protocolos não estão descritos; as condições devem vir das planilhas e publicações."
            )
        return {
            "status": "processado", "text": text, "pages": isa_pages(parsed), "tables": tables, "isa": parsed,
            "metadata": {"encoding": encoding, "formato": "ISA-Tab", "estudo": parsed["study"]["id"]},
            "warnings": warnings,
        }
    if _looks_tabular(text):
        try:
            return _extract_delimited(content, None, "TXT")
        except ValueError:
            pass
    lines = text.splitlines()
    pages = [{"page": n, "location": f"linha {n}", "text": line} for n, line in enumerate(lines, start=1) if line.strip()]
    return {
        "status": "processado", "text": text, "pages": pages, "tables": [],
        "metadata": {"encoding": encoding, "line_count": len(lines)}, "warnings": [],
    }


# ----------------------------------------------------------------------------- Excel

def _extract_excel(content: bytes, extension: str) -> dict[str, Any]:
    tables: list[dict[str, Any]] = []
    formulas: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {"sheets": [], "sheet_titles": {}}
    warnings: list[str] = []

    sheets: list[tuple[str, list[list[Any]]]] = []
    if extension == ".xlsx":
        from openpyxl import load_workbook

        read_only = len(content) > LARGE_XLSX_BYTES
        values_book = load_workbook(io.BytesIO(content), data_only=True, read_only=read_only)
        try:
            for sheet in values_book.worksheets:
                if sheet.max_row * sheet.max_column > MAX_GRID_CELLS:
                    raise ValueError("Planilha acima do limite de um milhão de células.")
                grid = [[json_value(v) for v in row] for row in sheet.iter_rows(values_only=True)]
                sheets.append((sheet.title, grid))
        finally:
            values_book.close()
        if not read_only:
            formula_book = load_workbook(io.BytesIO(content), data_only=False)
            cached = {name: grid for name, grid in sheets}
            try:
                for sheet in formula_book.worksheets:
                    for row in sheet.iter_rows():
                        for cell in row:
                            if isinstance(cell.value, str) and cell.value.startswith("="):
                                grid = cached.get(sheet.title, [])
                                value = grid[cell.row - 1][cell.column - 1] if cell.row - 1 < len(grid) and cell.column - 1 < len(grid[cell.row - 1]) else None
                                formulas.append({"sheet": sheet.title, "cell": cell.coordinate, "formula": cell.value, "cached_value": value})
            finally:
                formula_book.close()
        else:
            warnings.append("Arquivo grande: fórmulas não foram listadas (leitura em modo econômico).")
    else:
        try:
            import xlrd
        except ImportError as error:
            raise ImportError("Para ler .xls instale o pacote 'xlrd' (pip install xlrd).") from error
        book = xlrd.open_workbook(file_contents=content, on_demand=True)
        try:
            for sheet in book.sheets():
                if sheet.nrows * sheet.ncols > MAX_GRID_CELLS:
                    raise ValueError("Planilha acima do limite de um milhão de células.")
                grid = [
                    [json_value(sheet.cell_value(r, c)) for c in range(sheet.ncols)]
                    for r in range(sheet.nrows)
                ]
                sheets.append((sheet.name, grid))
        finally:
            book.release_resources()
        warnings.append("A extração de fórmulas em arquivos XLS antigos é limitada pela biblioteca utilizada.")

    for name, grid in sheets:
        metadata["sheets"].append(name)
        sheet_tables, titles, sheet_warnings = _grid_to_result(grid, list(range(1, len(grid) + 1)), name)
        tables.extend(sheet_tables)
        warnings.extend(f"Planilha '{name}': {w}" for w in sheet_warnings)
        if titles:
            metadata["sheet_titles"][name] = titles
    if not tables:
        warnings.append("Nenhuma tabela com células preenchidas foi localizada.")
    text = _search_text_for_tables(tables)
    return {
        "status": "processado", "text": text,
        "pages": [{"page": 1, "location": "arquivo de planilhas", "text": text}],
        "tables": tables, "formulas": formulas,
        "raw_matrices": [{"sheet": name, "rows": grid} for name, grid in sheets],
        "metadata": metadata, "warnings": warnings,
    }


# ----------------------------------------------------------------------------- PDF

_CAPTION = re.compile(
    r"^(?P<kind>Figure|Fig\.|Figura|Table|Tabela)\s*(?P<num>[A-Za-z]?\d+(?:[.\-]\d+)*[a-z]?)[\.:\)]?\s+(?P<rest>[A-Z(\[].+)$",
    re.S,
)


def _captions_from_blocks(page_number: int, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    captions = []
    for block in blocks:
        text = re.sub(r"\s+", " ", block["text"]).strip()
        if len(text) < 25 or re.search(r"\.{4,}", text):
            continue
        match = _CAPTION.match(text)
        if not match:
            continue
        kind = "tabela" if match.group("kind").lower().startswith("tab") else "figura"
        captions.append({
            "kind": kind, "number": match.group("num"), "page": page_number, "bbox": block["bbox"],
            "text": text[:700], "conditions": find_conditions(text),
        })
    return captions


def _pdf_tables(page: Any, page_number: int) -> list[dict[str, Any]]:
    if not hasattr(page, "find_tables"):
        return []
    try:
        found = page.find_tables()
    except Exception:
        return []
    result = []
    for index, detected in enumerate(getattr(found, "tables", []), start=1):
        try:
            raw = detected.extract()
        except Exception:
            continue
        rows = [
            [
                None if cell is None or (isinstance(cell, str) and not cell.strip())
                else cell.strip() if isinstance(cell, str) else cell
                for cell in row
            ]
            for row in raw if row
        ]
        if len(rows) < 3 or max(len(r) for r in rows) < 2:
            continue
        cells = [c for r in rows for c in r]
        if sum(c is not None for c in cells) / max(1, len(cells)) < 0.5:
            continue
        typed = [[_typed(c) if isinstance(c, str) else c for c in row] for row in rows]
        table = make_table(
            f"Tabela detectada p.{page_number}.{index}", f"página {page_number}, tabela {index}",
            typed[0], typed[1:], 1,
        )
        _wrap_generic_table(table, f"página {page_number}", "bbox " + ",".join(str(round(x)) for x in detected.bbox))
        table["page"] = page_number
        table["bbox"] = [round(float(x), 2) for x in detected.bbox]
        enrich_table(table)
        result.append(table)
    return result


def _extract_pdf(content: bytes) -> dict[str, Any]:
    import fitz

    pages: list[dict[str, Any]] = []
    captions: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    warnings: list[str] = []
    with fitz.open(stream=content, filetype="pdf") as pdf:
        metadata = {key: value for key, value in (pdf.metadata or {}).items() if value}
        metadata["page_count"] = pdf.page_count
        if pdf.page_count > 1000:
            raise ValueError("PDF acima do limite de mil páginas.")
        for index, page in enumerate(pdf, start=1):
            text = page.get_text("text", sort=True).strip()
            method = "camada de texto do PDF"
            blocks: list[dict[str, Any]] = []
            if text:
                for block in page.get_text("blocks", sort=True):
                    block_text = str(block[4]).strip()
                    if block_text:
                        first_line = block_text.splitlines()[0]
                        kind = "heading_candidate" if len(first_line) < 110 and not first_line.endswith((".", ",")) and len(block_text.splitlines()) <= 2 else "text"
                        blocks.append({"bbox": [round(float(x), 2) for x in block[:4]], "text": block_text, "kind": kind})
                captions.extend(_captions_from_blocks(index, blocks))
                if index <= PDF_MAX_TABLE_PAGES:
                    tables.extend(_pdf_tables(page, index))
            else:
                try:
                    ocr = page.get_textpage_ocr(language="por+eng", dpi=200, full=True)
                    text = page.get_text("text", textpage=ocr, sort=True).strip()
                    method = "OCR (texto reconhecido)" if text else "sem texto extraível"
                except Exception:
                    warnings.append(f"Página {index}: sem camada de texto; OCR indisponível ou não configurado.")
                    method = "sem texto extraível"
            pages.append({"page": index, "location": f"página {index}", "text": text, "method": method, "blocks": blocks})
    all_text = "\n\n".join(p["text"] for p in pages if p["text"])
    metadata["legendas"] = len(captions)
    metadata["tabelas_detectadas"] = len(tables)
    if tables:
        warnings.append(
            f"{len(tables)} tabela(s) detectada(s) automaticamente no PDF; confira visualmente, pois a detecção pode errar. "
            "Dados de figuras (gráficos) não são extraídos como números."
        )
    return {
        "status": "processado" if all_text or not warnings else "parcial",
        "text": all_text, "pages": pages, "tables": tables, "captions": captions,
        "metadata": metadata, "warnings": warnings,
    }


def render_pdf_page(content: bytes, page_number: int, dpi: int = 110) -> bytes:
    """Imagem PNG de uma página do PDF para conferência visual de legendas e tabelas."""
    import fitz

    with fitz.open(stream=content, filetype="pdf") as pdf:
        page = pdf[page_number - 1]
        return page.get_pixmap(dpi=dpi).tobytes("png")


# ----------------------------------------------------------------------------- DOCX e imagens

def _extract_docx(content: bytes) -> dict[str, Any]:
    from docx import Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    document = Document(io.BytesIO(content))
    text_blocks: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    paragraph_number = table_number = 0
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            paragraph_number += 1
            paragraph = Paragraph(child, document)
            if paragraph.text.strip():
                text_blocks.append({"page": paragraph_number, "location": f"parágrafo {paragraph_number}", "text": paragraph.text})
        elif isinstance(child, CT_Tbl):
            table_number += 1
            values = [[(cell.text.strip() or None) for cell in row.cells] for row in Table(child, document).rows]
            if values:
                typed = [[_typed(c) if isinstance(c, str) else c for c in row] for row in values]
                table = make_table(f"Tabela {table_number}", f"tabela {table_number} do DOCX", typed[0], typed[1:], 1, list(range(2, len(values) + 1)))
                tables.append(_wrap_generic_table(table, f"Tabela {table_number}"))
    enrich_tables(tables)
    core = document.core_properties
    metadata = {
        key: json_value(getattr(core, key, None))
        for key in ("title", "subject", "author", "created", "modified", "keywords")
        if getattr(core, key, None)
    }
    return {
        "status": "processado", "text": "\n\n".join(b["text"] for b in text_blocks),
        "pages": text_blocks, "tables": tables, "metadata": metadata, "warnings": [],
    }


def _extract_image(content: bytes) -> dict[str, Any]:
    from PIL import ExifTags, Image

    image = Image.open(io.BytesIO(content))
    exif: dict[str, Any] = {}
    try:
        for tag, value in image.getexif().items():
            label = ExifTags.TAGS.get(tag, str(tag))
            if isinstance(value, (str, int, float, bytes)):
                exif[label] = value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value
    except Exception:
        exif = {}
    pages: list[dict[str, Any]] = []
    warnings: list[str] = []
    frame_count = getattr(image, "n_frames", 1)
    try:
        import pytesseract

        for frame_number in range(frame_count):
            image.seek(frame_number)
            frame = image.convert("RGB")
            try:
                recognized = pytesseract.image_to_data(frame, lang="por+eng", output_type=pytesseract.Output.DICT)
            except Exception:
                recognized = pytesseract.image_to_data(frame, lang="eng", output_type=pytesseract.Output.DICT)
            tokens = []
            for i, token in enumerate(recognized.get("text", [])):
                label = str(token).strip()
                if not label:
                    continue
                try:
                    confidence = float(recognized["conf"][i])
                except (ValueError, TypeError, KeyError):
                    confidence = -1
                tokens.append({
                    "text": label, "confidence": confidence,
                    "bbox": [recognized["left"][i], recognized["top"][i], recognized["width"][i], recognized["height"][i]],
                })
            pages.append({
                "page": frame_number + 1, "location": f"quadro {frame_number + 1} da imagem",
                "text": " ".join(t["text"] for t in tokens), "method": "OCR", "words": tokens,
            })
    except ImportError:
        warnings.append("OCR não disponível: instale pytesseract e o executável Tesseract para extrair texto da imagem.")
    except Exception as error:
        warnings.append(f"Não foi possível concluir o OCR da imagem: {error}")
    text = "\n".join(p["text"] for p in pages if p["text"])
    if not pages and not warnings:
        warnings.append("A imagem foi indexada; OCR não produziu texto reconhecível.")
    return {
        "status": "processado" if text else "parcial", "text": text, "pages": pages, "tables": [],
        "metadata": {"format": image.format, "mode": image.mode, "width": image.width, "height": image.height,
                     "frames": frame_count, "exif": exif},
        "warnings": warnings,
    }


# ----------------------------------------------------------------------------- entrada principal

def extract_document(filename: str, content: bytes) -> dict[str, Any]:
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato não suportado: {extension or '(sem extensão)'}")
    if not content:
        raise ValueError("O arquivo está vazio.")
    validate_upload(filename, content)
    try:
        if extension == ".csv":
            result = _extract_delimited(content, None, "CSV")
        elif extension in {".tsv", ".dat"}:
            result = _extract_delimited(content, "\t", extension.lstrip(".").upper())
        elif extension in {".xls", ".xlsx"}:
            result = _extract_excel(content, extension)
        elif extension == ".pdf":
            result = _extract_pdf(content)
        elif extension == ".docx":
            result = _extract_docx(content)
        elif extension == ".txt":
            result = _extract_txt(content)
        else:
            result = _extract_image(content)
    except Exception as error:
        return {
            "status": "erro", "text": "", "pages": [], "tables": [], "metadata": {},
            "warnings": [f"Falha na extração: {type(error).__name__}: {error}"],
            "schema_version": SCHEMA_VERSION, "source_filename": filename, "source_extension": extension,
        }
    result["schema_version"] = SCHEMA_VERSION
    result["source_filename"] = filename
    result["source_extension"] = extension
    return result


def validate_upload(filename: str, content: bytes) -> None:
    """Reject resource abuse and unsafe OOXML archives before parser invocation."""
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Arquivo acima do limite de 30 MiB.")
    if Path(filename).suffix.lower() in {".xlsx", ".docx"}:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            entries = archive.infolist()
            if len(entries) > 10000 or sum(item.file_size for item in entries) > MAX_ARCHIVE_BYTES:
                raise ValueError("Arquivo compactado excede os limites de extração.")
            for item in entries:
                path = item.filename.replace("\\", "/")
                if path.startswith("/") or re.match(r"^[A-Za-z]:", path) or ".." in path.split("/"):
                    raise ValueError("Caminho inseguro no arquivo compactado.")
                if item.file_size > 1024 * 1024 and item.file_size / max(1, item.compress_size) > 200:
                    raise ValueError("Taxa de compressão excede o limite de segurança.")


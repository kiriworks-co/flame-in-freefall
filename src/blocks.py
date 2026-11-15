"""Detecção de blocos tabulares em uma grade de células (planilha, CSV, TSV).

Uma planilha de dados científicos raramente é "uma tabela por aba": há títulos,
blocos empilhados, blocos lado a lado e rótulos soltos acima ou ao lado do
cabeçalho. O algoritmo:

1. Marca células preenchidas e agrupa por conectividade 4 (vizinhança direta).
   Uma linha ou coluna em branco separa blocos.
2. Funde blocos de texto (catálogos) que ficaram separados de sua vizinha
   numérica por uma única coluna em branco.
3. Em cada bloco separa: título(s), rótulo, cabeçalho e linhas de dados.
   Uma coluna com cabeçalho mas sem dados abaixo é um rótulo do bloco
   (ex.: "nC12", "O3 = 4.1 mol.%"), não uma coluna.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Any

from .quantities import infer_column_name, parse_label_params

MAX_CELLS_FOR_DETECTION = 3_000_000


def is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    return not (isinstance(value, str) and not value.strip())


def column_letter(index: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA."""
    letters = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def json_value(value: Any) -> Any:
    from datetime import date, datetime, time

    if isinstance(value, float) and not math.isfinite(value):
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    return str(value)


def unique_headers(values: list[Any]) -> tuple[list[str], list[str]]:
    original = ["" if value is None else str(value) for value in values]
    result: list[str] = []
    seen: dict[str, int] = {}
    for index, label in enumerate(original, start=1):
        base = label.strip() or f"Coluna {index}"
        seen[base] = seen.get(base, 0) + 1
        result.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
    return result, original


def make_table(
    name: str,
    location: str,
    raw_headers: list[Any],
    rows: list[list[Any]],
    header_row: int | None,
    row_numbers: list[int] | None = None,
) -> dict[str, Any]:
    columns, original_headers = unique_headers(raw_headers)
    width = len(columns)
    normalized = []
    for row in rows:
        values = [json_value(value) for value in row[:width]]
        values.extend([None] * (width - len(values)))
        normalized.append(values)
    start = (header_row or 0) + 1
    return {
        "name": name,
        "location": location,
        "header_row": header_row,
        "columns": columns,
        "original_headers": original_headers,
        "rows": normalized,
        "source_rows": row_numbers or list(range(start, start + len(normalized))),
        "first_data_row": (row_numbers[0] if row_numbers else start),
    }


# ----------------------------------------------------------------------------- componentes conexos

def _components(mask: list[list[bool]]) -> list[list[tuple[int, int]]]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    seen = [[False] * width for _ in range(height)]
    result: list[list[tuple[int, int]]] = []
    for r in range(height):
        for c in range(width):
            if not mask[r][c] or seen[r][c]:
                continue
            queue = deque([(r, c)])
            seen[r][c] = True
            cells: list[tuple[int, int]] = []
            while queue:
                y, x = queue.popleft()
                cells.append((y, x))
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < height and 0 <= nx < width and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        queue.append((ny, nx))
            result.append(cells)
    return result


def _bbox(cells: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    rows = [y for y, _ in cells]
    cols = [x for _, x in cells]
    return min(rows), min(cols), max(rows), max(cols)  # top, left, bottom, right


def _text_fraction(grid: list[list[Any]], cells: list[tuple[int, int]], top: int) -> float:
    body = [grid[y][x] for y, x in cells if y > top]
    if not body:  # bloco de uma só linha: usa todas as células
        body = [grid[y][x] for y, x in cells]
    if not body:
        return 0.0
    return sum(isinstance(v, str) for v in body) / len(body)


def _merge_text_neighbours(grid: list[list[Any]], comps: list[list[tuple[int, int]]]) -> list[list[tuple[int, int]]]:
    """Funde um bloco de texto (catálogo) à vizinha à esquerda separada por 1 a 3 colunas em branco."""
    comps = sorted(comps, key=lambda cells: (_bbox(cells)[1], _bbox(cells)[0]))
    merged = True
    while merged:
        merged = False
        for i, a in enumerate(comps):
            ta, la, ba, ra = _bbox(a)
            for j, b in enumerate(comps):
                if i == j:
                    continue
                tb, lb, bb, rb = _bbox(b)
                if lb - ra not in (2, 3, 4):
                    continue
                inside = tb >= ta and bb <= ba
                if not inside:
                    continue
                if _text_fraction(grid, b, tb) >= 0.8 and _text_fraction(grid, a, ta) < 0.8:
                    comps[i] = a + b
                    del comps[j]
                    merged = True
                    break
            if merged:
                break
    return comps


# ----------------------------------------------------------------------------- estrutura de cada bloco

def _row_filled(sub: list[list[Any]], r: int) -> list[int]:
    return [c for c, value in enumerate(sub[r]) if is_filled(value)]


def _structure(sub: list[list[Any]], rows_src: list[int], col_src: list[int]) -> dict[str, Any] | None:
    """Transforma um sub-grid (linhas x colunas do bloco) em título/rótulo/cabeçalho/dados."""
    popped: list[str] = []
    start = 0

    def single_text(r: int) -> bool:
        filled = _row_filled(sub, r)
        return len(filled) == 1 and isinstance(sub[r][filled[0]], str)

    while start + 1 < len(sub) and single_text(start):
        nxt = len(_row_filled(sub, start + 1))
        after = len(_row_filled(sub, start + 2)) if start + 2 < len(sub) else 0
        if nxt >= 2 or (nxt == 1 and after >= 2):
            popped.append(str(sub[start][_row_filled(sub, start)[0]]).strip())
            start += 1
        else:
            break
    body_rows = list(range(start, len(sub)))
    if not body_rows:
        return None

    header_idx = body_rows[0]
    header_cells = [sub[header_idx][c] for c in range(len(sub[0]))]
    filled_header = [v for v in header_cells if is_filled(v)]
    strings = sum(isinstance(v, str) for v in filled_header)
    has_header = bool(filled_header) and strings / len(filled_header) >= 0.6
    data_rows = body_rows[1:] if has_header else body_rows

    width = len(sub[0])
    labels: list[str] = []
    kept: list[int] = []
    for c in range(width):
        column_data = [sub[r][c] for r in data_rows]
        has_data = any(is_filled(v) for v in column_data)
        header_value = header_cells[c] if has_header else None
        if has_data:
            kept.append(c)
        elif has_header and is_filled(header_value) and data_rows:
            labels.append(str(header_value).strip())
    if not kept:
        return None

    label_column = " | ".join(labels) if labels else None

    headers: list[Any] = []
    for c in kept:
        if has_header and is_filled(header_cells[c]):
            headers.append(str(header_cells[c]).strip())
        else:
            headers.append(infer_column_name([sub[r][c] for r in data_rows]))
    rows: list[list[Any]] = []
    source_rows: list[int] = []
    for r in data_rows:
        values = [sub[r][c] for c in kept]
        if any(is_filled(v) for v in values):
            rows.append(values)
            source_rows.append(rows_src[r])

    cells_count = sum(1 for row in rows for v in row if is_filled(v))
    strings_count = sum(1 for row in rows for v in row if isinstance(v, str) and v.strip())
    kind = "catalog" if cells_count and strings_count / cells_count >= 0.5 else "data"

    first_col, last_col = col_src[kept[0]], col_src[kept[-1]]
    top_row = rows_src[header_idx]
    bottom_row = source_rows[-1] if source_rows else top_row
    return {
        "popped": popped,
        "label_column": label_column,
        "col_span": (first_col, last_col),
        "headers": headers,
        "has_header": has_header,
        "rows": rows,
        "source_rows": source_rows,
        "header_row": top_row if has_header else None,
        "range": f"{column_letter(first_col)}{top_row}:{column_letter(last_col)}{bottom_row}",
        "kind": kind,
    }


def detect_blocks(grid: list[list[Any]], row_numbers: list[int] | None = None) -> dict[str, Any]:
    """Detecta blocos em ``grid`` (lista de linhas). ``row_numbers[i]`` é a linha de origem da linha i."""
    if not grid:
        return {"sheet_titles": [], "blocks": [], "warnings": []}
    width = max(len(row) for row in grid)
    grid = [list(row) + [None] * (width - len(row)) for row in grid]
    row_numbers = row_numbers or list(range(1, len(grid) + 1))
    warnings: list[str] = []

    mask = [[is_filled(v) for v in row] for row in grid]
    filled_total = sum(sum(row) for row in mask)
    if filled_total == 0:
        return {"sheet_titles": [], "blocks": [], "warnings": []}

    if len(grid) * width > MAX_CELLS_FOR_DETECTION:
        warnings.append("Planilha muito grande: detecção de blocos simplificada (um bloco, cabeçalho na primeira linha).")
        comps = [[(y, x) for y in range(len(grid)) for x in range(width) if mask[y][x]]]
    else:
        comps = _merge_text_neighbours(grid, _components(mask))
    comps.sort(key=lambda cells: (_bbox(cells)[0], _bbox(cells)[1]))

    sheet_titles: list[str] = []
    blocks: list[dict[str, Any]] = []
    for cells in comps:
        top, left, bottom, right = _bbox(cells)
        if len(cells) == 1:
            value = grid[cells[0][0]][cells[0][1]]
            sheet_titles.append(str(value).strip())
            continue
        in_comp = set(cells)
        sub = [
            [grid[y][x] if (y, x) in in_comp else None for x in range(left, right + 1)]
            for y in range(top, bottom + 1)
        ]
        structured = _structure(sub, row_numbers[top:bottom + 1], list(range(left, right + 1)))
        if structured is None:
            continue
        blocks.append(structured)

    blocks = _merge_continuations(blocks)
    multi = len(blocks) > 1
    for block in blocks:
        popped = block.pop("popped")
        label_column = block.pop("label_column")
        if label_column:
            block["label"], block["titles"] = label_column, popped
        elif len(popped) >= 2:
            block["label"], block["titles"] = popped[-1], popped[:-1]
        elif len(popped) == 1 and (parse_label_params(popped[0]) or (multi and block is not blocks[0])):
            block["label"], block["titles"] = popped[0], []
        else:
            block["label"], block["titles"] = None, popped
        for title in block["titles"]:
            if title not in sheet_titles:
                sheet_titles.append(title)
    return {"sheet_titles": sheet_titles, "blocks": blocks, "warnings": warnings}


def _merge_continuations(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Une blocos sem cabeçalho ao bloco anterior de mesma largura (tabela quebrada por linhas em branco)."""
    merged: list[dict[str, Any]] = []
    for block in blocks:
        previous = merged[-1] if merged else None
        if (
            previous is not None
            and not block["has_header"]
            and previous["has_header"]
            and previous["col_span"] == block["col_span"]
            and len(previous["headers"]) == len(block["headers"])
            and not block["popped"]
        ):
            previous["rows"].extend(block["rows"])
            previous["source_rows"].extend(block["source_rows"])
            start, end = previous["range"].split(":")
            end_col = "".join(ch for ch in end if ch.isalpha())
            previous["range"] = f"{start}:{end_col}{block['source_rows'][-1] if block['source_rows'] else ''}"
            continue
        merged.append(block)
    return merged


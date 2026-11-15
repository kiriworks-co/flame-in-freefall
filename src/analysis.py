"""Transformações e análises numéricas sobre séries (sempre explícitas e reprodutíveis)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def prepare_series(
    x: pd.Series,
    y: pd.Series,
    *,
    sort: bool = True,
    x_min: float | None = None,
    x_max: float | None = None,
    baseline: str = "nenhuma",      # nenhuma | mínimo | primeiros N
    baseline_n: int = 10,
    normalize: str = "nenhuma",     # nenhuma | pico | mín-máx
    smooth: int = 0,                # janela (pontos) de média móvel centrada
    max_points: int = 0,            # 0 = sem redução
) -> pd.DataFrame:
    frame = pd.DataFrame({"x": pd.to_numeric(x, errors="coerce"), "y": pd.to_numeric(y, errors="coerce")}).dropna()
    if sort:
        frame = frame.sort_values("x", kind="stable")
    if x_min is not None:
        frame = frame[frame["x"] >= x_min]
    if x_max is not None:
        frame = frame[frame["x"] <= x_max]
    frame = frame.reset_index(drop=True)
    if frame.empty:
        return frame
    if baseline == "mínimo":
        frame["y"] = frame["y"] - frame["y"].min()
    elif baseline == "primeiros N":
        frame["y"] = frame["y"] - frame["y"].head(max(1, baseline_n)).mean()
    if smooth and smooth > 1:
        frame["y"] = frame["y"].rolling(int(smooth), center=True, min_periods=1).mean()
    if normalize == "pico":
        peak = frame["y"].abs().max()
        if peak > 0:
            frame["y"] = frame["y"] / peak
    elif normalize == "mín-máx":
        low, high = frame["y"].min(), frame["y"].max()
        if high > low:
            frame["y"] = (frame["y"] - low) / (high - low)
    if max_points and len(frame) > max_points:
        frame = decimate(frame, max_points)
    return frame


def decimate(frame: pd.DataFrame, max_points: int) -> pd.DataFrame:
    """Reduz pontos preservando picos: em cada faixa de X mantém o mínimo e o máximo de Y."""
    buckets = max(1, max_points // 2)
    edges = np.linspace(0, len(frame), buckets + 1, dtype=int)
    keep: set[int] = {0, len(frame) - 1}
    values = frame["y"].to_numpy()
    for start, end in zip(edges[:-1], edges[1:]):
        if end > start:
            segment = values[start:end]
            keep.add(start + int(segment.argmin()))
            keep.add(start + int(segment.argmax()))
    return frame.iloc[sorted(keep)].reset_index(drop=True)


def fit_linear(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 3 or np.ptp(x) == 0:
        return {"n": int(len(x)), "slope": None, "intercept": None, "r": None, "r2": None}
    slope, intercept = np.polyfit(x, y, 1)
    residual = y - (slope * x + intercept)
    total = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((residual ** 2).sum()) / total if total > 0 else None
    r = float(np.corrcoef(x, y)[0, 1]) if np.ptp(y) > 0 else None
    return {"n": int(len(x)), "slope": float(slope), "intercept": float(intercept), "r": r, "r2": r2}


def peak_info(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 3:
        return {"x_peak": None, "y_peak": None, "fwhm": None}
    i = int(np.argmax(y))
    base, top = float(y.min()), float(y[i])
    half = base + (top - base) / 2
    fwhm = None
    if top > base:
        left = np.where(y[:i] <= half)[0]
        right = np.where(y[i:] <= half)[0]
        if len(left) and len(right):
            li, ri = left[-1], i + right[0]
            xl = np.interp(half, [y[li], y[li + 1]], [x[li], x[li + 1]]) if y[li + 1] != y[li] else x[li]
            xr = np.interp(half, [y[ri], y[ri - 1]], [x[ri], x[ri - 1]]) if y[ri - 1] != y[ri] else x[ri]
            fwhm = float(abs(xr - xl))
    return {"x_peak": float(x[i]), "y_peak": top, "fwhm": fwhm}


def final_point(x: np.ndarray, y: np.ndarray, min_y: float = 0.0) -> dict[str, Any]:
    """Último ponto com y > min_y (útil para diâmetro/tempo de extinção em históricos D(t))."""
    mask = np.isfinite(x) & np.isfinite(y) & (y > min_y)
    if not mask.any():
        return {"x_final": None, "y_final": None}
    order = np.argsort(x[mask])
    return {"x_final": float(x[mask][order][-1]), "y_final": float(y[mask][order][-1])}


def common_grid(series: dict[str, pd.DataFrame], points: int = 400) -> dict[str, pd.DataFrame]:
    """Interpola todas as séries na interseção de seus intervalos de X (para sobrepor malhas diferentes)."""
    valid = {k: v for k, v in series.items() if len(v) >= 2}
    if len(valid) < 2:
        return series
    low = max(v["x"].min() for v in valid.values())
    high = min(v["x"].max() for v in valid.values())
    if not high > low:
        return series
    grid = np.linspace(low, high, points)
    return {k: pd.DataFrame({"x": grid, "y": np.interp(grid, v["x"], v["y"])}) for k, v in valid.items()}


DERIVED_OPS = ["quadrado (A²)", "razão (A/B)", "diferença (A−B)", "produto (A×B)", "escala (A×k)", "derivada dA/dB"]


def derive_column(frame: pd.DataFrame, op: str, a: str, b: str | None = None, k: float = 1.0) -> pd.Series:
    x = frame[a].astype(float)
    if op.startswith("quadrado"):
        return x ** 2
    if op.startswith("escala"):
        return x * k
    if b is None:
        raise ValueError("Esta operação exige a coluna B.")
    y = frame[b].astype(float)
    if op.startswith("razão"):
        return x / y.replace(0, np.nan)
    if op.startswith("diferença"):
        return x - y
    if op.startswith("produto"):
        return x * y
    if op.startswith("derivada"):
        order = np.argsort(y.to_numpy())
        result = np.full(len(x), np.nan)
        result[order] = np.gradient(x.to_numpy()[order], y.to_numpy()[order])
        return pd.Series(result, index=frame.index)
    raise ValueError(f"Operação desconhecida: {op}")


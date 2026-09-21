"""NIGHTINGALE: a compact research prototype for Recursive ALE auditing."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Any
import numpy as np
import pandas as pd


@dataclass
class EffectNode:
    feature: str
    depth: int
    centers: list[float]
    effects: list[float]
    counts: list[int]
    amplitude: float
    stability: float | None = None
    stop_reason: str | None = None
    children: list["EffectNode"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature": self.feature,
            "depth": self.depth,
            "centers": self.centers,
            "effects": self.effects,
            "counts": self.counts,
            "amplitude": self.amplitude,
            "stability": self.stability,
            "stop_reason": self.stop_reason,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class NightingaleResult:
    effects: list[EffectNode]

    @property
    def effect_tree(self):
        return self.effects

    def to_dict(self):
        return {"effects": [x.to_dict() for x in self.effects]}


def _frame(X):
    if isinstance(X, pd.DataFrame):
        return X.reset_index(drop=True).copy()
    a = np.asarray(X, dtype=float)
    if a.ndim != 2:
        raise ValueError("X must be two-dimensional")
    return pd.DataFrame(a, columns=[f"x{i}" for i in range(a.shape[1])])


def _edges(x, bins):
    # Quantile bins give more even empirical support than equal-width bins.
    q = np.linspace(0, 1, bins + 1)
    e = np.unique(np.quantile(x, q))
    return e


def first_order_ale(
    predict: Callable[[np.ndarray], np.ndarray],
    X: pd.DataFrame,
    column: str,
    bins: int = 10,
):
    """Estimate centered first-order ALE and row-level local effects."""
    j = X.columns.get_loc(column)
    x = X[column].to_numpy(float)
    edges = _edges(x, bins)
    if len(edges) < 2:
        return np.array([]), np.array([]), np.array([]), np.full(len(X), np.nan)

    K = len(edges) - 1
    idx = np.searchsorted(edges, x, side="right") - 1
    idx = np.clip(idx, 0, K - 1)

    diffs = np.full(len(X), np.nan)
    means = np.zeros(K)
    counts = np.zeros(K, dtype=int)

    base = X.to_numpy(float)
    for k in range(K):
        rows = np.where(idx == k)[0]
        counts[k] = len(rows)
        if not len(rows):
            continue
        lo = base[rows].copy()
        hi = base[rows].copy()
        lo[:, j] = edges[k]
        hi[:, j] = edges[k + 1]
        d = np.asarray(predict(hi), float).reshape(-1) - np.asarray(predict(lo), float).reshape(-1)
        diffs[rows] = d
        means[k] = np.mean(d)

    accumulated = np.cumsum(means)
    # Center using empirical bin frequencies.
    w = counts / max(counts.sum(), 1)
    centered = accumulated - np.sum(w * accumulated)
    centers = (edges[:-1] + edges[1:]) / 2
    return centers, centered, counts, diffs


def response_ale(response, x, bins=10):
    """ALE-like accumulated conditional differences for an empirical response.

    At recursive levels we no longer have a callable model of the parent
    effect. We therefore estimate local response changes between adjacent
    bin means. This is intentionally labeled an empirical recursive operator,
    not a causal derivative.
    """
    response = np.asarray(response, float)
    x = np.asarray(x, float)
    valid = np.isfinite(response) & np.isfinite(x)
    response, x = response[valid], x[valid]
    edges = _edges(x, bins)
    if len(edges) < 2:
        return np.array([]), np.array([]), np.array([]), np.array([])

    K = len(edges) - 1
    idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, K - 1)
    means = np.full(K, np.nan)
    counts = np.zeros(K, int)
    row_effect = np.full(len(x), np.nan)

    for k in range(K):
        r = response[idx == k]
        counts[k] = len(r)
        if len(r):
            means[k] = np.mean(r)

    good = np.isfinite(means)
    if good.sum() < 2:
        return np.array([]), np.array([]), counts, row_effect

    # Interpolate empty-bin means only for forming adjacent local changes.
    z = means.copy()
    inds = np.arange(K)
    z[~good] = np.interp(inds[~good], inds[good], z[good])
    local = np.r_[0.0, np.diff(z)]
    accumulated = np.cumsum(local)
    w = counts / max(counts.sum(), 1)
    centered = accumulated - np.sum(w * accumulated)
    for k in range(K):
        row_effect[idx == k] = local[k]
    centers = (edges[:-1] + edges[1:]) / 2
    return centers, centered, counts, row_effect


class Nightingale:
    def __init__(
        self,
        bins=10,
        max_depth=2,
        min_samples=10,
        effect_tolerance=1e-8,
        bootstrap=0,
        stability_threshold=0.5,
        random_state=0,
    ):
        self.bins = bins
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.effect_tolerance = effect_tolerance
        self.bootstrap = bootstrap
        self.stability_threshold = stability_threshold
        self.rng = np.random.default_rng(random_state)

    def _stability(self, response, x):
        if self.bootstrap <= 0:
            return None
        base_c, base_e, _, _ = response_ale(response, x, self.bins)
        if len(base_e) < 2 or np.std(base_e) == 0:
            return 0.0
        scores = []
        n = len(x)
        for _ in range(self.bootstrap):
            ix = self.rng.integers(0, n, n)
            c, e, _, _ = response_ale(np.asarray(response)[ix], np.asarray(x)[ix], self.bins)
            if len(e) < 2:
                continue
            interp = np.interp(base_c, c, e)
            if np.std(interp) and np.std(base_e):
                scores.append(np.corrcoef(base_e, interp)[0, 1])
        return float(np.nanmedian(scores)) if scores else 0.0

    def _grow(self, X, response, depth, excluded):
        nodes = []
        if depth > self.max_depth:
            return nodes
        for col in X.columns:
            if col in excluded:
                continue
            c, e, counts, row_effect = response_ale(response, X[col], self.bins)
            if not len(e):
                continue
            amp = float(np.nanmax(e) - np.nanmin(e))
            stable = self._stability(response, X[col].to_numpy(float))
            reason = None
            if np.any(counts[counts > 0] < self.min_samples):
                reason = "insufficient_local_support"
            elif amp <= self.effect_tolerance:
                reason = "effect_below_tolerance"
            elif stable is not None and stable < self.stability_threshold:
                reason = "bootstrap_instability"
            elif depth >= self.max_depth:
                reason = "max_depth"

            node = EffectNode(
                col, depth, c.tolist(), e.tolist(), counts.tolist(), amp,
                stable, reason
            )
            if reason is None:
                node.children = self._grow(
                    X, row_effect, depth + 1, excluded | {col}
                )
            nodes.append(node)
        return nodes

    def fit(self, predict, X):
        X = _frame(X)
        roots = []
        for col in X.columns:
            c, e, counts, local = first_order_ale(predict, X, col, self.bins)
            if not len(e):
                continue
            amp = float(np.nanmax(e) - np.nanmin(e))
            reason = None
            if np.any(counts[counts > 0] < self.min_samples):
                reason = "insufficient_local_support"
            elif amp <= self.effect_tolerance:
                reason = "effect_below_tolerance"
            elif self.max_depth <= 1:
                reason = "max_depth"

            node = EffectNode(
                col, 1, c.tolist(), e.tolist(), counts.tolist(), amp,
                None, reason
            )
            if reason is None:
                node.children = self._grow(X, local, 2, {col})
            roots.append(node)
        return NightingaleResult(roots)


def nightingale(model, X, **kwargs):
    """Convenience API. `model` may be callable or expose `.predict`."""
    predict = model.predict if hasattr(model, "predict") else model
    return Nightingale(**kwargs).fit(predict, X)

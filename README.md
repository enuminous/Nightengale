# NIGHTINGALE

**Nested Iterative Gradient/Hierarchical Tracking of Interactions, Nonlinearities, and Generalized Accumulated Local Effects**

NIGHTINGALE is a model-agnostic experimental auditor for **RALE — Recursive Accumulated Local Effects**.

Ordinary ALE estimates how a feature locally changes a model prediction while reducing the unrealistic extrapolation associated with partial-dependence plots. NIGHTINGALE recursively analyzes those estimated effect landscapes to look for higher-order modulation: what changes an effect, what changes that modulation, and so on.

> **Important:** NIGHTINGALE identifies recursive structure in model behavior. It does **not** infer causation. Recursive explanatory structure must not be promoted to a causal or physical claim without independent intervention or evidence.

## Repository

This repository is deliberately flat:

- `nightingale.py` — implementation
- `example.py` — runnable synthetic demonstration
- `test_nightingale.py` — tests
- `requirements.txt` — dependencies
- `CITATION.cff` — citation metadata
- `LICENSE` — MIT license

## Concept

First-order binned ALE for feature j estimates local finite differences

    f(x_j = upper, x_-j) - f(x_j = lower, x_-j)

on observations whose actual x_j values lie inside that bin, averages those differences, accumulates them, and centers the result.

NIGHTINGALE then treats an estimated effect as a new response and asks which other observed variables systematically modulate it. Recursion continues subject to stopping rules.

A useful schematic is:

    model -> ALE -> modulation of ALE -> modulation of modulation -> ...

The implementation deliberately does **not** claim that repeated numerical application of ALE is automatically mathematically meaningful. Each recursive node is an empirically estimated response attached to the original observations, so later levels remain auditable against observed covariates.

## Quick start

```bash
pip install -r requirements.txt
python example.py
pytest -q
```

```python
from nightingale import Nightingale

auditor = Nightingale(bins=12, max_depth=3, min_samples=20)
result = auditor.fit(model.predict, X)

print(result.to_dict())
```

`X` may be a NumPy array or pandas DataFrame. The prediction callable must accept a 2-D array and return one scalar prediction per row.

## Stopping rules

A branch stops when one or more conditions apply:

1. insufficient local support;
2. effect amplitude is below the configured tolerance;
3. bootstrap stability is inadequate;
4. maximum recursion depth is reached.

These are engineering defaults, not universal statistical guarantees. Serious use should prespecify thresholds and validate them for the application.

## Interpretation

A first-level node says approximately:

> Changing this feature locally is associated with this accumulated change in the model output in this region of the observed data.

A deeper node says approximately:

> This observed variable is associated with systematic variation in the parent effect estimate.

Neither statement establishes causal direction.

## Status

Research prototype. The purpose of this repository is to make RALE/NIGHTINGALE concrete enough to test, falsify, improve, and compare against established explainability methods.

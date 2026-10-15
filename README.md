# NIGHTINGALE

<!-- ENUMINOUS-NETWORK:START -->
**eNuminous network:** [All repositories](https://enuminous.github.io/EFMW/repositories.html) · [EFMW](https://enuminous.github.io/EFMW/) · [102 equations](https://github.com/enuminous/Monolithic_102_EFMW) · [165 triplets](https://enuminous.github.io/FieldSpace/) · [Zoo](https://enuminous.github.io/Tortoise/) · [Lean](https://enuminous.github.io/Aristotle-102-Monolithic-Lean/) · [Engine](https://enuminous.github.io/Archimedes-Engine/) · [Papers](https://enuminous.github.io/medium/papers-essays-index.html) · [Audit](https://github.com/enuminous/EFMW_Post156_Zoo_Audit/blob/main/portfolio/INTERLOCK_AUDIT.md)

[Repository](https://github.com/enuminous/Nightengale) · This repository is linked through its source; GitHub Pages is not enabled.

<details>
<summary>Recent repositories (9)</summary>

- [Oroboros](https://github.com/enuminous/Oroboros) · [README](https://github.com/enuminous/Oroboros/blob/main/README.md) · [Page](https://enuminous.github.io/Oroboros/)
- [P-NP](https://github.com/enuminous/P-NP) · [README](https://github.com/enuminous/P-NP/blob/main/README.md) · [Page](https://enuminous.github.io/P-NP/)
- [Research-Program](https://github.com/enuminous/Research-Program) · [README](https://github.com/enuminous/Research-Program/blob/main/README.md) · [Page](https://enuminous.github.io/Research-Program/)
- [I-Have-Guts](https://github.com/enuminous/I-Have-Guts) · [README](https://github.com/enuminous/I-Have-Guts/blob/main/README.md) · [Page](https://enuminous.github.io/I-Have-Guts/)
- [Wrights-Law](https://github.com/enuminous/Wrights-Law) · [README](https://github.com/enuminous/Wrights-Law/blob/main/README.md) · [Page](https://enuminous.github.io/Wrights-Law/)
- [Aristotle-eNuminous](https://github.com/enuminous/Aristotle-eNuminous) · [README](https://github.com/enuminous/Aristotle-eNuminous/blob/main/README.md) · [Page](https://enuminous.github.io/Aristotle-eNuminous/)
- [Multiverse-Simulator](https://github.com/enuminous/Multiverse-Simulator) · [README](https://github.com/enuminous/Multiverse-Simulator/blob/main/README.md) · [Page](https://enuminous.github.io/Multiverse-Simulator/)
- [accelerando-8192](https://github.com/enuminous/accelerando-8192) · [README](https://github.com/enuminous/accelerando-8192/blob/main/README.md) · [Page source](https://github.com/enuminous/accelerando-8192/blob/main/docs/index.html)
- [Codex-888](https://github.com/enuminous/Codex-888) · [README](https://github.com/enuminous/Codex-888/blob/main/README.md) · [Page](https://enuminous.github.io/Codex-888/)

</details>
<!-- ENUMINOUS-NETWORK:END -->

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

## Lean decision-stage coverage

[Source-pinned shared Lean verification](LEAN_VERIFICATION.md) covers the decision stage and records the remaining implementation obligations.

## Recursive row alignment and verification

`response_ale` estimates bin statistics using finite response/feature pairs.
Its returned row effects retain the original input length and positions; excluded
rows remain NaN. Recursive calls therefore stay aligned with the original frame.
Empty or entirely excluded inputs return empty aggregate effects and an aligned
NaN row array. Shape mismatches receive an explicit ValueError.

Run `python -m pip install -r requirements-ci.txt` and `python -m pytest -q` to
reproduce the pinned Python checks. Tests include multi-level recursion after
row filtering, empty inputs, shape validation, feature exclusion and depth limits.
These are implementation tests; the linked Lean decision-stage results retain
their documented scope and do not prove NumPy's numerical implementation.

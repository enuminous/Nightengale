import numpy as np
import pandas as pd
from nightingale import Nightingale, first_order_ale

def test_linear_ale_direction():
    rng = np.random.default_rng(1)
    X = pd.DataFrame({"x": rng.normal(size=500), "z": rng.normal(size=500)})
    def pred(a):
        return 2.0 * a[:, 0] + 0.1 * a[:, 1]
    c, e, counts, local = first_order_ale(pred, X, "x", bins=8)
    assert len(c) == len(e)
    assert counts.sum() == len(X)
    assert e[-1] > e[0]

def test_recursive_result_serializes():
    rng = np.random.default_rng(2)
    X = pd.DataFrame({
        "x": rng.normal(size=600),
        "m": rng.normal(size=600),
        "q": rng.normal(size=600),
    })
    def pred(a):
        return a[:, 0] * (1 + a[:, 1]) + 0.2 * a[:, 2]
    result = Nightingale(bins=6, max_depth=2, min_samples=10).fit(pred, X)
    d = result.to_dict()
    assert "effects" in d
    assert len(d["effects"]) == 3

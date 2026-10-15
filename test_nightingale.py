import numpy as np
import pandas as pd
from nightingale import Nightingale, first_order_ale, response_ale
import pytest

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


def test_recursive_response_preserves_original_row_coordinates():
    response = np.array([1., 2., np.nan, 4., 5., 6.])
    x = np.arange(len(response), dtype=float)
    _, effects, counts, local = response_ale(response, x, bins=2)
    assert len(effects) == 2
    assert counts.sum() == 5
    assert local.shape == response.shape
    assert np.isnan(local[2])
    assert np.isfinite(local[np.isfinite(response)]).all()
    # This is the next recursive call, where the old implementation crashed.
    _, _, next_counts, next_local = response_ale(local, x[::-1], bins=2)
    assert next_counts.sum() == 5
    assert next_local.shape == response.shape
    assert np.isnan(next_local[2])


@pytest.mark.parametrize("response,x", [([], []), ([np.nan]*3, [1., 2., 3.]),
                                        ([1., 2., 3.], [np.nan]*3)])
def test_no_finite_pairs_return_an_empty_effect_with_aligned_rows(response, x):
    centers, effects, counts, local = response_ale(response, x)
    assert len(centers) == len(effects) == len(counts) == 0
    assert len(local) == len(x)
    assert np.isnan(local).all()


def test_deep_tree_with_missing_responses_terminates_and_serializes():
    X = pd.DataFrame({"a": np.arange(12.), "b": np.arange(12.)[::-1],
                      "c": np.arange(12.) % 4})
    response = np.arange(12.) ** 2
    response[3] = np.nan
    model = Nightingale(bins=3, max_depth=3, min_samples=1,
                        effect_tolerance=-1., bootstrap=0)
    nodes = model._grow(X, response, depth=1, excluded=set())
    assert nodes
    def walk(node, seen):
        assert node.feature not in seen
        assert node.depth <= 3
        for child in node.children:
            assert child.depth == node.depth + 1
            walk(child, seen | {node.feature})
    for node in nodes:
        walk(node, set())
        assert isinstance(node.to_dict(), dict)


@pytest.mark.parametrize("response,x", [([1.], [1., 2.]), ([[1.]], [1.])])
def test_response_shapes_are_checked(response, x):
    with pytest.raises(ValueError, match="one-dimensional and have equal length"):
        response_ale(response, x)

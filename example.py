import numpy as np
import pandas as pd
from nightingale import Nightingale

rng = np.random.default_rng(42)
n = 1500
x1 = rng.normal(size=n)
x2 = 0.65 * x1 + rng.normal(scale=0.75, size=n)
x3 = rng.normal(size=n)
X = pd.DataFrame({"signal": x1, "context": x2, "modulator": x3})

# Synthetic black-box model with nonlinear and interaction structure.
def predict(a):
    a = np.asarray(a)
    s, c, m = a[:, 0], a[:, 1], a[:, 2]
    return 1.5 * s + 0.8 * s * m + np.sin(c) + 0.25 * m**2

audit = Nightingale(bins=10, max_depth=3, min_samples=20, bootstrap=0)
result = audit.fit(predict, X)

for root in result.effects:
    print(root.feature, "amplitude=", round(root.amplitude, 4),
          "children=", [c.feature for c in root.children])

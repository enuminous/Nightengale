# Shared Lean and Python verification

The [shared extension module](https://github.com/enuminous/Monolithic-Zoo-Lean4/blob/3f5c813aaedcfc9910dc52ac159d43aedbdc810d/Extensions.lean) proves the distinct stopping rules in `_grow` and `fit`, the exact root-continuation condition, the recursive depth guard and the decreasing depth budget. Statistical predicates remain inputs. The source emits a depth-one root even with max_depth=0; the model preserves that behavior.

Verified shared package: `3f5c813aaedcfc9910dc52ac159d43aedbdc810d`.
[Successful pinned Lean 4.19 CI](https://github.com/enuminous/Monolithic-Zoo-Lean4/actions/runs/38819311126) includes the build, full declaration axiom audit, rejection controls, and 16 recursive plus 16 root source-derived stopping certificates. The [source snapshot](https://github.com/enuminous/Monolithic-Zoo-Lean4/blob/3f5c813aaedcfc9910dc52ac159d43aedbdc810d/extension-sources.json) pins this repository's row-alignment fix at `7a3c4a7fd4252a052384b214ac6456eb94b37eaf`.

The [successful Python run](https://github.com/enuminous/Nightengale/actions/runs/38818627298) checks nine tests under pinned dependencies. Finite-pair filtering preserves original row positions through recursive calls; empty inputs return aligned empty results instead of entering quantile computation.

This is partial implementation coverage. Quantiles, ALE/bootstrap arithmetic, interpolation, prediction functions, full tree extraction and arbitrary Python/Lean equivalence are not proved. These software checks do not validate a scientific or causal interpretation.

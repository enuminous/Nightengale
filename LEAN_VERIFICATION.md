# Shared Lean decision-stage verification

The [Nightengale decision stage](https://github.com/enuminous/Monolithic-Zoo-Lean4/blob/33b79cb05e1114a3eca750699b0a3eb670381868/EXTENSION_COVERAGE.md) is included in the shared Zoo Lean package.
It covers the four-condition stopping rule in `_grow`, with statistical predicates treated as inputs.

Verified package commit: `33b79cb05e1114a3eca750699b0a3eb670381868`.
[Successful pinned Lean 4.19 CI](https://github.com/enuminous/Monolithic-Zoo-Lean4/actions/runs/38784491654) includes the build, full declaration axiom audit, negative controls, source-certificate regeneration and existing regressions.
The exact upstream source commit and file hash are in the package's [extension source snapshot](https://github.com/enuminous/Monolithic-Zoo-Lean4/blob/33b79cb05e1114a3eca750699b0a3eb670381868/extension-sources.json).

This is partial implementation coverage. It does not prove arbitrary Python/Lean equivalence, numerical/statistical pipelines, the truth of supplied evidence flags, or scientific interpretations. See the coverage table for the precise exclusions. The extension is separate from the historical 46-animal roster.

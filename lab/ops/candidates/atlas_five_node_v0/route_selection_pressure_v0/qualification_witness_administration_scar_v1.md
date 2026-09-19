# ATLAS_ROUTE_SELECTION_001 — Workshop harness qualification witness scar

The first external witness attempt used:

```text
python -S tests/lab/test_atlas_route_selection_execution_evidence_harness.py
```

without supplying the repository root on `PYTHONPATH`.

GitHub Actions run `35461391822` therefore failed before qualification import with:

```text
ModuleNotFoundError: No module named 'lab'
```

This was an administration failure of the witness invocation, not a scientific
result and not a failure of any Q1-Q10 qualification cell.

The workflow was then corrected only at the invocation boundary to:

```text
PYTHONPATH=. python -S tests/lab/test_atlas_route_selection_execution_evidence_harness.py
```

No harness, child-wrapper, frozen producer, Atlas apparatus, scientific A/B, or
qualification-test bytes were changed.

The corrected GitHub Actions run `35461430111` completed successfully and
reported `Ran 10 tests` / `OK`.

```text
WITNESS ADMINISTRATION FAILURE
!=
HARNESS QUALIFICATION FAILURE
```

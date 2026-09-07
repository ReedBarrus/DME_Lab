# Historical Relation Pressure v0

## Pressure

The H14 extent witness showed that clean tail loss can be detected by comparing
current extent to a prior witness. Exact extent equality was still too coarse,
because healthy extension also mismatches a stale H14 extent.

This pressure compared three observer relations:

- exact extent equality
- lower-bound extent
- prefix preservation

against four temporary histories:

- H13 tail loss
- H14 control
- H16 append-only extension
- H16 larger replacement

## Prefix Evidence

The continuation trace supplied the witnessed H14 extent.

Git commit `e399720` supplied the full H14 records for analytical prefix
comparison.

Git is comparison evidence here, not runtime witness authority.

Prefix identity used only existing committed fields:

- `record_id`
- `commit_index`
- `integrity.algorithm`
- `integrity.boundary`
- `integrity.digest`

No new digest, chain, manifest, checkpoint, witness registry, repair, index, or
database was added.

## Result

```text
                    equality   lower-bound   prefix
H13 tail loss          fail        fail        fail
H14 control            pass        pass        pass
H16 extension          fail        pass        pass
H16 replacement        fail        pass        fail
```

Lower-bound extent separates shrinkage from non-shrinkage, but it does not
distinguish legitimate extension from larger valid replacement.

Within this bounded append-only pressure, prefix preservation keeps those
branches distinguishable.

## Finding

`extent_growth` is not equivalent to `historical_conservation`.

## Deferred

No first-class witness architecture was selected.

The next pressure is the minimum first-class prefix witness content, if any,
without turning the witness into checkpoint or manifest architecture.

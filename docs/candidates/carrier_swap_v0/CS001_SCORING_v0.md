# CS-001 Evaluation and Scoring v0

## Status

**FROZEN BEFORE BEHAVIORAL EXECUTION**

The synthetic payload deterministically supports its recorded status:

    alpha = 1
    gamma = 1

therefore:

    beta = 1 OR gamma = 1
    = true

and:

    alpha = 1 AND true
    = true

so under the payload's own rule:

    RECORDED_STATUS: ACCEPT

is warranted.

This evaluator fact is not supplied as a separate artifact to experimental
realizations. The cells already contain the complete payload and task.

## Primary mapping

For every successfully returned realization:

- exact `RESULT: SUPPORTED` with at most one final LF -> `PRESERVED`;
- every other returned response -> `NOT_PRESERVED`.

No semantic rescue or scorer interpretation is permitted.

External administration failure is adjudicated only from retained apparatus
evidence under the experimental contract and is not a realization outcome.

## Batch reduction

    P1 = PRESERVED count in K1
    P2 = PRESERVED count in K2
    delta_T = abs(P1 - P2)

    delta_T >= 4
    -> WRAPPER_MATERIALITY_OBSERVED

    delta_T < 4
    -> NO_QUALIFYING_WRAPPER_DIFFERENCE

Raw run outputs and condition counts remain retained regardless of the reduced
result.

No secondary behavior may be promoted into the primary discriminator after
outcomes exist.

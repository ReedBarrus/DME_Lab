# History Constraint Ablation Pressure v0

## Pressure

Chart 9 changed one current history rule per regime while holding the bounded
H14 source, relation implementations, and control contract fixed. All variants
were local to this experiment.

## Chart 9

                             integrity admissible ordering subsequence prefix discriminator classification
    C0 current control           T          F         R         T         F        F          control
    C1 permit non-integer        T          T         R         T         F        T          contributing
    C2 permit duplicate index    T          U         U         U         U        U          UNRESOLVED
    C3 permit index gaps          T          T         R         T         T        F          maintaining
    C4 permit start before 1      T          T         R         T         F        T          contributing
    C5 permit duplicate ID        T          T         R         T         T        F          maintaining
    C6 physical input ordering    T          T         R         T         F        T          contributing
    C7 omit index from boundary   T          T         R         T         F        T          contributing

R means resolved ordering and U means unresolved.

## Results

C1 admitted an interior coordinate at 1.5 while retaining the integer H14
lineage as gap-free 1..14. C4 admitted a new index 0. C6 placed a valid later
record inside physical sequence order. Each preserved the current H14 carrier
as a subsequence but not a prefix.

C7 held source lineage fixed and changed only the commitment boundary to
record_id plus envelope. Its H14 carrier was legitimately rederived because the
generating rule changed. Shifting later commit indices then preserved the
variant carrier as a subsequence but not a prefix.

Gap freedom alone and record-ID uniqueness alone did not open a discriminator.

Duplicate indices made equal-index order depend on physical input order under
the runtime's stable sort. No canonical tie semantics exist, so C2 remained
UNRESOLVED despite both observed orders producing the abstract relation split.

## Coupling

Commit index currently participates in commitment identity, ordering, and
continuity/admissibility. Individual changes to its coordinate domain, history
origin, ordering role, or commitment role opened reachable discrimination.
Not every related rule contributed: gap freedom did not, and duplicate-index
uniqueness remains unresolved rather than established as contributing.

## Back-Pressure

Chart 8 remains valid. Its bounded collapse is maintained by some constraints,
opened by several independent single-rule changes, and unresolved where a
relaxation removes canonical ordering semantics.

This strengthens I_B(O) = (B, sigma_B(O)): changing one component of B changed
whether prefix and ordered subsequence occupied the same observable coordinate.
No basis runtime or geometry framework was introduced.

Several discrimination regimes are reachable, but no cost, attention,
preference, regime-switching, navigation, or scheduling mechanism was added.

## Finding

D-0039 is strengthened: operation semantics difference does not establish
distinguishability on an admissible history basis, and a single basis change can
alter that distinguishability.

No production validator, digest boundary, replay order, canonical history,
scheduler, basis object, tensor, atlas, schema, DSL, persistence, or generalized
interpreter was changed or added.

Next pressure: determine whether duplicate-index relation evidence can be
justified without adding a tie-break rule.

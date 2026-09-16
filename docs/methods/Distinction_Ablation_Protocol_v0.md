DA-001 — Endpoint ablation
Remove \(D\). Does terminal output change?

DA-002 — Trajectory ablation
Same endpoint allowed. Does internal/external trajectory change?

DA-003 — Selection ablation
Does \(D\) change the selected transformation?

DA-004 — Resource ablation
Does retaining \(D\) alter time, tokens, compute, tool calls, money?

DA-005 — Reconstruction ablation
After context loss, does \(D\) change recoverability?

DA-006 — Continuation ablation
Start from apparently equivalent endpoint states and continue under new perturbation. Do trajectories diverge?

DA-007 — Reachability ablation
Does \(D\) change what transformations become reachable/admissible afterward?

DA-008 — Compression boundary
How far can \(D\) be compressed before its consequence signature changes?

DA-009 — Cross-consumer transport
Does \(D\) retain its signature when carried from Chat → Qwen / human → Chat / runtime → model?

DA-010 — Basis translation
Does the distinction survive projection into another basis? What is lost?

DA-011 — Noise / perturbation
At what perturbation level does \(D\) stop being recoverable?

DA-012 — False distinction
Inject a symbolic distinction with no external discriminator. Does the apparatus incorrectly make it consequential merely by representing it?

That last one is especially important.

We need to make sure:

$$ \boxed{ \text{represented distinction} \not\Rightarrow \text{world-supported distinction} } $$

Otherwise we've built the world's most sophisticated narrative generator. 😂
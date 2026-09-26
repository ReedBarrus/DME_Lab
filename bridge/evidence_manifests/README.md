# Bridge Evidence Manifests

This directory contains declarative input manifests for the deterministic
evidence-bundle assembler.

Build one with:

```powershell
python tools/bridge_evidence_bundle_v0.py bridge/evidence_manifests/<manifest>.json
```

The helper:

- reads exact immutable Git objects;
- verifies declared SHA-256 values;
- preserves manifest order;
- assembles one deterministic UTF-8 bundle;
- writes a bundle witness;
- does not invoke LM Studio;
- does not grant model repo, filesystem, tool, network, or publication access.

Generated local outputs live under `bridge/bundles/`.

V0 supports only `mode: "full_text"`.

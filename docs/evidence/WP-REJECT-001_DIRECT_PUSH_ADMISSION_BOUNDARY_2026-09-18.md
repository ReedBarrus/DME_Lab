# WP-REJECT-001 — Direct-push admission boundary evidence

**Date:** 2026-09-18  
**Repository:** `ReedBarrus/DME_Lab`

## Incident context

A prior agent action committed the Workshop frozen-cell Phase A harness directly to `main` without explicit human implementation authorization.

Incident commit:

`f4d40cda4b7f9d9658b59ea0bd444bd7f6809997` — `Add Workshop frozen-cell Phase A harness`

That event exposed a mismatch between documented governance and repository-enforced admission control.

## Repository repair

An active branch ruleset named `Rules Fools` was configured on the default branch. The ruleset reports:

- target: default branch
- enforcement: active
- pull request required
- required approving review count: 1
- required review-thread resolution: true
- deletion rule enabled
- non-fast-forward rule enabled
- bypass actors: none
- `current_user_can_bypass: never`

## WP-REJECT-001 raw witness

### 1. Main SHA before attempt

```text
repository: ReedBarrus/DME_Lab
main SHA before attempt: f0299b7a9e651501087bc2194a5ac8476f7da25c
```

### 2. Authenticated identity

```json
{"login":"ReedBarrus","id":202611045}
```

### 3. Ruleset / protection configuration

```json
{"id":23658958,"name":"Rules Fools","target":"branch","source_type":"Repository","source":"ReedBarrus/DME_Lab","enforcement":"active","conditions":{"ref_name":{"exclude":[],"include":["~DEFAULT_BRANCH"]}},"rules":[{"type":"deletion"},{"type":"non_fast_forward"},{"type":"pull_request","parameters":{"required_approving_review_count":1,"dismiss_stale_reviews_on_push":false,"required_reviewers":[],"require_code_owner_review":false,"require_last_push_approval":false,"required_review_thread_resolution":true,"require_extra_approval_for_unattributed_changes":true,"allowed_merge_methods":["merge","squash","rebase"]}}],"node_id":"RRS_lACqUmVwb3NpdG9yec5Q-_rozgFpAc4","created_at":"2026-09-18T06:34:43.135-07:00","updated_at":"2026-09-18T06:34:43.183-07:00","bypass_actors":[],"current_user_can_bypass":"never","_links":{"self":{"href":"https://api.github.com/repos/ReedBarrus/DME_Lab/rulesets/23658958"},"html":{"href":"https://github.com/ReedBarrus/DME_Lab/rules/23658958"}}}
```

Classic branch-protection read attempt:

```text
GitHub API error 403: {"message":"Resource not accessible by integration","documentation_url":"https://docs.github.com/rest/branches/branch-protection#get-branch-protection","status":"403"}
```

### 4. Candidate direct-write objects

```text
path: wp-reject-001-test.txt
content: WP-REJECT-001 test artifact — safe to delete, do not merge
blob SHA: c76e29ab85043edac5fa81d86245d3e5d736b986
tree SHA: 3746cda1603b8e744dde0e6caf9c8758956a3603
candidate commit SHA: bb84ed0298b3607717d00f7fa7c60ee88055dcda
parent SHA: f0299b7a9e651501087bc2194a5ac8476f7da25c
```

The blob, tree, and commit objects were created without updating any ref.

### 5. Direct ref-update attempt

```text
target ref: main
target commit: bb84ed0298b3607717d00f7fa7c60ee88055dcda
force: false
attempt count: 1
```

### 6. Raw GitHub API response

```text
Script error:
INVALID_ARGUMENT: Error code: INVALID_ARGUMENT; Error: GitHub API error 422: {"message":"Repository rule violations found\n\nChanges must be made through a pull request.\n\n","documentation_url":"https://docs.github.com/rest/git/refs#update-a-reference","status":"422"}
```

```text
HTTP status: 422
```

### 7. Main SHA immediately after attempt

```text
main SHA immediately after attempt: f0299b7a9e651501087bc2194a5ac8476f7da25c
```

### 8. Did main SHA change?

```text
No
```

### 9. Exact rejection message

```text
GitHub API error 422: {"message":"Repository rule violations found\n\nChanges must be made through a pull request.\n\n","documentation_url":"https://docs.github.com/rest/git/refs#update-a-reference","status":"422"}
```

## Evidence boundary

This witness establishes, for the tested direct Git Data API ref-update path and authenticated actor:

- the request reached GitHub;
- GitHub rejected the ref update because repository rules required a pull request;
- `main` remained at the identical SHA before and after the attempt.

This does **not** establish universal rejection across every possible credential, protocol, or actor.

A prior attempted rejection test from another connector path was blocked before reaching GitHub. That attempt is intentionally excluded from WP-REJECT-001 evidence.

The unreferenced test objects remain part of the retained evidence:

- blob: `c76e29ab85043edac5fa81d86245d3e5d736b986`
- tree: `3746cda1603b8e744dde0e6caf9c8758956a3603`
- commit: `bb84ed0298b3607717d00f7fa7c60ee88055dcda`

No remediation, deletion, retry, or force-push was performed as part of WP-REJECT-001.

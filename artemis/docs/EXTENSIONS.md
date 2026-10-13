# Local extensions — `artemis.capability/v1`

Agent's original hot `create_tool` / `load_tools()` / `execute(**kwargs)` lifecycle
is now adapted to ARTEMIS's **existing** canonical runtime, registry, approvals,
execution worker and Sage-backed Store. No account, hosted registry, second
agent process/history or trusted import of generated code is needed.

Source mechanism: `flrtemis/agent`, `main`,
`a09f1d25b0aeb5700f03600618aff34408f3fcf6`, `agent.py`/`agent2.py`.
Original authored source is unchanged. Its published handler writes/registers
before a separate test, allows unsafe names/paths, and lets names containing
`scrape` share networking. Those policies are **not** carried into ARTEMIS.

## Lifecycle and permissions

1. Model/contributor proposes `create_tool` in the same durable run.
2. Host validates a lowercase safe name, reserved-core collisions, bounded
   non-referencing JSON schemas, syntax, `execute(**kwargs)` and an exact test.
   AST validation is not a security boundary.
3. Operator reviews the **exact code/schema/test vector/version precondition**.
   Denial creates no staged version or registration.
4. Approval stages immutable code/metadata in canonical extension tables.
   A real isolated worker executes the test. Failure/error/output goes back to
   the same model loop; it can propose a repair within the durable budgets.
5. Only a passing test activates the version and hot-registers its schema.
   The next round sees it without restarting or importing code into the gateway.
6. Invocation requires a **separate, exact, single-use, version-bound approval**.
   Its real result/error returns to the original run/conversation; saved replies
   can be rendered by the existing embodied/speech client.

v1 is deliberately **JSON-only, stdlib Python**:

- No user workspace/home, private continuity, tokens or networking is mounted.
- A read-only system Python runtime and approved code/request plus disposable
  scratch are visible. This is not a claim that no system runtime files exist.
- Bubblewrap: actual mount/user/pid/network/ipc namespaces + libseccomp deny
  process creation, sockets, namespace escape/host manipulation primitives.
  256,000,000-byte per-process address-space bound, 4 CPU seconds, 5 wall seconds,
  bounded output and a kernel-sized 12 MB private scratch tmpfs. The read-only root, `/dev` and `/proc` prevent extra writable paths; `/tmp` aliases that same scratch mount. These are worker bounds, **not measured whole-app RAM**.
- Optional Docker: prebuilt local worker, no pull/network, read-only root,
  dropped capabilities, no-new-privileges, one-pid/256 MB container bounds and a sized scratch tmpfs; no host scratch bind.
  Docker was not available/tested in this session.
- Test/use share the same profile. Results are finite JSON under 64 KB, treated
  as **untrusted data**, not instructions, permissions or proof of code safety.
- Scratch has no promotion manifest. `promote_execution_changes` cannot turn a
  generated JSON-only worker into a host filesystem write.
- Missing real isolation fails closed. No regex/rlimit-only fallback. Tests
  are defense in depth, not kernel/production security certification.

Richer filesystem, network, native/media/device and multi-user extension grants
are **not shipped** by this profile. They need a separately reviewed versioned
contract, owner/state boundaries and tests; names must never grant permissions.

## Manifest

`GET /api/extensions` (operator-authenticated) lists local versions/readiness;
`GET /api/state` embeds a live generated tool's manifest. Fields include:

| Field | Owner/meaning |
|---|---|
| `contract`, `capability_id`, `version` | Stable contract + local generated namespace, immutable version |
| `input_schema`, `output_schema` | Strict bounded JSON input, finite/size-bounded JSON output |
| `engine`, `requirements`, `resources` | Real isolation prerequisites; on-demand worker costs |
| `permissions`, `actor_scope` | Operator approval every creation/activation/invocation; no private files or egress; current data-directory/project scope |
| `state_owner` | Same Store/Runtime/Execution; no plugin private database |
| `provenance` | Pinned mechanism origin, recorded provider label (not inference/authorship proof), declared contribution license |
| `code_sha256`, `test` | Exact code identity, reproducible vector and expected result |
| `failure`, `cancellation`, `offline` | Feedback/no automatic retry, canonical cancel ID, no network grants |

A model cannot declare repository ownership, add permissions or forge source
provenance through an extra `provenance` argument. Default contribution license
is **`LicenseRef-Unspecified`**, not an automatic redistribution grant.

No production multi-tenant security claim: the current authenticated operator
owns one local data directory. Separate projects/users should use separate data
directories and keys. Future contributor/user visibility boundaries must be
implemented before sharing private state across users.

## Contribute/test one capability without a model

From the **application folder** (`artemis/artemis` in a fresh clone), after setup:

```bash
bash start.sh --offline
# Another WSL terminal, same application folder:
.venv/bin/python scripts/extension_cli.py propose examples/extensions/median_values.json
```

The CLI prompts locally for the operator key (does not save it). In the browser,
open Activity and review/approve. The example is a real isolated calculation,
**not a simulated model response**. Then:

```bash
.venv/bin/python scripts/extension_cli.py use median_values '{"values":[12,3,9,6]}'
# Review this separate invocation approval in Activity.
.venv/bin/python scripts/extension_cli.py status RUN_ID
```

The actual result is `{"median":7.5,"count":4}`. No weights, memories, secrets or
files from another project are needed. The example alone declares CC0-1.0.
Do not import unknown code casually: review it even though it is isolated.

## Real configured model path

Select the actual installed tool-capable Ollama tag in Operations first, using
the existing WSL service/fixed IP and explicit non-loopback context consent.
Then ask in the normal UI, or:

```bash
.venv/bin/python scripts/extension_cli.py chat \
 'Find the median of [12, 3, 9, 6]. Create a needed capability if it is missing.'
```

Review both approvals. The source tests/screenshot use **scripted decisions**;
they do not verify your model will author valid code or use tool feedback well.
No model is silently substituted/downloaded. Errors remain in the original job.

## Versioning, rollback, cancellation and opt-in export

A replacement must supply `replace_version` equal to the active version.
Passing code activates the next immutable version; a failed test never replaces
working code. Failed stages remain visible (limits: 64 names / 32 versions/name).
`rollback_tool` requires `name`, tested target `version`, exact `expected_version`
and approval. It reactivates a tested version; **no test/actions are replayed**.
Stale invocation approvals are blocked after a version change.

Explicit job cancellation kills the worker and prevents late activation.
Ambiguous executing approvals become `unknown_outcome` on restart; they are not
automatically replayed. Audio yield/disconnect never cancels the durable job.

```bash
.venv/bin/python scripts/extension_cli.py export median_values --out my-median.json
# On another separate local ARTEMIS installation:
.venv/bin/python scripts/extension_cli.py propose my-median.json
```

Export is explicit, one selected tool only, and refuses to overwrite an output
file. It contains code/schema/test/manifest, **not Sage memories or private
history**. Review code and declared license before publishing it; test vectors
may themselves contain data you chose, so do not export private test data.
Import always proposes a fresh local test/approval, never executes a manifest's
claimed provenance or silently trusts a previous machine's result.

Implementation: `capability_contract.py`, `generated_tools.py`,
`extension_sandbox.py`, `extension_worker.py`, `store.py`, `tools.py`, `runtime.py`.
Contracts: `tests/test_hot_tools.py`, `tests/test_job_presence.py`,
`tests/test_offline_sources.py`. Optional richer extensions are staged follow-up
work, not a completed community platform.

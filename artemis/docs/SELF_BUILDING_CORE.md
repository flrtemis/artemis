# ARTEMIS's self-building core — founder specification correction

**2026-10-19 · founder correction relayed directly by Rowan.**

**ARTEMIS — A Reality That Enhances My Integrated Services.**

> The spec is not merely “can do what we can do.” It is “can do what we can do
> AND grow new capabilities autonomously.” The self-building core is the real build.

A capability inventory does not build ARTEMIS. It is evidence and discovery
infrastructure for the product, not the product's endpoint. This correction is
additive: it does not discard existing tools, Sage continuity, FORGE, speech,
vision, phone, workspace, interface, privacy, or native-worker work.

## Product requirement

ARTEMIS must eventually identify useful unmet needs and extend itself without
requiring a person to initiate and steer every construction step. Within an
owner-authorized purpose, resource budget and permission boundary, it should:

1. Observe task failures, unmet goals and missing/unreliable abilities.
2. Express the gap as a concrete capability objective and acceptance contract.
3. Plan and construct a candidate implementation and its integration metadata.
4. Stage candidate artifacts in a bounded environment, not execute model code
   inside the trusted gateway or overwrite working source/state.
5. Run acceptance/security/resource/compatibility checks, including checks whose
   authority is not the same candidate/model asserting it passed.
6. Consume real failures, repair/retest within a durable budget, and stop honestly
   when blocked, exhausted, cancelled or uncertain—not invent success.
7. Make a validated candidate usable when already within the grant, with exact
   immutable versions, provenance, rollback and known state/resource ownership.
8. Use the new ability in the original task, retain the evidence, and reuse it in
   a later independent task without rebuilding a pretend demonstration.
9. Continue that loop from useful observations without requiring a human prompt
   for every new capability. Scheduling must respect interactive work and the
   existing selected local model/resource policy.

The target is **autonomous functional growth**. That may mean new executable
capabilities, adapters, workflows or reviewed artifacts; it is not proof that a
base model's weights, general intelligence, consciousness or hardware performance
improve. Those are separate mechanisms and evidence requirements.

## Autonomy and authority are different

“Autonomous” must not be implemented as “ask permission for every build/test/repair
step and call that autonomous.” A future owner grant should cover a **bounded
construction mission/policy**, so routine authorized work can proceed unattended.

It also must not mean “unlimited privilege”:

- A generated tool cannot authorize itself, widen its grant, edit the policy,
  overwrite the gateway, expose private memory, install arbitrary dependencies,
  acquire devices or enable network/cloud/training operations by naming them.
- New permissions, external costs, private-data egress, irreversible effects,
  provider/hardware changes and materially expanded resource use require the
  appropriate authority. Repeated approval for already authorized pure build/test
  work is different from permission escalation.
- Disable/cancel/revoke must fence model responses, worker output, registration
  and subsequent calls. Audio interruption must not silently cancel the mission.
- Crashes and unknown mutation outcomes must not cause automatic irreversible
  replay. A pending build and a completed/activated capability are different states.
- A tested candidate is not automatically safe or semantically correct. Acceptance
  oracles must be independent of “the candidate says it works”; retain provenance,
  real execution evidence and limitations.
- No second assistant/history/database is introduced. Runtime/Store remain the
  canonical mission, continuity, event, approval, artifact and registry owners;
  resource-admitted workers perform the isolated construction/testing.

The current v1 generated-tool manifest promises per-creation/activation/invocation
approval. Do not silently reinterpret old v1 records as autonomously authorized.
Any unattended mode needs an explicit versioned authority contract, clear scope
and migration/tests—not a global removal of `requires_approval`.

## Honest current state (code inspected at 4f6e1f3)

| Existing mechanism | What exists | Missing self-building behavior |
|---|---|---|
| `generated_tools.py` | Immutable staging, real isolation/test, hot schema registration, feedback, version preconditions, rollback/export | Creation/use each require human approval; one model-selected expected result is not an independent acceptance suite; no unattended mission authority |
| `runtime.py` | Same canonical model/task/tool loop, durable call/round budgets, errors/results, correction/cancel/restart policy | No versioned construction mission, scoped preauthorization, discovery scheduling, independent evaluator or reusable unattended-growth completion gate |
| `autonomy.py` | Scheduled continuity/reflection with public projections, preemption and bounded actions | `provider.chat(..., [])` gives no tool schemas; host contract forbids shell/web/files; arbitrary/generated tools are intentionally not actionable in wakes |
| Store/registry | Persisted extension versions, tested-state activation, canonical runs/events | No separate recorded construction authority/revocation, goal-to-gap lineage or acceptance-oracle ownership |
| Capability/source matrix | Provenance/readiness/gap evidence | Inventory alone is not a planner, constructor, evaluator, repair loop or growth result |
| FORGE contribution | Source-pinned candidate/test/verifier for local voice training | Native training still NOT RUN here; not a registered self-building/voice-training worker or automatic voice promotion |

The earlier scripted hot-tool tests prove real runtime/isolation mechanics, not
that the full autonomous-growth requirement has been delivered. This document is
**a specification and implementation contract, not an implementation claim**.
No approval/sandbox/network/resource gate was weakened by this correction.

## First concrete build milestone — bounded unattended JSON capability growth

Start by extending the safe existing pure-JSON/std-lib sandbox path, not by giving
an agent unrestricted shell access or self-editing the trusted application.

A single owner-authorized construction mission should bind:

- Purpose/origin (including a system-discovered gap) and canonical run/thread/actor.
- Versioned grant ID/digest, revocation, allowed capability namespace and no core
  replacement, no files/private continuity/egress, dependency policy and scope.
- Host-owned acceptance contract/oracle identity and immutable test/evaluation
  cases; the repair model cannot simply change expected results to make failure pass.
- Maximum model rounds, code versions, tests, wall/CPU/memory/output/scratch,
  per-mission/host resource admission and unattended scheduling limits.
- Candidate/staged/failed/validated/activated/used/blocked/cancelled states and
  immutable artifact/code/test hashes, all in the canonical Store/events.

The model may generate and repair code within this mission without human clicks
between attempts. Existing tests are mechanisms to reuse, not a new isolated fake
registry. Completion requires actual sandbox execution and usable registration,
not merely a generated code file, a plan, a metadata row or a congratulatory reply.

### Required first demonstration

1. A concrete task/goal needs a capability absent from the registry.
2. The mission has one explicit scope/resource authorization; no per-attempt
   code or invocation approval is manually clicked inside that authorized boundary.
3. The same canonical model/runtime builds a candidate whose first test fails.
4. Real failure returns to that same mission; it repairs the implementation,
   while the authoritative acceptance tests stay unchanged.
5. Actual namespace/seccomp/container isolation runs the tests; no host execution
   or stub substitute. Resource/egress/private-state boundaries hold.
6. Passing candidate activates atomically under the still-valid grant and exact
   version preconditions, and answers the original task from an actual invocation.
7. Restart preserves the tested capability and evidence; a separate subsequent
   task uses it without another restart or rebuilding it.
8. Negative cases prove cancellation, revocation, stale version/model response,
   budget exhaustion, missing real isolation, core collision, acceptance tampering,
   cross-scope private data, failed candidate replacement, unknown outcomes and
   unsupported effects fail closed.
9. An unattended observation/goal schedules a subsequent eligible mission under
   policy rather than waiting for someone to type “create a tool.” Interactive
   work can defer construction; no unlimited busy-model concurrency is promised.

A deterministic provider may test orchestration, but must remain labelled. Actual
model authoring/repair and Bob's machine/resource behavior need their own evidence.
Do not count a documentation update, inventory entry or fixture-only execution as
this full milestone.

## Exact implementation seams and tests

- **Proposed `artemis_app/construction.py`:** versioned mission/grant validation,
  immutable acceptance contract and decision policy. No second model/history owner.
- **Existing `runtime.py`:** mission start and `advance` integration, durable budgets,
  same-loop failure/repair, origin lineage, interactive scheduling/preemption.
- **Existing `generated_tools.py`:** split candidate test/evaluation/activation;
  honor scoped authority without changing legacy v1 approval semantics; preserve
  immutable code, exact preconditions, real sandbox and caller grant checks.
- **Existing `store.py`:** additive mission/grant/evaluation/revocation records,
  transactional activation and recovery with no irreversible auto-replay.
- **Existing `autonomy.py`:** explicit gap/goal construction scheduling under policy,
  not silently exposing all tools to legacy continuity wakes or their private state.
- **Existing `extensions.py` / `api.py`:** authenticated admission/status/revoke and
  honest capability/readiness projection. Default off until configured authority.
- **Proposed `tests/test_self_building_core.py`:** the complete positive/negative
  demonstration above, real isolation mandatory for execution assertions.
- **Existing hot-tool/job-presence/source tests:** preserve previous approvals,
  audio-only interruption, immutable originals and no private-state leak.

Proposed paths above are TODOs, not empty files presented as completed work.

## Relationship to FORGE and other contributions

Continue FORGE's real native verification; its source/test work is not discarded.
A future construction mission may identify, adapt and validate such a worker, but
it does not gain permission to train on private audio, upload to a roaming provider,
load large models or promote a new serving voice merely because the task is
“self-building.” Rich native/media/device grants need reviewed contracts and real
resource/license/privacy tests beyond this first JSON-only milestone.

Pages should show honest verified progress, but it is a public static surface,
not the autonomous local runtime. Existing publishing-source permission failure
remains a separate blocker. No merge, main/source-branch overwrite, read-only inbox
change or deployment is implied by this spec correction.

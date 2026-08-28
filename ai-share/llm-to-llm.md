# Session Handover — GPT/User Experiment Interaction Layer

state: ready
created_at: 2026-08-28T14:17:00+09:00
project: `comus93/portfolio-optimizer-kr`

## 1. Why this handover exists

The next conversation should continue from the existing optimizer v1 and design the next interaction layer:

> **User ↔ GPT conversation → experiment selection/design → YAML generation/management → engine execution, including batch runs → run outputs → GPT interpretation with user discussion → interpretation stored in GitHub and linked back to the originating experiment/run → follow-up experiments.**

The user wants this phase discussed in a separate ChatGPT conversation.

Do not restart from basic optimizer design. Treat the optimizer engine as the existing execution backend.

---

## 2. Current system baseline

Current execution paths already exist conceptually/partially as:

```text
1) YAML → Optimizer Engine → result/review/raw CSV/JSON

2) Streamlit → YAML → Optimizer Engine → result/review/raw
                                      → viewer/charts later
```

Important architectural boundary already agreed:

```text
Streamlit → YAML → existing runner
CLI       → YAML → existing runner
GPT       → YAML → existing runner
```

There should not be a separate GPT-only financial API or UI-only execution semantics.

The YAML contract is the common execution contract.

Current v1 optimization objectives are effectively closed for product progression:

- Maximum Sharpe Ratio
- Maximum Return subject to Target Annual Volatility

Both have PV golden/offline/live validation work. Target-vol parity diagnostics may receive minor artifact-polish follow-up, but that is **not a blocker for the next phase**.

Current run output model includes:

```text
runs/<run_id>/
├─ input.yaml
├─ result.json
├─ review/*.csv
├─ raw/*.csv
└─ optional parity diagnostics for golden validation
```

`review/` is human/GPT-friendly percentage-oriented output; `raw/` preserves full-precision calculation projections.

---

## 3. New interaction model the user wants

The user does **not** want to manually browse YAML files and choose filenames.

GPT should become the semantic research front-end.

Example desired interaction:

```text
User: 예전에 하던 실험 이어서 하자.

GPT reads GitHub research state and answers roughly:

1. 8/28 GLD cap sensitivity
   - what was tested
   - what conclusion user + GPT reached
   - what follow-up was proposed

2. QQQ / target-volatility study
   - what was tested
   - prior interpretation
   - next candidate work

User: 1번

GPT:
- selects the corresponding experiment or follow-up batch
- updates the execution pointer in GitHub
- engine can then execute the selected experiment without the user knowing the YAML filename
```

So **experiment discovery and selection are also GPT responsibilities**.

The user should choose based on meaning/history, not repository path knowledge.

---

## 4. GitHub is the interaction/state bridge

GitHub should act as the durable research memory and handoff bus between:

```text
User ↔ GPT ↔ GitHub ↔ Optimizer
                ↑         ↓
                └─ results/interpretation
```

GitHub is not necessarily the runtime compute engine.

Optimizer execution stays in the existing runner/runtime environment.

GitHub stores the durable artifacts needed to reconstruct research context.

Expected roles:

```text
Specification / code
Experiment definitions
Batch definitions
Execution selection pointer
Run outputs
GPT + user interpretation / conclusions
Links between experiment → run → interpretation → follow-up
```

---

## 5. Core research objects discussed

The conceptual model agreed so far is:

```text
Study
  │
  ├─ Experiment YAML
  │      │
  │      ▼
  │     Run
  │      │
  │      ▼
  └── Interpretation / Report
          │
          ▼
      Follow-up Experiment or Batch
```

Candidate object meanings:

### Study
A research topic/question grouping multiple related experiments.

Example:

```text
GLD allocation cap sensitivity
KODEX 운송 편입 연구
QQQ concentration study
```

### Experiment
A concrete optimizer YAML that can be executed reproducibly.

### Batch
A set of experiments executed together to answer one comparative question.

The user explicitly **agreed with batch experiment support**.

### Run
A concrete execution instance with generated outputs.

One experiment may have multiple runs over time.

### Interpretation / Report
Stores more than an AI-generated summary.

It should capture:

```text
calculated result facts
GPT interpretation
user understanding / reaction / judgment
agreed conclusion
follow-up question or next experiment
```

This is important because the user wants GPT to later say not only:

> “이런 run이 있었다”

but also:

> “그 당시 사용자와 LLM은 이 결과를 이렇게 해석했고, 이런 follow-up을 남겼다.”

---

## 6. Experiment ↔ Run ↔ Interpretation linkage is essential

The user explicitly wants:

```text
experiment set
   ↓
run
   ↓
interpretation
```

linked in the repository.

This linkage must support future GPT recall/navigation.

A run should retain enough source metadata to identify the exact experiment/revision that produced it.

Current `runs/<run_id>/input.yaml` copy is already a useful reproducibility anchor.

A lightweight metadata record may be useful, for example:

```yaml
study_id: gld-cap-sensitivity
experiment: studies/gld-cap-sensitivity/experiments/004-gld-max30-r02.yaml
batch: studies/gld-cap-sensitivity/batches/round-02.yaml
```

Exact schema is **not yet frozen**. Discuss it in the new conversation.

---

## 7. Execution pointer idea

The previous conversation proposed that GPT should update one small tracked control file after the user chooses an experiment semantically.

Preferred direction was a tracked YAML pointer rather than `.env`, because `.env` implies secrets/local environment and is usually gitignored.

Candidate:

```text
control/execute.yaml
```

Single execution example:

```yaml
mode: single
study_id: korean-transport
experiment: studies/korean-transport/experiments/003-add-140710-r01.yaml
```

Batch example:

```yaml
mode: batch
study_id: gld-cap-sensitivity
batch: studies/gld-cap-sensitivity/batches/round-02.yaml
```

Then the runtime command can be intentionally boring:

```text
portfolio-optimizer execute
```

and it reads the pointer.

This was a design discussion, **not yet an implemented contract**.

The new conversation should validate/refine this design before implementation.

---

## 8. Batch experiment direction

The user explicitly approved batch experiments.

Desired behavior:

```text
GPT/user discussion
   ↓
GPT designs several YAML experiments
   ↓
batch groups them under one research question
   ↓
engine executes selected/all batch members
   ↓
comparison outputs
   ↓
GPT interprets the batch jointly
```

Example conceptual batch:

```yaml
batch_id: round-02
question: >
  GLD 25~35% stable plateau 내부를 세분화해 적정 allocation range를 확인한다.
experiments:
  - ...27.5...
  - ...30.0...
  - ...32.5...
```

Do not assume this exact schema is final.

A major design question for the new conversation is how much comparative aggregation the engine should generate versus how much GPT should derive from existing run outputs.

Prefer a small, practical first version.

---

## 9. Revision philosophy

User wants practical revision management, not a heavy versioning subsystem.

For experiment YAMLs, file naming can distinguish revisions, e.g.:

```text
004-gld-max30-r01.yaml
004-gld-max30-r02.yaml
```

Do not build a complex semantic-version/revision database unless a real need appears.

Git itself already provides history.

Important correction from the prior conversation:

> **Do NOT impose a rule that interpretation/report files must be immutable or that every change requires a new report file.**

The user rejected that rigidity.

Reports/interpretations should remain practical and flexible: edit, supplement, replace, or add files as useful.

The system should preserve traceability without turning research note-taking into bureaucracy.

---

## 10. Candidate repository structure discussed

A possible direction, not frozen:

```text
studies/
└─ <study-id>/
   ├─ study.md                 # optional human/GPT context
   ├─ index.yaml               # optional navigation index
   ├─ experiments/
   │  ├─ 001-base-r01.yaml
   │  ├─ 002-...yaml
   │  └─ ...
   ├─ batches/
   │  ├─ round-01.yaml
   │  └─ ...
   └─ reports/                 # GPT + user interpretation/history
      └─ ...

control/
└─ execute.yaml

runs/
└─ <run_id>/
   ├─ input.yaml
   ├─ result.json
   ├─ review/
   └─ raw/
```

Do not treat this as final architecture.

The new conversation should simplify or change it if a more practical mapping emerges.

---

## 11. GPT recall/navigation requirement

The repository should make the following future interaction possible:

```text
User: 운송 관련 실험 다시 보자.

GPT:
- finds relevant studies
- summarizes the experiments performed
- identifies linked runs
- retrieves prior GPT/user interpretation
- tells the user what follow-up was left
- asks which line to continue

User: 1번

GPT:
- selects/creates the relevant follow-up YAML or batch
- updates execution selection
```

GPT should not need to scan every raw CSV in the repository for every question.

Therefore a lightweight navigation/index strategy may be valuable.

But avoid premature heavy state machines such as `draft → ready → executed → reviewed` unless they prove necessary.

Previous preference was **not** to put mutable execution status into experiment YAML itself.

---

## 12. Three front-ends, one backend

The intended end state has three complementary user surfaces:

| Interface | Primary use |
|---|---|
| YAML / CLI | precise developer/agent execution |
| Streamlit | GUI search/select/configure/run/view |
| ChatGPT ↔ GitHub | natural-language experiment design, recall, selection, comparison, interpretation |

All should ultimately converge on the same YAML/run contract.

Conceptually:

```text
             ChatGPT
                │
Streamlit ──── YAML ──── CLI
                │
                ▼
             Engine
                │
                ▼
              Runs
```

---

## 13. Design principles to preserve

1. **Practicality over ceremony.**
   Do not over-engineer a research-management framework.

2. **GPT handles semantic selection.**
   User should not have to remember YAML names or paths.

3. **Reproducible execution remains YAML-based.**
   GPT conversation itself is not the calculation source of truth.

4. **Runs are factual machine output.**
   GPT/user interpretation must remain distinguishable from calculated facts.

5. **Interpretation is durable research memory.**
   Store what the user and GPT concluded, not only generated metrics.

6. **Batch is first-class enough to be useful, but keep v1 small.**

7. **Reports remain editable/flexible.**
   No unnecessary immutability rule.

8. **Filename-level experiment revisions are sufficient initially.**

9. **GitHub is the durable bridge.**
   It should allow a new GPT conversation to recover studies, runs, conclusions, and next steps.

10. **Do not reopen completed optimizer-engine questions unless the new interaction layer exposes a real gap.**

---

## 14. Recommended first discussion in the new conversation

Before assigning implementation to Codex/Agent, settle the minimum contracts for:

```text
Study
Experiment
Batch
Run linkage metadata
Interpretation/Report linkage
Execution pointer
Navigation/index
```

The most important practical scenario to design end-to-end first is:

```text
1. User and GPT discuss a portfolio hypothesis.
2. GPT creates 3 related experiment YAMLs and one batch.
3. Later the user says “그 실험 이어가자.”
4. GPT discovers the study and summarizes prior work/conclusions.
5. User chooses option 1 conversationally.
6. GPT changes the execution pointer.
7. Engine executes the batch.
8. GPT reads review outputs and compares runs.
9. GPT and user discuss what the results mean.
10. Their conclusion + follow-up are written back and linked to the study/runs.
11. A later GPT session can reconstruct the chain without the user manually relaying files.
```

If this scenario is clean, the metadata model is probably sufficient.

---

## 15. Current pending work outside this handover

There was a non-blocking follow-up request to enrich Target Volatility golden parity diagnostic artifacts. It is useful validation polish, not a blocker for this next interaction-layer design.

Do not let that distract the new conversation from the main next-phase goal.

---

## 16. User working style relevant to this phase

The user wants the LLM to act as the research PM/analyst rather than merely paraphrase requests.

Expected behavior:

- propose concrete next experiment structure
- challenge weak designs
- prefer robust simple workflows
- create repository artifacts when the design is agreed
- use Codex Agent for implementation/hardening after LLM defines contracts/tests
- minimize manual user copy/paste between GPT and Agent

The immediate task in the new conversation is **design discussion**, not automatic implementation before the interaction contract is agreed.

# RegPulse Roadmap — from skeleton to production agent

Ten milestones, built one at a time with Claude Code. Each one ends in a merged
PR, green CI, and a learning-log entry (see [LEARNING.md](LEARNING.md)).

**Rule:** only the milestone marked **CURRENT** gets worked on. When it meets
its "Done when", mark it ✅, move **CURRENT** to the next one, and update the
status table in `CLAUDE.md`.

| # | Milestone | Status | You'll learn (production) |
|---|---|---|---|
| M1 | Ingest & deterministic diff | **CURRENT** | Scraping brittleness, fixtures, determinism, idempotency |
| M2 | Storage, scheduling & CI | | Migrations, idempotent jobs, retries, structured logs, CI |
| M3 | Mock lender: effective-dated rules engine | | Temporal data, audit trails, deterministic decisions |
| M4 | First LLM step: impact mapping | | Structured output, citations, prompt injection, cost |
| M5 | Retrieval over guides, rules & code | | Chunking, hybrid search, embedding versioning, retrieval evals |
| M6 | Agent graph with human approval | | State, checkpoints, bounded loops, HITL, tool errors |
| M7 | Fix drafting in a sandbox → PR | | Sandboxing, least privilege, never auto-merge, rollback |
| M8 | API, auth & review UI | | AuthN/Z, rate limits, input validation, async jobs |
| M9 | Observability & eval gates | | Tracing, regression gates, LLM-as-judge, drift, cost dashboards |
| M10 | Deploy, harden & demo | | Containers, IaC, secrets, SLOs, chaos drills, runbooks |

Stack (unchanged): Python 3.11, FastAPI, LangGraph, AWS Bedrock (larger Claude
model for reasoning, smaller for triage), PostgreSQL + pgvector, Langfuse,
GitHub Actions.

Each milestone below has the same sections:

- **Goal** — one sentence.
- **Learn first** — concepts to read about *before* opening Claude Code (≤ 1 hour).
- **You write by hand** — the pieces you implement yourself; Claude reviews.
- **Build** — the task list.
- **Production scenarios** — the failure drills you must run and handle.
- **Done when** — acceptance criteria. Not done until every box is checked.
- **Kickoff prompt** — paste into Claude Code to start.

---

## M1 — Ingest & deterministic diff  **CURRENT**

**Goal:** detect a new GSE bulletin and produce a correct section-by-section
diff of the guide.

**Learn first:** HTML/PDF extraction pitfalls; why diffs must be deterministic;
test fixtures vs live calls; idempotency.

**You write by hand:** the HTML parser for the bulletin list page; two golden
cases.

**Build**
- [x] Repo skeleton, shared `core/` contract
- [x] `diff_sections` with noise normalization + tests
- [ ] `fetch_latest_bulletins` for ONE source (Fannie Mae Selling Guide announcements)
- [ ] `fetch_guide_snapshot` for the sections a bulletin names; raw cache in `data/raw/`
- [ ] Saved real pages in `tests/fixtures/`; parser tests against them
- [ ] 3–5 golden cases from real past changes (with `sources` URLs)
- [ ] `examples/worked-example.md` filled from a real run

**Production scenarios**
- Source page layout changes → parser fails loudly with a clear error, not empty results
- Network timeout / 5xx → raises; caller decides retry
- Same bulletin fetched twice → same output (idempotent)
- PDF re-extraction noise → no false "modified"

**Done when**
- [ ] `pytest -q` green with zero network calls
- [ ] `python -m regpulse.eval` ≥ 3 real cases, all passing
- [ ] Worked example uses real data end to end

**Kickoff prompt:** see "Step 2 — Fetcher" in [claude-code-setup.md](claude-code-setup.md).

---

## M2 — Storage, scheduling & CI

**Goal:** the watcher runs on a schedule, stores everything in Postgres, never
double-processes a bulletin, and every PR runs tests automatically.

**Learn first:** Alembic migrations; idempotency keys; exponential backoff with
jitter; structured (JSON) logging; GitHub Actions basics.

**You write by hand:** the first Alembic migration; the idempotency check.

**Build**
- [ ] Docker Compose with Postgres (+ pgvector image, used in M5)
- [ ] Tables: `bulletins`, `guide_snapshots`, `guide_sections`, `section_diffs`, `runs`
- [ ] Repository layer (plain SQL or SQLAlchemy Core), no ORM magic in `core/`
- [ ] `regpulse watch` CLI: fetch → store → diff → store; unique key on `(source, bulletin_id)`
- [ ] Retries with backoff for fetches; `runs` table records start/end/status/error
- [ ] JSON logging with a `run_id` on every line
- [ ] GitHub Actions: ruff, mypy, pytest, `python -m regpulse.eval` on every PR
- [ ] Scheduled workflow (cron) or local scheduler running `regpulse watch`

**Production scenarios**
- Run crashes halfway → re-run completes without duplicates
- Two runs start at once → only one processes a bulletin (row lock or advisory lock)
- Source down for a day → backoff, then a clear failed `run` row, no data loss
- Schema change → migration up and down both work

**Done when**
- [ ] Killing the watcher mid-run and re-running produces identical tables
- [ ] CI is required on `main` and green
- [ ] `docs/runbook.md` has "how to re-run a failed watch"

**Kickoff prompt**
```
/plan Start M2 from docs/ROADMAP.md. Propose the schema and migration plan
first and wait for my approval. I will write the first Alembic migration and
the idempotency check myself — leave TODO(YOU) markers there and explain what
they must do. Add CI last.
```

---

## M3 — Mock lender: effective-dated rules engine

**Goal:** a small, realistic "lender" whose decisions depend on rule versions in
force on a date, so a regulatory change visibly flips a loan decision.

**Learn first:** slowly changing dimensions (type 2); bitemporal basics; why
rules belong in data, not code; decision audit trails.

**You write by hand:** the "rule in force on date D" query; 5 boundary tests.

**Build**
- [ ] `lender/` package (separate from `regpulse/`): rules table with
      `rule_id, version, dt_effective_start, dt_effective_end, expression, source_citation`
- [ ] Rule change = expire old row + insert new row (never update in place)
- [ ] Evaluator for credit score, DTI, LTV/CLTV, reserves, property type, overlays
- [ ] Loan fixtures with expected outcomes; every decision cites rule ids + versions
- [ ] Planted traps for later milestones: a hard-coded threshold in Python, a
      duplicated rule, a stale threshold in a policy doc, a magic number in a test
      (answer key in `evals/answer_keys/` — keep it out of prompts)
- [ ] Demo script: same loan, decision before vs after a rule change

**Production scenarios**
- Two versions overlap in time → constraint rejects it
- Decision replay: re-running a 6-month-old decision uses the rules in force then
- Rule with no citation → rejected on insert

**Done when**
- [ ] Decision flip demo runs from one command
- [ ] Every decision row stores the exact rule versions used

**Kickoff prompt**
```
/plan Start M3 from docs/ROADMAP.md. Show me the rules table design and the
"rule in force on date D" approach first. Leave TODO(YOU) for that query and
the boundary tests. Don't touch src/regpulse/ except to read core/.
```

---

## M4 — First LLM step: impact mapping

**Goal:** given a `SectionDiff`, an LLM returns which lender rules, code, tests,
and docs are affected — as validated structured output with citations.

**Learn first:** structured output with schemas; prompt injection from
*retrieved/fetched* documents; temperature and determinism; token cost math;
precision/recall.

**You write by hand:** the output schema; the impact-mapping eval metric.

**Build**
- [ ] `core/llm.py`: Bedrock client wrapper — timeouts, retries on throttling,
      token + cost accounting per call, model id from config
- [ ] Prompt files versioned in `prompts/` (name + version in every trace)
- [ ] `impact.map_impact(diff, candidates) -> ImpactBrief`, Pydantic-validated;
      one repair retry on invalid output, then fail
- [ ] Guardrail: drop any claim without a citation (`ImpactBrief.uncited()`)
- [ ] Fetched regulatory text wrapped as untrusted data in the prompt
- [ ] Eval kind `impact_mapping`: precision/recall vs answer keys; ≥ 5 cases
- [ ] Response cache keyed on (prompt version, model, input hash) for dev

**Production scenarios**
- Model returns invalid JSON → one repair attempt, then a clean failure
- Bulletin text contains "ignore previous instructions…" → no behavior change (add as a golden case)
- Bedrock throttles → backoff; budget exceeded → stops with a clear error
- Model invents a rule id → caught because it isn't in the candidate set

**Done when**
- [ ] Impact eval ≥ 0.8 recall, ≥ 0.8 precision on the golden set (record actuals)
- [ ] Cost per run printed; prompt-injection case passes
- [ ] Unit tests run with a fake LLM, no network

**Kickoff prompt**
```
/plan Start M4 from docs/ROADMAP.md. Before code, explain the trade-offs
between tool-use structured output and JSON-mode for Bedrock, and how we'll
test without calling the model. Leave TODO(YOU) for the output schema and the
eval metric.
```

---

## M5 — Retrieval over guides, rules & code

**Goal:** find the right candidates for M4 automatically across the guide,
lender rules, policy docs, and code.

**Learn first:** chunking strategies; BM25 vs embeddings vs hybrid; reranking;
retrieval metrics (recall@k, MRR); embedding model versioning.

**You write by hand:** the chunker for guide sections; recall@k.

**Build**
- [ ] pgvector tables with `embedding_model` + `chunk_version` columns
- [ ] Indexers: guide sections, lender rules, docs, code (by function)
- [ ] Hybrid search (keyword + vector) with a small reranker step
- [ ] Guideline Copilot exposed as a FastAPI tool service; RegPulse calls it over HTTP
- [ ] Retrieval eval kind: recall@5 against answer keys
- [ ] Re-index command; old-version chunks never mixed with new

**Production scenarios**
- Embedding model changes → full re-index, no mixed vectors
- Guide section updated → only that section re-embedded
- Exact section ids ("B3-6-02") → keyword path finds them where vectors miss

**Done when**
- [ ] recall@5 ≥ 0.9 on golden cases; M4 now runs on retrieved candidates
- [ ] Re-index is idempotent and resumable

**Kickoff prompt**
```
/plan Start M5 from docs/ROADMAP.md. Compare 3 chunking options for selling
guide sections with pros/cons, then wait for my pick. Leave TODO(YOU) for the
chunker and recall@k.
```

---

## M6 — Agent graph with human approval

**Goal:** a LangGraph workflow: triage → retrieve → impact → draft actions →
verify → **human approval**, resumable from any step.

**Learn first:** LangGraph state, nodes, conditional edges, checkpointers,
interrupts; when an agent loop is better than a fixed pipeline (and when not).

**You write by hand:** the state schema; the verifier node's checks.

**Build**
- [ ] Graph state = typed object; every node pure-ish (state in → state out)
- [ ] Triage node on the small model: "does this change matter to us?" with reason
- [ ] Postgres checkpointer; resume a run by `thread_id`
- [ ] Verifier: every action cites a source; affected ids exist; else loop back (max 2)
- [ ] `interrupt` before any outward action; approval stored with who/when
- [ ] Hard limits: max steps, max tokens, wall-clock timeout per run
- [ ] Graph-level eval: end-to-end on golden bulletins

**Production scenarios**
- Process dies mid-graph → resumes from last checkpoint, no repeated LLM calls
- Verifier keeps failing → stops at the loop limit with a "needs human" brief
- Tool raises → node records the error in state, graph routes to failure path
- Approval never comes → run stays parked, no timeout side effects

**Done when**
- [ ] Kill-and-resume demo works
- [ ] No path reaches an outward action without an approval record

**Kickoff prompt**
```
/plan Start M6 from docs/ROADMAP.md. Draw the graph (nodes, edges, state
fields) in text first and explain each failure path. Leave TODO(YOU) for the
state schema and verifier checks.
```

---

## M7 — Fix drafting in a sandbox → PR

**Goal:** for an approved impact, draft the change to the mock lender (new rule
version, doc edit, test update), run its tests in a sandbox, and open a PR.

**Learn first:** container sandboxing; GitHub fine-grained tokens; why agents
must never auto-merge; idempotent PR creation.

**You write by hand:** the sandbox runner's resource limits; the PR body template.

**Build**
- [ ] Drafter produces a patch (new rule row via migration, doc/test edits)
- [ ] Sandbox: Docker, no network, CPU/memory/time limits, read-only base
- [ ] Run lender tests in sandbox; failing patch → back to drafter (max 2)
- [ ] Open PR on a separate demo repo via fine-grained token (contents + PRs only)
- [ ] PR body = ImpactBrief with citations; label `regpulse`; never merges
- [ ] Idempotency: same impact → same branch name → updates, not duplicates

**Production scenarios**
- Patch breaks tests → never opened as PR; brief says why
- Token leaked scope → token can't merge or touch other repos (verify)
- Planted traps from M3 found (hard-coded threshold, stale doc) — measure how many

**Done when**
- [ ] One real bulletin → approved → PR with green tests on the demo repo
- [ ] Trap-detection score recorded in the learning log

**Kickoff prompt**
```
/plan Start M7 from docs/ROADMAP.md. Explain the sandbox threat model first:
what could a bad patch do, and how each limit stops it. Leave TODO(YOU) for
resource limits and the PR template.
```

---

## M8 — API, auth & review UI

**Goal:** reviewers see impact briefs, approve or reject, and trigger runs
through an authenticated API and a small UI.

**Learn first:** FastAPI dependencies, OAuth/JWT basics, background jobs vs
request/response, pagination, rate limiting.

**You write by hand:** the approval endpoint and its authorization check.

**Build**
- [ ] Endpoints: list runs, get brief, approve/reject (with reason), trigger watch
- [ ] Auth (simple JWT or GitHub OAuth) + roles: viewer, approver
- [ ] Long work runs as background jobs; API returns a run id
- [ ] Small UI (Streamlit or a light React page): queue, brief view with
      citations linked, diff view, approve button
- [ ] Optional (README Phase 2): chat that builds a loan file and runs M3 decisions

**Production scenarios**
- Viewer tries to approve → 403 (test it)
- Same approval clicked twice → one approval (idempotent)
- Huge payload / bad ids → 4xx with clear errors, never 500

**Done when**
- [ ] Full flow from UI: new bulletin → brief → approve → PR
- [ ] API tests cover every auth path

---

## M9 — Observability & eval gates

**Goal:** you can see every run, trace any answer to its inputs, and CI blocks
changes that make quality worse.

**Learn first:** traces vs logs vs metrics; Langfuse concepts; LLM-as-judge and
its calibration; offline vs online evals.

**You write by hand:** the CI eval gate thresholds; one judge rubric.

**Build**
- [ ] Langfuse tracing on every LLM call and graph node (prompt version, model, tokens, cost)
- [ ] Golden set grown to ~30 cases across kinds
- [ ] CI gate: PR fails if any eval metric drops more than a set margin vs `main`
- [ ] LLM-as-judge for brief quality, checked against 10 human-labeled briefs
- [ ] Dashboard: runs/day, failure rate, p95 latency, cost/run, approval rate

**Production scenarios**
- Prompt edit lowers recall → CI blocks the PR
- Model version change → full eval run before switching
- Judge disagrees with humans > 20% → judge not trusted; fix rubric

**Done when**
- [ ] Any brief in the UI links to its trace
- [ ] A deliberately bad prompt PR is blocked by CI (screenshot in learning log)

---

## M10 — Deploy, harden & demo

**Goal:** RegPulse runs in AWS on a schedule, survives common failures, and has
a demo that tells the story in 5 minutes.

**Learn first:** containers on ECS/App Runner or Lambda; RDS; Secrets Manager;
IaC (CDK or Terraform); SLOs; threat modeling for LLM apps.

**You write by hand:** the threat model; the runbook.

**Build**
- [ ] Dockerfile; IaC for app, scheduler, RDS Postgres, secrets
- [ ] Least-privilege IAM: Bedrock invoke only for the models used
- [ ] SLOs: e.g. new bulletin → brief within 1 hour; alerts on breach
- [ ] Chaos drills (scripted): source down, malformed PDF, Bedrock throttled,
      DB restart, bad deploy rollback
- [ ] `docs/threat-model.md` (prompt injection, data exfiltration via PR, token theft)
- [ ] `docs/runbook.md` + one written postmortem from a real drill
- [ ] README: architecture diagram, demo GIF/video, results table (eval scores, cost/run)
- [ ] Optional: move `core/` to its own package; start HazardLens on it

**Done when**
- [ ] Deployed scheduled run produced a real brief
- [ ] Every chaos drill has a documented outcome
- [ ] Demo script rehearsed; interview stories written (see LEARNING.md)

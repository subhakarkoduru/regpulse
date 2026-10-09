# How to build RegPulse and actually learn production agent engineering

The goal isn't just a working repo. It's that by M10 you can design, debug,
and defend every part of a production agent in an interview — without Claude.

## The milestone loop (repeat for M1 … M10)

| Step | Time | What you do | Claude Code's role |
|---|---|---|---|
| 1. **Read & predict** | 30–60 min | Read the milestone in [ROADMAP.md](ROADMAP.md). Study the "Learn first" topics. Write your own design in `docs/decisions/NNN-<topic>.md` (template below) **before** asking Claude. | None. Closed laptop if needed. |
| 2. **Plan together** | 20 min | Run the kickoff prompt in plan mode. Compare Claude's plan to yours. For every difference ask: *"Why this over my approach? What breaks with mine?"* Update your decision record. | Proposes, explains trade-offs. You approve. |
| 3. **Build in slices** | most of the week | One slice = one test + the code to pass it, ≤ ~100 lines. Write the `TODO(YOU)` pieces yourself. For Claude's slices, ask *"explain this diff line by line"* before accepting. | Writes non-core slices, reviews your code. |
| 4. **Break it** | 1–2 hours | Run every "Production scenarios" drill for the milestone. Predict what happens first, then run it. Fix what fails. | Helps write the drill scripts, not the predictions. |
| 5. **Measure** | 30 min | Run tests + evals. Record the numbers. A milestone without a number didn't happen. | Runs commands, adds golden cases you choose. |
| 6. **Review** | 30 min | Ask Claude to review the branch as a skeptical staff engineer. Fix findings yourself where you can. | Reviewer, not author. |
| 7. **Write it down** | 20 min | Add a `learning-log.md` entry (template below), including one interview story. | Can check your explanation for errors. |
| 8. **Ship** | 10 min | PR, CI green, merge, tag `m<N>`. Update `CLAUDE.md` status + ROADMAP. | Opens PR if you ask. |

**Rhythm:** roughly one milestone per 1–2 weeks at evenings/weekends pace.
M1–M3 are faster (no LLM); M4–M7 are the core learning; M8–M10 are breadth.

## Rules for learning with an AI pair

1. **Never merge code you can't explain.** If you can't explain a line out loud, ask until you can, or rewrite it.
2. **Predict before you run.** Before running tests or a drill, write the expected result. Wrong predictions are where learning happens — log them.
3. **You own the core.** The `TODO(YOU)` pieces in each milestone are the parts interviewers ask about. Write them yourself, then ask for review.
4. **Read the error before asking.** Spend 5 minutes on any failure alone first. Then ask Claude *"what's your hypothesis?"*, not *"fix it"*.
5. **Re-derive once.** After each milestone, rebuild its hardest piece from memory in a scratch file (30 min). If you can't, you haven't learned it yet.
6. **One milestone at a time.** Scope creep is the #1 portfolio killer. Park ideas in `docs/ideas.md`.
7. **Use learning mode.** Start sessions with *"learning mode"* — see `CLAUDE.md` for what that makes Claude do.

## Production scenarios checklist (master list)

By M10, you should have handled every row in real code, with a test or drill.

| Area | Scenario | Milestone |
|---|---|---|
| Data ingestion | Source layout changes; timeouts; partial downloads | M1, M2 |
| Reliability | Idempotent re-runs; concurrent runs; retries with backoff + jitter | M2 |
| Data | Migrations up/down; effective-dated records; audit trail; replay | M2, M3 |
| LLM output | Invalid structured output; repair-then-fail | M4 |
| Grounding | Citations required; invented ids rejected; forecast vs rule labeling | M4, M6 |
| Security | Prompt injection in fetched docs; least-privilege tokens; sandboxed execution; secrets handling | M4, M7, M10 |
| Cost & latency | Token accounting, budgets, caching, small-model triage | M4, M6, M9 |
| Retrieval | Chunking, hybrid search, embedding versioning, re-indexing | M5 |
| Agent control | Bounded loops, step/time limits, tool errors as state, checkpoint/resume | M6 |
| Human-in-the-loop | Approval gates, parked runs, audit of who approved | M6, M8 |
| Change safety | Tests in sandbox, never auto-merge, idempotent PRs, rollback | M7, M10 |
| API | AuthN/Z, rate limits, validation, background jobs | M8 |
| Quality | Golden sets, CI eval gates, LLM-as-judge calibration, model/prompt versioning | M1, M4, M9 |
| Operations | Tracing, metrics, SLOs, alerts, runbooks, postmortems, chaos drills | M9, M10 |

## Templates

### Decision record — `docs/decisions/NNN-<topic>.md`

```markdown
# NNN — <decision>
Date: YYYY-MM-DD · Milestone: M<N>
## Context
What problem, what constraints.
## My design (written before asking Claude)
## Options considered
| Option | Pros | Cons |
## Decision & why
## What would make us revisit this
```

### Learning log entry — append to `docs/learning-log.md`

```markdown
## M<N> — <title> (YYYY-MM-DD)
- **Built:** one paragraph.
- **Numbers:** tests, eval scores, cost/run, latency.
- **Wrong predictions:** what I expected vs what happened.
- **Drill results:** each production scenario → outcome.
- **I can now explain without help:** 3 bullets.
- **Still fuzzy:** what to revisit.
- **Interview story (STAR):** Situation · Task · Action · Result, 4 sentences.
```

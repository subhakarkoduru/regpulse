# CLAUDE.md — RegPulse

Project instructions for Claude Code. Loaded automatically at the start of
every session in this repo. Keep it short, current, and true.

## What this project is

RegPulse is a Regulatory Change Impact Agent for mortgage/finance. It watches
public regulatory sources (GSE selling-guide announcements, CFPB rules, FHFA
notices), diffs the guide section by section, maps downstream impact, and —
in later phases — drafts fixes and opens PRs, always waiting for human
approval before anything ships.

It is a portfolio project. Only **public** data. Never add employer data,
internal documents, credentials, or anything from a real lender.

A sibling project, **HazardLens** (climate outlook → property/portfolio
impact), will reuse `src/regpulse/core/`. Both produce the same `ImpactBrief`.

## Roadmap and current milestone

The whole project is split into milestones M1–M10 in `docs/ROADMAP.md`. **Only
work on the milestone marked CURRENT there.** If a request belongs to a later
milestone, say so and suggest parking it in `docs/ideas.md`. When a milestone
meets its "Done when", update ROADMAP.md and the status table below.

## Current milestone: M1 / Week 1

| Step | Status |
|---|---|
| 1. Repo skeleton | done |
| 2. One public source: bulletin fetcher + guide snapshot fetcher (`fetcher.py`) | **next** |
| 3. Deterministic section diff (`diff.py`) | done, tested |
| 4. First 3–5 golden eval cases from **real** bulletins (`evals/golden/`) | todo |
| 5. One real worked example end to end (`examples/worked-example.md`) | todo |

**Week 1 is done when:** the watcher detects a new bulletin, produces a
section-by-section diff, and `examples/worked-example.md` shows one real
example. **No agents, no LLM calls, no PR generation, no dashboards, no
database yet** (those arrive in M2–M10). If a task drifts toward those, stop
and say so.

## Commands

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q                     # all tests must pass before every commit
python -m regpulse.eval       # golden evals (add --golden-dir PATH to override)
```

## Layout and boundaries

```
src/regpulse/core/   Domain-neutral contract shared with HazardLens.
                     MUST NOT import from regpulse.models / diff / fetcher
                     or mention guides, bulletins, GSEs, or climate.
src/regpulse/        Regulatory-specific code (models, fetcher, diff, eval).
evals/golden/        One JSON file per case; "kind" defaults to "section_diff".
examples/            Real worked examples only.
tests/               pytest; one test file per module.
```

## Rules for working in this repo

1. **Plan first for anything over ~30 lines.** Use plan mode, list the files
   you'll touch, and wait for approval.
2. **Deterministic before generative.** Fetching, parsing, and diffing are
   plain code. An LLM may *summarize* a diff later; it never *produces* one.
3. **Never invent regulatory facts.** Section ids, effective dates, URLs, and
   rule text come from fetched source documents. Golden cases and the worked
   example use real bulletins, never synthetic ones. Unit tests may use
   synthetic text.
4. **Tests with every change.** New behavior gets a test in the same commit.
   Run `pytest -q` and `python -m regpulse.eval` before saying a task is done,
   and paste the result.
5. **Fetching etiquette.** Use `httpx` with a timeout and a descriptive
   User-Agent, cache raw downloads under `data/raw/` (git-ignored), and never
   hit a source in a unit test — tests use saved fixtures in `tests/fixtures/`.
6. **Small commits, feature branches.** Branch names: `week1/<topic>`. Never
   push to `main` directly; open a PR.
7. **Style:** Python 3.11+, type hints everywhere, dataclasses for models
   (Pydantic only at API boundaries later), `from __future__ import annotations`,
   no new dependencies without asking.
8. **Secrets:** none are needed in Week 1. Never commit `.env`, keys, or tokens.

## Key design decisions (don't undo without discussion)

- A **bulletin is the trigger**; the **diff runs between two `GuideSnapshot`s**
  of the guide itself. Bulletins summarize; they don't contain full sections.
- `diff_sections` normalizes extraction noise (whitespace, smart quotes,
  soft hyphens, NBSP) before comparing, but returns the original text.
- Duplicate `section_id`s are an extraction bug → raise, don't guess.
- `ImpactBrief` claims carry a `basis` of `rule`, `observation`, or
  `forecast`; every claim and action needs a `Citation` (`uncited()` checks).

## Learning mode

The owner is building this project to learn production agent engineering
(process in `docs/LEARNING.md`). When a session starts with "learning mode",
or the task is from a ROADMAP milestone, follow these rules:

1. **Ask for their design first.** Before proposing a plan, ask whether they
   have a decision record in `docs/decisions/` for this task; if so, read it and
   compare your plan against it, explaining every difference.
2. **Leave `TODO(YOU)` pieces for the owner.** Each milestone lists "You write by
   hand" items. Don't implement them. Create the stub, a failing test, and a
   comment explaining what it must do and which edge cases matter. Review their
   implementation honestly when they're done.
3. **Explain before writing.** For each slice you implement, first say in 2–4
   sentences what you'll do and why, then write it. Keep slices small (one test
   + the code to pass it).
4. **Debug Socratically.** When something fails, state your hypothesis and the
   evidence, and ask the owner for theirs before fixing, unless they say "just fix it".
5. **Name the production concern.** When code handles a production scenario
   (retry, idempotency, injection, limits…), say which one in a code comment
   and in your reply.
6. **Be a skeptical reviewer.** When asked to review, prioritize correctness,
   failure modes, and security over style. Don't soften findings.
7. **Close the loop.** At the end of a milestone, remind the owner to run the
   production drills, record eval numbers, and write the learning-log entry.

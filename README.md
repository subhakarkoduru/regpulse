# RegPulse — Regulatory Change Impact Agent

Watches mortgage/finance regulatory sources (GSE selling-guide bulletins, CFPB rules,
FHFA notices), diffs new material section-by-section against prior guide versions,
maps downstream impact, drafts fixes in a sandbox, and opens GitHub PRs/tickets —
always waiting for human approval before anything ships.

## Week 1 scope (the only scope that matters right now)

1. Repo skeleton (this)
2. One public bulletin source + fetcher (`src/regpulse/fetcher.py`)
3. Section-by-section diff (`src/regpulse/diff.py`)
4. First 3–5 golden eval cases (`evals/golden/`)
5. One real worked example end to end (`examples/worked-example.md`)

**Done =** the watcher detects a new bulletin, produces a section-by-section diff,
and `examples/worked-example.md` shows one real worked example.
No agents, no PR generation, no dashboards yet.

## Layout

```
src/regpulse/
  models.py    Data models: Bulletin, GuideSection, SectionDiff
  fetcher.py   Bulletin fetching (one source to start)
  diff.py      Section-by-section diff of guide versions
  eval.py      Golden-case eval harness
evals/golden/  Golden eval cases (JSON) — target ~30 over time
examples/      Real worked examples
tests/         Unit tests
```

## Roadmap (parked until Week 1 ships)

- **Phase 2:** underwriting engine with rules in Postgres (not YAML) — each rule
  carries `dt_effective_start` / `dt_effective_end`; a rule change expires the old
  row and inserts a new one, giving a full audit trail. Loan decisions cite the
  rule version in force. Plus an LLM chat UI that builds the loan file
  conversationally. Demo: same loan file, decision flips before/after a reg change.

## Dev

```bash
pip install -e ".[dev]"
pytest
python -m regpulse.eval   # run golden evals
```

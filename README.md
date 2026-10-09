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
  core/        Domain-neutral contract shared with HazardLens:
    events.py    ChangeEvent — any external change (regulatory, climate, ...)
    citations.py Citation — one format for every claim
    brief.py     ImpactBrief — event, scope, claims (rule/observation/forecast),
                 required actions, confidence; .uncited() guardrail hook
    evals.py     Golden-case runner; projects register an evaluator per case kind
  models.py    Regulatory models: GuideSection, GuideSnapshot, Bulletin, SectionDiff
  fetcher.py   Bulletin (trigger) + guide snapshot (diff input) fetching
  diff.py      Deterministic section-by-section diff, noise-normalized
  eval.py      RegPulse "section_diff" evaluator + CLI
evals/golden/  Golden eval cases (JSON) — target ~30 over time
examples/      Real worked examples
tests/         Unit tests
```

`regpulse.core` must not import anything regulatory-specific. Once RegPulse and
HazardLens both work end to end, `core/` moves to its own package that both
import, and a supervisor graph treats each project as a sub-agent.

## Roadmap

Ten milestones from this skeleton to a deployed, production-hardened agent:
[docs/ROADMAP.md](docs/ROADMAP.md). How to build it and learn along the way:
[docs/LEARNING.md](docs/LEARNING.md).

## Dev

Working with Claude Code? See [docs/claude-code-setup.md](docs/claude-code-setup.md);
project rules for Claude live in [CLAUDE.md](CLAUDE.md).

```bash
pip install -e ".[dev]"
pytest
python -m regpulse.eval   # run golden evals
```

# Working on RegPulse with Claude Code

A step-by-step guide to open this repo in your IDE and continue Week 1 with
Claude Code. Commands verified against the Claude Code docs (Oct 2026); if
anything differs, the docs win: https://code.claude.com/docs/en/setup

---

## 1. Prerequisites

- A paid Claude plan (Pro, Max, Team, or Enterprise) or a Claude Console
  account. The free plan doesn't include Claude Code.
- Git, Python 3.11+, and VS Code 1.94.0 or later (or Cursor / a JetBrains IDE).
- Optional: AWS Bedrock instead of a Claude subscription — see
  https://code.claude.com/docs/en/amazon-bedrock. Not needed for Week 1.

## 2. Install the Claude Code CLI

macOS / Linux / WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

(Alternatives: `brew install --cask claude-code`,
`winget install Anthropic.ClaudeCode`, or `npm install -g @anthropic-ai/claude-code`
with Node.js 22+. Never use `sudo npm`.)

Open a **new** terminal and check:

```bash
claude --version
claude doctor      # optional: install/settings diagnostics
```

## 3. Clone the repo and set up Python

```bash
git clone https://github.com/subhakarkoduru/regpulse.git
cd regpulse
git checkout week1/shared-core-and-diff   # until the PR is merged; then use main

python -m venv .venv
source .venv/bin/activate                  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q                                  # expect: 21 passed
python -m regpulse.eval                    # expect: "No golden cases found" (for now)
```

## 4. Open it in your IDE with Claude Code

### VS Code (recommended)

1. Open the folder: `code .` (or File → Open Folder → `regpulse`).
2. Install the extension: Extensions view (`Cmd+Shift+X` / `Ctrl+Shift+X`)
   → search **Claude Code** (publisher: Anthropic, id `anthropic.claude-code`)
   → Install.
3. Select the interpreter: Command Palette → *Python: Select Interpreter* →
   choose `.venv`.
4. Open any file, then click the **Spark icon** in the editor toolbar
   (top-right) to open the Claude Code panel. Sign in with your Claude
   account the first time.
5. `Cmd+Esc` / `Ctrl+Esc` toggles focus between the editor and Claude.
   Select code and @-mention it to give Claude exact context.

### Cursor

Same extension: search **Claude Code** in Extensions, or install from the
Open VSX registry.

### JetBrains (PyCharm, IntelliJ)

Install the **Claude Code** plugin from the JetBrains Marketplace, restart the
IDE, then run `claude` in the IDE's built-in terminal.

### Terminal only

From the repo root, just run `claude`. Works in any terminal, including the
IDE's integrated one.

## 5. First session checklist

Claude Code reads `CLAUDE.md` automatically, so it already knows the project,
the Week 1 scope, and the rules. In the first session:

1. Ask: `learning mode. Summarize CLAUDE.md, the CURRENT milestone in
   docs/ROADMAP.md, and the learning loop in docs/LEARNING.md in 5 bullets.`
   Confirm it understood before giving it work.
2. Approve permissions as they come up. Safe to allow for this repo:
   `pytest`, `python -m regpulse.eval`, `pip install -e .`, `git status/diff/add/commit`.
   Keep `git push` on "ask".
3. Use **plan mode** for anything non-trivial: type `/plan <task>` (or cycle
   modes with `Shift+Tab` in the terminal). Review the plan, then approve.

## 6. Ready-to-paste prompts for the rest of Week 1 (M1)

Later milestones (M2–M10) each have their own kickoff prompt in
[ROADMAP.md](ROADMAP.md). Follow the loop in [LEARNING.md](LEARNING.md).

Run them in order. Each one ends with tests passing and a commit on a branch.

### Step 2 — Fetcher (one source)

```
/plan Implement Week 1 step 2 in src/regpulse/fetcher.py for ONE source:
the Fannie Mae Selling Guide announcements page as the bulletin trigger, and
the guide sections it names as GuideSnapshot input.
- First, fetch the public pages, show me the HTML structure you found, and
  propose the parsing approach before writing code.
- Use httpx with a 30s timeout and a descriptive User-Agent; cache raw
  downloads under data/raw/ (add to .gitignore).
- Save 1–2 real downloaded pages as fixtures in tests/fixtures/ and write
  parser tests against them. No network calls in tests.
- Don't add dependencies beyond pyproject.toml without asking.
Branch: week1/fetcher. Run pytest -q at the end and show the output.
```

### Step 4 — First golden cases

```
Build the first 3 golden eval cases in evals/golden/ from REAL past Selling
Guide changes. For each: find the announcement, get the before/after text of
the affected sections (use archived guide editions if needed), and write the
JSON in the format in evals/golden/README.md. Put the source URLs in each
case under a "sources" key. If you can't get verifiable before/after text for
a case, skip it and tell me — do not synthesize text.
Run python -m regpulse.eval and show the output. Branch: week1/golden-cases.
```

### Step 5 — Worked example

```
Fill in examples/worked-example.md end to end using one real bulletin:
run the fetcher, take two guide snapshots, run diff_sections, and paste the
real output into the template sections. For "Downstream impact (draft)", list
which underwriting checks the change would touch, and mark that part clearly
as a hand-written draft. Branch: week1/worked-example.
```

### Wrap-up

```
Review the whole repo against CLAUDE.md's Week 1 "done" definition. List
anything missing, then update the README and CLAUDE.md status table.
```

## 7. Tips

- `/clear` between unrelated tasks to keep context focused.
- `/init` is not needed — `CLAUDE.md` already exists. Edit it as the project
  evolves (update the status table after each step).
- If Claude starts building agents, LLM calls, or a database, it has drifted
  out of Week 1 — stop it and point at CLAUDE.md.
- Commit often; review diffs before approving pushes.

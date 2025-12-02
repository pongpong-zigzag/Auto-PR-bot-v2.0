# Auto PR Bot

Freshly structured toolkit for automating a lightweight GitHub workflow:

- Keep a head branch (default `dev`) alive by cloning it from the base branch when missing
- Overwrite `README.md` on that branch with auto-generated content
- Create and (optionally) merge a PR from head → base, once diffs exist

## Project Layout

```
autopr_bot/
  ├─ bot.py            # GitHub automation logic
  ├─ content.py        # Random content generators
  └─ ui/               # Tkinter desktop experience
main.py                # Backwards-compatible script entry
ui.py                  # Thin launcher for the redesigned UI
```

## Requirements

- Python 3.9+
- `requests` (install via `pip install -r requirements.txt` or `pip install requests`)
- GitHub Personal Access Token (classic) with `repo` scope

## Launch the UI

```bash
python ui.py
```

Highlights:
- Modern dark theme with status badges and live log stream
- Optional co-author section; enable it only when you want `Co-authored-by` lines
- Loop controls with interval spinbox and live indicators
- Preview generator to inspect the random PR/README copy before running anything

## Programmatic Usage

```python
from autopr_bot import AutoPRBot

bot = AutoPRBot(
    token="<YOUR_TOKEN>",
    repo="owner/repo",
    base_branch="main",
    head_branch="dev",
    # co_authors=[{"name": "Ada Lovelace", "email": "ada@example.com"}],
)

bot.run_once()   # Single cycle
# bot.run_loop(120)  # Continuous automation
```

## Automation Flow

1. Ensure the head branch exists (creates it from base if missing).
2. Overwrite `README.md` on the head branch with new random content.
3. If commits exist, open a PR from head → base.
4. Merge the PR automatically if creation succeeds.

## Troubleshooting

- **Validation Failed: No commits between** – nothing changed; either wait or tweak content.
- **404s / 403s** – usually incorrect `owner/repo`, branch names, or token permissions.
- **Merge blocked** – branch protection rules may prevent auto-merges.
- **Rate limits** – widen the loop interval or use fewer API calls.

## Security Notes

- Prefer environment variables or secret managers for tokens; never commit them.
- Limit PAT scopes to `repo`, or less if possible.

## License

MIT

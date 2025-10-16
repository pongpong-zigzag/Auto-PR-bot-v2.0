# Auto PR Bot

Automates a simple GitHub workflow:
- Ensure head branch exists (default `dev`)
- Overwrite `README.md` on head branch
- Create PR from head → base (default `dev` → `main`)
- Auto-merge the PR

## Requirements
- Python 3.8+
- GitHub Personal Access Token (classic) with `repo` scope
- `requests` library (`pip install requests`)

## Quick Start (UI)
```bash
python ui.py
```
Fill in:
- Token: your GitHub PAT
- Username/Owner: e.g., `octocat`
- Repository: e.g., `hello-world`
- Base Branch: e.g., `main`
- Head Branch: e.g., `dev`
- Uptime (seconds): loop interval

Buttons:
- Run Once: single cycle (ensure branch → overwrite README → PR → merge)
- Start Loop: run every N seconds
- Stop Loop: stop background loop

## Programmatic Usage
```python
from main import AutoPRBot

bot = AutoPRBot(
    token="<YOUR_TOKEN>",
    repo="owner/repo",
    base_branch="main",
    head_branch="dev",
)

# Single cycle
bot.run_once()

# Continuous loop every 60 seconds
# bot.run_loop(60)
```

## How It Works
1. If the head branch does not exist, it is created from the base branch
2. `README.md` on the head branch is overwritten using the Contents API
3. If there are diffs, a PR from head → base is created
4. The PR is merged automatically

## Notes & Troubleshooting
- If you see "Validation Failed: No commits between", there were no diffs to PR.
- 404 errors usually indicate wrong `owner/repo`, branch names, or insufficient token permissions.
- Merge may fail if branch protection rules block auto-merge.
- API rate limits: increase the loop interval.

## Security
- Use least-privilege tokens. For private repos, `repo` scope is required.
- Avoid hardcoding tokens; the UI uses in-memory token entry.

## License
MIT

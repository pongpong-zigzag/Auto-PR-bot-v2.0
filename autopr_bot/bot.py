from __future__ import annotations

import base64
import time
from typing import Callable, Dict, List, Optional

import requests

from .content import generate_pr_content, generate_readme_content


class AutoPRBot:
    """High-level helper that keeps a GitHub PR flowing between branches."""

    def __init__(
        self,
        token: str,
        repo: str,
        base_branch: str = "main",
        head_branch: str = "dev",
        logger: Optional[Callable[[str], None]] = None,
        co_authors: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        self.token = token
        self.repo = repo
        self.base_branch = base_branch
        self.head_branch = head_branch
        self.co_authors = co_authors or []
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "auto-pr-bot",
        }
        self.log = logger if logger else print

    # ------------------------------------------------------------------ #
    # Content helpers
    # ------------------------------------------------------------------ #
    def generate_random_content(self) -> Dict[str, object]:
        return generate_pr_content()

    def generate_random_readme_content(self) -> str:
        return generate_readme_content()

    # ------------------------------------------------------------------ #
    # GitHub helpers
    # ------------------------------------------------------------------ #
    def branches_have_diffs(self) -> bool:
        url = f"https://api.github.com/repos/{self.repo}/compare/{self.base_branch}...{self.head_branch}"
        response = requests.get(url, headers=self.headers, timeout=30)
        if not response.ok:
            self.log(f"Failed to compare branches: {response.text}")
            return False
        data = response.json()
        return data.get("ahead_by", 0) > 0

    def ensure_branch_exists(self, branch: str) -> bool:
        url_ref = f"https://api.github.com/repos/{self.repo}/git/ref/heads/{branch}"
        response = requests.get(url_ref, headers=self.headers, timeout=30)
        if response.ok:
            return True
        if response.status_code != 404:
            self.log(f"Failed to check branch: {response.text}")
            return False

        base_ref_url = f"https://api.github.com/repos/{self.repo}/git/ref/heads/{self.base_branch}"
        base_ref = requests.get(base_ref_url, headers=self.headers, timeout=30)
        if not base_ref.ok:
            self.log(f"Failed to get base branch ref: {base_ref.text}")
            return False
        base_sha = base_ref.json().get("object", {}).get("sha")
        if not base_sha:
            self.log("Base branch SHA not found")
            return False

        create_ref_url = f"https://api.github.com/repos/{self.repo}/git/refs"
        payload = {"ref": f"refs/heads/{branch}", "sha": base_sha}
        created = requests.post(create_ref_url, headers=self.headers, json=payload, timeout=30)
        if not created.ok:
            self.log(f"Failed to create branch: {created.text}")
            return False

        self.log(f"Created branch {branch} from {self.base_branch}")
        return True

    def update_readme_on_branch(self, branch: str) -> bool:
        path = "README.md"
        new_content = self.generate_random_readme_content()
        get_url = f"https://api.github.com/repos/{self.repo}/contents/{path}?ref={branch}"
        response = requests.get(get_url, headers=self.headers, timeout=30)

        sha = None
        if response.status_code == 200:
            data = response.json()
            sha = data.get("sha")
        elif response.status_code != 404 and not response.ok:
            self.log(f"Failed to fetch README: {response.text}")
            return False

        encoded_content = base64.b64encode(new_content.encode()).decode()
        put_url = f"https://api.github.com/repos/{self.repo}/contents/{path}"

        commit_message = "chore: overwrite README via auto-update"
        if self.co_authors:
            co_author_lines = [
                f"Co-authored-by: {author['name']} <{author['email']}>"
                for author in self.co_authors
                if author.get("name") and author.get("email")
            ]
            if co_author_lines:
                commit_message += "\n\n" + "\n".join(co_author_lines)

        payload = {
            "message": commit_message,
            "content": encoded_content,
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        put_response = requests.put(put_url, headers=self.headers, json=payload, timeout=30)
        if not put_response.ok:
            self.log(f"Failed to update README: {put_response.text}")
            return False

        self.log(f"Updated {path} on {branch}")
        return True

    def create_pull_request(self) -> Optional[int]:
        url = f"https://api.github.com/repos/{self.repo}/pulls"
        random_content = self.generate_random_content()
        data = {
            "title": random_content["title"],
            "head": self.head_branch,
            "base": self.base_branch,
        }
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        if response.status_code == 422:
            text = response.text
            if "A pull request already exists" in text:
                self.log("PR already exists, skipping.")
                return None
            if "No commits between" in text:
                self.log("No commits between branches, skipping PR creation.")
                return None

        if response.ok:
            pr = response.json()
            self.log(f"Created PR #{pr['number']}")
            return pr["number"]

        self.log(f"Failed to create PR: {response.text}")
        return None

    def merge_pull_request(self, pr_number: int) -> None:
        url = f"https://api.github.com/repos/{self.repo}/pulls/{pr_number}/merge"
        data = {"merge_method": "merge"}
        response = requests.put(url, headers=self.headers, json=data, timeout=30)
        if response.ok:
            self.log(f"Merged PR #{pr_number}")
        else:
            self.log(f"Failed to merge PR #{pr_number}: {response.text}")

    def get_open_pr(self) -> Optional[int]:
        owner = self.repo.split("/")[0]
        url = f"https://api.github.com/repos/{self.repo}/pulls?head={owner}:{self.head_branch}&base={self.base_branch}&state=open"
        response = requests.get(url, headers=self.headers, timeout=30)
        if response.ok:
            prs = response.json()
            if prs:
                return prs[0]["number"]
        return None

    # ------------------------------------------------------------------ #
    # Workflows
    # ------------------------------------------------------------------ #
    def run_once(self) -> None:
        if not self.token:
            raise ValueError("❌ Please provide a GITHUB_TOKEN")
        if not self.ensure_branch_exists(self.head_branch):
            raise SystemExit(1)
        if not self.update_readme_on_branch(self.head_branch):
            raise SystemExit(1)

        self.log("\n=== Checking for PRs ===")
        pr_number = self.get_open_pr()
        if pr_number:
            self.log(f"Found existing PR #{pr_number}, merging...")
            self.merge_pull_request(pr_number)
            return

        if not self.branches_have_diffs():
            self.log("No diffs between dev and main. Skipping PR.")
            return

        self.log("No PR found, creating one...")
        new_pr = self.create_pull_request()
        if new_pr:
            self.merge_pull_request(new_pr)

    def run_loop(self, interval_seconds: int) -> None:
        while True:
            try:
                self.run_once()
            except Exception as exc:
                self.log(f"Error: {exc}")
            time.sleep(interval_seconds)

    # ------------------------------------------------------------------ #
    # Debug helpers
    # ------------------------------------------------------------------ #
    def display_random_content(self) -> None:
        self.log("\n" + "=" * 80)
        self.log("RANDOM PR CONTENT GENERATED")
        self.log("=" * 80)
        random_content = self.generate_random_content()
        self.log(f"\nTitle: {random_content['title']}")
        self.log(f"\nBody:\n{random_content['body']}")
        self.log(f"\nWords Used: {random_content['words_used']}")
        self.log(f"\nAll Words: {', '.join(random_content['all_words'])}")

        self.log("\n" + "=" * 80)
        self.log("RANDOM README CONTENT GENERATED")
        self.log("=" * 80)
        readme_content = self.generate_random_readme_content()
        self.log(f"\n{readme_content}")



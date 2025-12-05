from __future__ import annotations

import base64
import random
import time
from datetime import datetime, timedelta
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
        commit_author_date: Optional[str] = None,
        commit_committer_date: Optional[str] = None,
        commit_author_name: Optional[str] = None,
        commit_author_email: Optional[str] = None,
    ) -> None:
        self.token = token
        self.repo = repo
        self.base_branch = base_branch
        self.head_branch = head_branch
        self.co_authors = co_authors or []
        self.commit_author_date = commit_author_date
        self.commit_committer_date = commit_committer_date
        self.commit_author_name = commit_author_name
        self.commit_author_email = commit_author_email
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
    def _get_authenticated_user(self) -> Dict[str, str]:
        """Fetch the authenticated user's information from GitHub."""
        url = "https://api.github.com/user"
        response = requests.get(url, headers=self.headers, timeout=30)
        if not response.ok:
            self.log(f"Failed to fetch user info: {response.text}")
            return {"name": "Unknown", "email": ""}
        data = response.json()
        # Try to get email from user's public emails endpoint
        emails_url = "https://api.github.com/user/emails"
        emails_response = requests.get(emails_url, headers=self.headers, timeout=30)
        email = ""
        if emails_response.ok:
            emails = emails_response.json()
            # Find primary email or first verified email
            primary = next((e for e in emails if e.get("primary")), None)
            verified = next((e for e in emails if e.get("verified")), None)
            if primary:
                email = primary.get("email", "")
            elif verified:
                email = verified.get("email", "")
            elif emails:
                email = emails[0].get("email", "")
        
        # Use GitHub's no-reply email as fallback if no email found
        if not email:
            username = data.get("login", "")
            email = f"{username}@users.noreply.github.com"
        
        return {
            "name": data.get("name") or data.get("login", "Unknown"),
            "email": email,
        }
    
    def _generate_random_date(self, days_back: int = 365, days_forward: int = 0) -> str:
        """Generate a random date string in ISO 8601 format for GitHub API."""
        # Generate random date within specified range
        end_date = datetime.utcnow() + timedelta(days=days_forward)
        start_date = end_date - timedelta(days=days_back)
        
        # Random time between start and end
        time_between = (end_date - start_date).total_seconds()
        random_seconds = random.uniform(0, time_between)
        random_date = start_date + timedelta(seconds=random_seconds)
        
        # Format as ISO 8601 with Z timezone
        return random_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _generate_random_date_between(self, start_year: int = 2022, end_date: Optional[datetime] = None) -> str:
        """Generate a random date between start_year (January 1st) and end_date (defaults to yesterday to ensure past dates)."""
        if end_date is None:
            # Use yesterday to ensure commit date is always in the past (not today)
            end_date = datetime.utcnow() - timedelta(days=1)
            # Set to end of yesterday (23:59:59)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
        else:
            # If end_date is provided, ensure it's at least 1 day before today
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            if end_date >= today:
                end_date = today - timedelta(days=1)
                end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
        
        start_date = datetime(start_year, 1, 1, 0, 0, 0)
        
        # Ensure start_date is before end_date
        if start_date >= end_date:
            # If start_date is same or after end_date, move end_date back
            end_date = start_date + timedelta(days=1)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
        
        # Random time between start and end (inclusive of start, exclusive of end to ensure past)
        time_between = (end_date - start_date).total_seconds()
        # Use a small buffer to ensure we never hit the exact end_date
        random_seconds = random.uniform(0, max(1, time_between - 1))
        random_date = start_date + timedelta(seconds=random_seconds)
        
        # Ensure random_date is still before end_date
        if random_date >= end_date:
            random_date = end_date - timedelta(seconds=1)
        
        # Format as ISO 8601 with Z timezone
        return random_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _format_date_for_api(self, date_str: str) -> str:
        """Format date string to ISO 8601 format with timezone for GitHub API."""
        if not date_str:
            return date_str
        
        # If already has timezone indicator, return as-is
        if date_str.endswith(("Z", "+", "-")) or "+" in date_str[-6:]:
            return date_str
        
        # Try to parse and format the date
        try:
            # Try ISO format first (e.g., "2024-01-02T15:04:05")
            if "T" in date_str:
                # Parse ISO format
                if date_str.endswith("Z"):
                    return date_str
                # Try parsing with timezone info
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    # No timezone, parse as naive datetime
                    dt = datetime.fromisoformat(date_str)
            else:
                # Try other common formats
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            
            # Convert to ISO format with Z timezone (UTC)
            # If datetime is naive (no timezone), assume it's already in desired timezone
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, AttributeError) as e:
            # If parsing fails, add Z suffix if not present (assume UTC)
            if not date_str.endswith("Z"):
                return date_str + "Z"
            return date_str

    def branches_have_diffs(self) -> bool:
        url = f"https://api.github.com/repos/{self.repo}/compare/{self.base_branch}...{self.head_branch}"
        response = requests.get(url, headers=self.headers, timeout=30)
        if not response.ok:
            self.log(f"Failed to compare branches: {response.text}")
            return False
        data = response.json()
        return data.get("ahead_by", 0) > 0

    def ensure_branch_exists(self, branch: str) -> bool:
        """Ensure the branch exists, creating it from base branch if it doesn't."""
        url_ref = f"https://api.github.com/repos/{self.repo}/git/ref/heads/{branch}"
        response = requests.get(url_ref, headers=self.headers, timeout=30)
        
        # Branch already exists
        if response.ok:
            self.log(f"Branch '{branch}' already exists")
            return True
        
        # Error other than "not found"
        if response.status_code != 404:
            error_text = response.text
            try:
                error_json = response.json()
                error_message = error_json.get("message", error_text)
            except:
                error_message = error_text
            self.log(f"Failed to check branch '{branch}': {error_message}")
            return False

        # Branch doesn't exist, create it from base branch
        self.log(f"Branch '{branch}' does not exist, creating from '{self.base_branch}'...")
        
        # Get base branch SHA
        base_ref_url = f"https://api.github.com/repos/{self.repo}/git/ref/heads/{self.base_branch}"
        base_ref = requests.get(base_ref_url, headers=self.headers, timeout=30)
        if not base_ref.ok:
            error_text = base_ref.text
            try:
                error_json = base_ref.json()
                error_message = error_json.get("message", error_text)
            except:
                error_message = error_text
            self.log(f"❌ Failed to get base branch '{self.base_branch}': {error_message}")
            self.log(f"   Please verify that the base branch '{self.base_branch}' exists in the repository.")
            return False
        
        base_sha = base_ref.json().get("object", {}).get("sha")
        if not base_sha:
            self.log(f"❌ Base branch '{self.base_branch}' SHA not found in response")
            return False

        self.log(f"   Using base branch SHA: {base_sha[:7]}...")

        # Create the new branch
        create_ref_url = f"https://api.github.com/repos/{self.repo}/git/refs"
        payload = {"ref": f"refs/heads/{branch}", "sha": base_sha}
        created = requests.post(create_ref_url, headers=self.headers, json=payload, timeout=30)
        
        if not created.ok:
            error_text = created.text
            error_message = error_text
            try:
                error_json = created.json()
                error_message = error_json.get("message", error_text)
            except:
                pass
            
            # Check if branch already exists (race condition)
            if created.status_code == 422:
                # Verify if branch exists now (might have been created concurrently)
                verify_response = requests.get(url_ref, headers=self.headers, timeout=30)
                if verify_response.ok:
                    self.log(f"✓ Branch '{branch}' exists now (may have been created concurrently)")
                    return True
                else:
                    # Check if maybe the branch name format is wrong or branch exists with different name
                    self.log(f"❌ Failed to create branch '{branch}': {error_message}")
                    self.log(f"   Error code: 422 - Possible causes:")
                    self.log(f"   1. Branch '{branch}' already exists (check on GitHub)")
                    self.log(f"   2. Base branch '{self.base_branch}' or SHA {base_sha[:7]}... is invalid")
                    self.log(f"   3. Branch name contains invalid characters")
                    self.log(f"   4. Insufficient permissions (token needs 'repo' scope)")
                    self.log(f"   Please verify the branch doesn't exist and try again.")
                    return False
            else:
                self.log(f"❌ Failed to create branch '{branch}': {error_message}")
                return False

        self.log(f"✓ Successfully created branch '{branch}' from '{self.base_branch}'")
        return True

    def update_readme_on_branch(self, branch: str) -> bool:
        """
        Update README.md on the branch using Git Data API to support custom commit dates.
        This method creates commits with custom author/committer dates that will be
        displayed correctly on GitHub.
        """
        path = "README.md"
        new_content = self.generate_random_readme_content()
        
        # Always set author to owner and use random commit dates
        user_info = self._get_authenticated_user()
        author_name = self.commit_author_name or user_info["name"]
        author_email = self.commit_author_email or user_info["email"]
        
        # Generate random commit dates (between 2022 and yesterday, or use custom if specified)
        # Dates are always in the past to ensure commits appear as historical
        if self.commit_author_date:
            formatted_author_date = self._format_date_for_api(self.commit_author_date)
        else:
            # Generate random date between 2022-01-01 and yesterday (ensures past date)
            formatted_author_date = self._generate_random_date_between(
                start_year=2022, 
                end_date=None  # None uses default: yesterday to ensure past date
            )
        
        if self.commit_committer_date:
            formatted_committer_date = self._format_date_for_api(self.commit_committer_date)
        elif self.commit_author_date:
            # If only author_date is set manually, use same for committer
            formatted_committer_date = formatted_author_date
        else:
            # Generate random committer date between 2022 and yesterday (ensures past date)
            formatted_committer_date = self._generate_random_date_between(
                start_year=2022,
                end_date=None  # None uses default: yesterday to ensure past date
            )
        
        # Log the generated commit dates in a readable format for UI display
        try:
            author_dt = datetime.strptime(formatted_author_date, "%Y-%m-%dT%H:%M:%SZ")
            committer_dt = datetime.strptime(formatted_committer_date, "%Y-%m-%dT%H:%M:%SZ")
            author_formatted = author_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            committer_formatted = committer_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            author_formatted = formatted_author_date
            committer_formatted = formatted_committer_date
        
        self.log("")
        self.log("═══════════════════════════════════════════════════════════")
        self.log("📅 COMMIT DATE INFORMATION")
        self.log("═══════════════════════════════════════════════════════════")
        self.log(f"   Author Date:    {author_formatted}")
        self.log(f"   Committer Date: {committer_formatted}")
        self.log("═══════════════════════════════════════════════════════════")
        self.log("")
        
        # Use Git Data API to create commit with custom dates
        # Step 1: Get the current commit SHA for the branch
        ref_url = f"https://api.github.com/repos/{self.repo}/git/ref/heads/{branch}"
        ref_response = requests.get(ref_url, headers=self.headers, timeout=30)
        if not ref_response.ok:
            self.log(f"Failed to get branch ref: {ref_response.text}")
            return False
        
        current_commit_sha = ref_response.json()["object"]["sha"]
        
        # Step 2: Get the commit object to get the tree SHA
        commit_url = f"https://api.github.com/repos/{self.repo}/git/commits/{current_commit_sha}"
        commit_response = requests.get(commit_url, headers=self.headers, timeout=30)
        if not commit_response.ok:
            self.log(f"Failed to get commit: {commit_response.text}")
            return False
        
        base_tree_sha = commit_response.json()["tree"]["sha"]
        
        # Step 3: Get the current tree to find existing file entries
        tree_url = f"https://api.github.com/repos/{self.repo}/git/trees/{base_tree_sha}?recursive=1"
        tree_response = requests.get(tree_url, headers=self.headers, timeout=30)
        if not tree_response.ok:
            self.log(f"Failed to get tree: {tree_response.text}")
            return False
        
        tree_data = tree_response.json()
        tree_entries = tree_data.get("tree", [])
        
        # Step 4: Create a blob with the new content
        blob_content = base64.b64encode(new_content.encode()).decode()
        blob_url = f"https://api.github.com/repos/{self.repo}/git/blobs"
        blob_payload = {"content": blob_content, "encoding": "base64"}
        blob_response = requests.post(blob_url, headers=self.headers, json=blob_payload, timeout=30)
        if not blob_response.ok:
            self.log(f"Failed to create blob: {blob_response.text}")
            return False
        
        new_blob_sha = blob_response.json()["sha"]
        
        # Step 5: Create a new tree with the updated file
        # Keep existing tree entries, but replace the README.md entry
        new_tree_entries = []
        readme_updated = False
        for entry in tree_entries:
            if entry.get("path") == path:
                # Replace existing README.md entry
                new_tree_entries.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": new_blob_sha
                })
                readme_updated = True
            elif entry.get("type") == "blob":
                # Keep other blob entries
                new_tree_entries.append({
                    "path": entry["path"],
                    "mode": entry["mode"],
                    "type": entry["type"],
                    "sha": entry["sha"]
                })
        
        # If README.md doesn't exist yet, add it
        if not readme_updated:
            new_tree_entries.append({
                "path": path,
                "mode": "100644",
                "type": "blob",
                "sha": new_blob_sha
            })
        
        # Create the new tree
        create_tree_url = f"https://api.github.com/repos/{self.repo}/git/trees"
        tree_payload = {"base_tree": base_tree_sha, "tree": new_tree_entries}
        create_tree_response = requests.post(create_tree_url, headers=self.headers, json=tree_payload, timeout=30)
        if not create_tree_response.ok:
            self.log(f"Failed to create tree: {create_tree_response.text}")
            return False
        
        new_tree_sha = create_tree_response.json()["sha"]
        
        # Step 6: Create commit message
        commit_message = "chore: overwrite README via auto-update"
        if self.co_authors:
            co_author_lines = [
                f"Co-authored-by: {author['name']} <{author['email']}>"
                for author in self.co_authors
                if author.get("name") and author.get("email")
            ]
            if co_author_lines:
                commit_message += "\n\n" + "\n".join(co_author_lines)
        
        # Step 7: Create a new commit with custom author/committer dates
        create_commit_url = f"https://api.github.com/repos/{self.repo}/git/commits"
        commit_payload = {
            "message": commit_message,
            "tree": new_tree_sha,
            "parents": [current_commit_sha],
            "author": {
                "name": author_name,
                "email": author_email,
                "date": formatted_author_date,
            },
            "committer": {
                "name": author_name,
                "email": author_email,
                "date": formatted_committer_date,
            }
        }
        
        create_commit_response = requests.post(create_commit_url, headers=self.headers, json=commit_payload, timeout=30)
        if not create_commit_response.ok:
            self.log(f"Failed to create commit: {create_commit_response.text}")
            return False
        
        new_commit_sha = create_commit_response.json()["sha"]
        
        # Step 8: Update the branch reference to point to the new commit
        update_ref_url = f"https://api.github.com/repos/{self.repo}/git/refs/heads/{branch}"
        update_ref_payload = {"sha": new_commit_sha}
        update_ref_response = requests.patch(update_ref_url, headers=self.headers, json=update_ref_payload, timeout=30)
        if not update_ref_response.ok:
            self.log(f"Failed to update branch ref: {update_ref_response.text}")
            return False
        
        self.log(f"Updated {path} on {branch} with custom commit dates")
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



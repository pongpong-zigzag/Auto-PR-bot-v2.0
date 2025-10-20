import time
import requests
import base64
import random
from datetime import datetime, timezone
from typing import Callable, Optional # seconds

# === CODING WORDS FOR RANDOM CONTENT ===
CODING_WORDS = [
    "algorithm", "array", "boolean", "class", "compiler", "debugger", "function",
    "variable", "string", "integer", "object", "method", "parameter", "return",
    "loop", "condition", "statement", "expression", "operator", "syntax", "semantic",
    "recursion", "iteration", "inheritance", "polymorphism", "encapsulation", "abstraction",
    "interface", "implementation", "constructor", "destructor", "pointer", "reference",
    "memory", "allocation", "deallocation", "garbage", "collection", "optimization",
    "performance", "efficiency", "complexity", "asymptotic", "big", "notation",
    "data", "structure", "stack", "queue", "tree", "graph", "hash", "table",
    "binary", "search", "sorting", "bubble", "merge", "quick", "heap", "radix",
    "database", "query", "sql", "schema", "table", "index", "transaction", "commit",
    "rollback", "concurrency", "threading", "synchronization", "mutex", "semaphore",
    "deadlock", "race", "condition", "parallel", "distributed", "microservice",
    "api", "rest", "json", "xml", "http", "https", "endpoint", "request", "response",
    "authentication", "authorization", "encryption", "decryption", "security", "vulnerability",
    "testing", "unit", "integration", "regression", "coverage", "mock", "stub", "fixture",
    "deployment", "ci", "cd", "pipeline", "docker", "kubernetes", "container", "orchestration"
]

# === HEADERS ===
class AutoPRBot:
    def __init__(self, token: str, repo: str, base_branch: str = "main", head_branch: str = "dev", logger: Optional[Callable[[str], None]] = None, co_authors: Optional[list] = None):
        self.token = token
        self.repo = repo
        self.base_branch = base_branch
        self.head_branch = head_branch
        self.co_authors = co_authors or []  # List of co-author info: [{"name": "John Doe", "email": "john@example.com"}]
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "auto-pr-bot"
        }
        self.log = logger if logger else print

    def generate_random_content(self) -> dict:
        """Generate random PR content using coding words"""
        selected_words = random.sample(CODING_WORDS, min(50, len(CODING_WORDS)))
        
        # Generate title
        title_words = random.sample(selected_words, 3)
        title = f"feat: implement {title_words[0]} {title_words[1]} {title_words[2]} optimization"
        
        # Generate body content
        what_changed = f"""
## What Changed
- Enhanced {random.choice(selected_words)} {random.choice(selected_words)} processing
- Improved {random.choice(selected_words)} {random.choice(selected_words)} performance
- Added {random.choice(selected_words)} {random.choice(selected_words)} validation
- Refactored {random.choice(selected_words)} {random.choice(selected_words)} logic
- Updated {random.choice(selected_words)} {random.choice(selected_words)} configuration
"""
        
        tech_details = f"""
## Technical Details
This PR introduces significant improvements to the {random.choice(selected_words)} {random.choice(selected_words)} system:

- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Implemented advanced {random.choice(selected_words)} {random.choice(selected_words)} algorithms
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Enhanced {random.choice(selected_words)} {random.choice(selected_words)} processing capabilities  
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Optimized {random.choice(selected_words)} {random.choice(selected_words)} performance metrics
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Added robust {random.choice(selected_words)} {random.choice(selected_words)} error handling
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Improved {random.choice(selected_words)} {random.choice(selected_words)} security protocols

The implementation leverages modern {random.choice(selected_words)} {random.choice(selected_words)} patterns and follows best practices for {random.choice(selected_words)} {random.choice(selected_words)} development.
"""
        
        performance = f"""
## Performance Improvements
- Reduced {random.choice(selected_words)} {random.choice(selected_words)} latency by 40%
- Optimized {random.choice(selected_words)} {random.choice(selected_words)} memory usage
- Enhanced {random.choice(selected_words)} {random.choice(selected_words)} throughput
- Improved {random.choice(selected_words)} {random.choice(selected_words)} scalability
- Streamlined {random.choice(selected_words)} {random.choice(selected_words)} operations
"""
        
        testing = f"""
## Testing
- Added comprehensive {random.choice(selected_words)} {random.choice(selected_words)} unit tests
- Implemented {random.choice(selected_words)} {random.choice(selected_words)} integration tests
- Enhanced {random.choice(selected_words)} {random.choice(selected_words)} regression testing
- Improved {random.choice(selected_words)} {random.choice(selected_words)} test coverage
- Added {random.choice(selected_words)} {random.choice(selected_words)} performance benchmarks
"""
        
        code_quality = f"""
## Code Quality
- Applied {random.choice(selected_words)} {random.choice(selected_words)} design patterns
- Implemented {random.choice(selected_words)} {random.choice(selected_words)} best practices
- Enhanced {random.choice(selected_words)} {random.choice(selected_words)} documentation
- Improved {random.choice(selected_words)} {random.choice(selected_words)} maintainability
- Added {random.choice(selected_words)} {random.choice(selected_words)} type safety
"""
        
        footer_words = random.sample(selected_words, 10)
        footer = f"""
---
**Generated**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
"""
        
        body = what_changed + tech_details + performance + testing + code_quality + footer
        
        return {
            "title": title,
            "body": body,
            "words_used": len(selected_words),
            "all_words": selected_words
        }

    def generate_random_readme_content(self) -> str:
        """Generate random README content using coding words"""
        selected_words = random.sample(CODING_WORDS, min(30, len(CODING_WORDS)))
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        
        content = f"""# Auto-Generated README

This file was auto-updated on {timestamp}.

## Project Overview
This repository demonstrates automated {random.choice(selected_words)} {random.choice(selected_words)} workflows using advanced {random.choice(selected_words)} {random.choice(selected_words)} techniques.

## Features
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Implements robust {random.choice(selected_words)} {random.choice(selected_words)} processing
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Enhanced {random.choice(selected_words)} {random.choice(selected_words)} performance optimization
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Advanced {random.choice(selected_words)} {random.choice(selected_words)} error handling
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Secure {random.choice(selected_words)} {random.choice(selected_words)} authentication
- **{random.choice(selected_words).title()} {random.choice(selected_words).title()}**: Efficient {random.choice(selected_words)} {random.choice(selected_words)} data structures

## Technical Implementation
The system utilizes modern {random.choice(selected_words)} {random.choice(selected_words)} patterns and follows industry best practices for {random.choice(selected_words)} {random.choice(selected_words)} development.

## Performance Metrics
- Optimized {random.choice(selected_words)} {random.choice(selected_words)} algorithms
- Enhanced {random.choice(selected_words)} {random.choice(selected_words)} memory management
- Improved {random.choice(selected_words)} {random.choice(selected_words)} scalability
- Streamlined {random.choice(selected_words)} {random.choice(selected_words)} operations

## Random Coding Terms
{', '.join(random.sample(selected_words, 15))}

---
*This content was generated using 100 random coding-related words*
"""
        return content

    def branches_have_diffs(self) -> bool:
        url = f"https://api.github.com/repos/{self.repo}/compare/{self.base_branch}...{self.head_branch}"
        r = requests.get(url, headers=self.headers)
        if not r.ok:
            self.log(f"Failed to compare branches: {r.text}")
            return False
        data = r.json()
        return data.get("ahead_by", 0) > 0

    def ensure_branch_exists(self, branch: str) -> bool:
        url_ref = f"https://api.github.com/repos/{self.repo}/git/ref/heads/{branch}"
        r = requests.get(url_ref, headers=self.headers)
        if r.ok:
            return True
        if r.status_code != 404:
            self.log(f"Failed to check branch: {r.text}")
            return False
        base_ref_url = f"https://api.github.com/repos/{self.repo}/git/ref/heads/{self.base_branch}"
        base_ref = requests.get(base_ref_url, headers=self.headers)
        if not base_ref.ok:
            self.log(f"Failed to get base branch ref: {base_ref.text}")
            return False
        base_sha = base_ref.json().get("object", {}).get("sha")
        if not base_sha:
            self.log("Base branch SHA not found")
            return False
        create_ref_url = f"https://api.github.com/repos/{self.repo}/git/refs"
        payload = {"ref": f"refs/heads/{branch}", "sha": base_sha}
        created = requests.post(create_ref_url, headers=self.headers, json=payload)
        if not created.ok:
            self.log(f"Failed to create branch: {created.text}")
            return False
        self.log(f"Created branch {branch} from {self.base_branch}")
        return True

    def update_readme_on_branch(self, branch: str) -> bool:
        path = "README.md"
        # Generate random content using coding words
        new_content = self.generate_random_readme_content()
        get_url = f"https://api.github.com/repos/{self.repo}/contents/{path}?ref={branch}"
        r = requests.get(get_url, headers=self.headers)
        existing_content_decoded = ""
        sha = None
        if r.status_code == 200:
            data = r.json()
            sha = data.get("sha")
            # We ignore previous content on purpose; we only need SHA to update
        elif r.status_code != 404 and not r.ok:
            self.log(f"Failed to fetch README: {r.text}")
            return False
        encoded = base64.b64encode(new_content.encode()).decode()
        put_url = f"https://api.github.com/repos/{self.repo}/contents/{path}"
        
        # Build commit message with co-authors
        commit_message = "chore: overwrite README via auto-update"
        if self.co_authors:
            co_author_lines = []
            for co_author in self.co_authors:
                co_author_lines.append(f"Co-authored-by: {co_author['name']} <{co_author['email']}>")
            commit_message += "\n\n" + "\n".join(co_author_lines)
        
        payload = {
            "message": commit_message,
            "content": encoded,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha
        put = requests.put(put_url, headers=self.headers, json=payload)
        if not put.ok:
            self.log(f"Failed to update README: {put.text}")
            return False
        self.log(f"Updated {path} on {branch}")
        return True

    def create_pull_request(self) -> Optional[int]:
        url = f"https://api.github.com/repos/{self.repo}/pulls"
        
        # Generate random PR content
        random_content = self.generate_random_content()
        
        data = {
            "title": random_content["title"],
            "head": self.head_branch,
            "base": self.base_branch,
            "body": pr_body
        }
        response = requests.post(url, headers=self.headers, json=data)
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
        else:
            self.log(f"Failed to create PR: {response.text}")
            return None

    def merge_pull_request(self, pr_number: int) -> None:
        url = f"https://api.github.com/repos/{self.repo}/pulls/{pr_number}/merge"
        data = {"merge_method": "merge"}
        response = requests.put(url, headers=self.headers, json=data)
        if response.ok:
            self.log(f"Merged PR #{pr_number}")
        else:
            self.log(f"Failed to merge PR #{pr_number}: {response.text}")

    def get_open_pr(self) -> Optional[int]:
        owner = self.repo.split('/')[0]
        url = f"https://api.github.com/repos/{self.repo}/pulls?head={owner}:{self.head_branch}&base={self.base_branch}&state=open"
        r = requests.get(url, headers=self.headers)
        if r.ok and len(r.json()) > 0:
            return r.json()[0]["number"]
        return None

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
        else:
            if not self.branches_have_diffs():
                self.log("No diffs between dev and main. Skipping PR.")
            else:
                self.log("No PR found, creating one...")
                new_pr = self.create_pull_request()
                if new_pr:
                    self.merge_pull_request(new_pr)

    def display_random_content(self) -> None:
        """Display generated random content for preview"""
        self.log("\n" + "="*80)
        self.log("RANDOM PR CONTENT GENERATED")
        self.log("="*80)
        
        random_content = self.generate_random_content()
        self.log(f"\nTitle: {random_content['title']}")
        self.log(f"\nBody:\n{random_content['body']}")
        self.log(f"\nWords Used: {random_content['words_used']}")
        self.log(f"\nAll Words: {', '.join(random_content['all_words'])}")
        
        self.log("\n" + "="*80)
        self.log("RANDOM README CONTENT GENERATED")
        self.log("="*80)
        readme_content = self.generate_random_readme_content()
        self.log(f"\n{readme_content}")

    def run_loop(self, interval_seconds: int) -> None:
        while True:
            try:
                self.run_once()
            except Exception as e:
                self.log(f"Error: {e}")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    # Example with co-authors
    co_authors = [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"}
    ]
    
    # Set your GitHub token and repository here
    GITHUB_TOKEN = "your_token_here"
    REPO = "owner/repo"
    BASE_BRANCH = "main"
    HEAD_BRANCH = "dev"
    
    bot = AutoPRBot(
        token=GITHUB_TOKEN,
        repo=REPO,
        base_branch=BASE_BRANCH,
        head_branch=HEAD_BRANCH,
        co_authors=co_authors
    )
    
    # Display random content generation
    bot.display_random_content()
    
    # Uncomment the line below to run the actual bot
    # bot.run_once()

import random
from datetime import datetime, timezone
from typing import Dict, List


CODING_WORDS: List[str] = [
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
    "deployment", "ci", "cd", "pipeline", "docker", "kubernetes", "container", "orchestration",
]


def _select_words(sample_size: int) -> List[str]:
    return random.sample(CODING_WORDS, min(sample_size, len(CODING_WORDS)))


def generate_pr_content() -> Dict[str, object]:
    """Generate a pseudo-random pull request title and body."""
    selected_words = _select_words(50)
    title_words = random.sample(selected_words, 3)
    title = f"feat: implement {title_words[0]} {title_words[1]} {title_words[2]} optimization"

    def _section(name: str, lines: List[str]) -> str:
        return f"\n## {name}\n" + "\n".join(f"- {line}" for line in lines) + "\n"

    what_changed = _section(
        "What Changed",
        [
            f"Enhanced {random.choice(selected_words)} {random.choice(selected_words)} processing",
            f"Improved {random.choice(selected_words)} {random.choice(selected_words)} performance",
            f"Added {random.choice(selected_words)} {random.choice(selected_words)} validation",
            f"Refactored {random.choice(selected_words)} {random.choice(selected_words)} logic",
            f"Updated {random.choice(selected_words)} {random.choice(selected_words)} configuration",
        ],
    )

    technical_details = """
## Technical Details
This PR introduces significant improvements to the {0} {1} system:

- **{2} {3}**: Implemented advanced {4} {5} algorithms
- **{6} {7}**: Enhanced {8} {9} processing capabilities
- **{10} {11}**: Optimized {12} {13} performance metrics
- **{14} {15}**: Added robust {16} {17} error handling
- **{18} {19}**: Improved {20} {21} security protocols

The implementation leverages modern {22} {23} patterns and follows best practices for {24} {25} development.
""".format(*(random.choice(selected_words) for _ in range(26)))

    performance = _section(
        "Performance Improvements",
        [
            f"Reduced {random.choice(selected_words)} {random.choice(selected_words)} latency by 40%",
            f"Optimized {random.choice(selected_words)} {random.choice(selected_words)} memory usage",
            f"Enhanced {random.choice(selected_words)} {random.choice(selected_words)} throughput",
            f"Improved {random.choice(selected_words)} {random.choice(selected_words)} scalability",
            f"Streamlined {random.choice(selected_words)} {random.choice(selected_words)} operations",
        ],
    )

    testing = _section(
        "Testing",
        [
            f"Added comprehensive {random.choice(selected_words)} {random.choice(selected_words)} unit tests",
            f"Implemented {random.choice(selected_words)} {random.choice(selected_words)} integration tests",
            f"Enhanced {random.choice(selected_words)} {random.choice(selected_words)} regression testing",
            f"Improved {random.choice(selected_words)} {random.choice(selected_words)} test coverage",
            f"Added {random.choice(selected_words)} {random.choice(selected_words)} performance benchmarks",
        ],
    )

    code_quality = _section(
        "Code Quality",
        [
            f"Applied {random.choice(selected_words)} {random.choice(selected_words)} design patterns",
            f"Implemented {random.choice(selected_words)} {random.choice(selected_words)} best practices",
            f"Enhanced {random.choice(selected_words)} {random.choice(selected_words)} documentation",
            f"Improved {random.choice(selected_words)} {random.choice(selected_words)} maintainability",
            f"Added {random.choice(selected_words)} {random.choice(selected_words)} type safety",
        ],
    )

    footer = f"""
---
**Generated**: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
"""

    return {
        "title": title,
        "body": what_changed + technical_details + performance + testing + code_quality + footer,
        "words_used": len(selected_words),
        "all_words": selected_words,
    }


def generate_readme_content() -> str:
    """Generate random README content."""
    selected_words = _select_words(30)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

    content = f"""# Generated README

This file was updated on {timestamp}.

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

"""
    return content


__all__ = ["CODING_WORDS", "generate_pr_content", "generate_readme_content"]



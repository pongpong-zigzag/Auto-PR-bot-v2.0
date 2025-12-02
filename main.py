"""Backwards-compatible entry point for the Auto PR Bot."""

from autopr_bot import AutoPRBot


def main() -> None:
    """Demonstrate the bot with placeholder values."""
    bot = AutoPRBot(
        token="your_token_here",
        repo="owner/repo",
        base_branch="main",
        head_branch="dev",
    )
    bot.display_random_content()
    

if __name__ == "__main__":
    main()

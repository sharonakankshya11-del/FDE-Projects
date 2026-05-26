"""
utils/logger.py
Logging & Monitoring

Sets up:
  • Structured logging with Rich for console output
  • File-based audit log for all agent traces
  • Simple analytics tracker
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from rich.logging import RichHandler
from rich.console import Console

console = Console()

LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

ANALYTICS_FILE = LOG_DIR / "analytics.jsonl"


def setup_logging(level: str = "INFO") -> None:
    """Configure Rich + file logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True, show_path=False),
            logging.FileHandler(LOG_DIR / "assistant.log", encoding="utf-8"),
        ],
    )


def log_session(state: dict) -> None:
    """
    Append a session record to the analytics JSONL file.
    Each line is one query/response pair with metrics.
    """
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": state.get("user_query", "")[:200],
        "intent": state.get("intent", ""),
        "workflow": state.get("workflow_type", ""),
        "confidence": state.get("confidence_score", 0.0),
        "eval_scores": state.get("eval_scores", {}),
        "review_passed": state.get("review_passed", False),
        "revision_count": state.get("revision_count", 0),
        "sources_count": len(state.get("sources", [])),
        "is_safe": state.get("is_safe", False),
    }

    with open(ANALYTICS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def print_agent_logs(logs: list[str]) -> None:
    """Print the agent audit trail in a readable format."""
    console.print("\n[bold cyan]── Agent Trace ──[/bold cyan]")
    for line in logs:
        console.print(f"  [dim]{line}[/dim]")


def load_analytics() -> list[dict]:
    """Load all session analytics records."""
    if not ANALYTICS_FILE.exists():
        return []
    records = []
    with open(ANALYTICS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records

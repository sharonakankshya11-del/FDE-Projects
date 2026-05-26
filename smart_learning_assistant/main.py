"""
main.py
Smart Learning Assistant — CLI Entry Point

Usage:
    python main.py                      # Interactive chat mode
    python main.py --query "Explain Transformers"
    python main.py --ingest ./data/sample_docs/
    python main.py --analytics          # Show usage stats
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box

load_dotenv()

# Validate API key early
if not os.getenv("OPENAI_API_KEY"):
    print("❌  ERROR: OPENAI_API_KEY not set.")
    print("   Copy .env.example → .env and add your key.")
    sys.exit(1)

from utils.logger import setup_logging, log_session, print_agent_logs, load_analytics
from core.graph import run_query

setup_logging(os.getenv("LOG_LEVEL", "WARNING"))   # suppress verbose LangChain logs

console = Console()

BANNER = """
╔══════════════════════════════════════════════════════════╗
║       🎓  AI Multi-Agent Smart Learning Assistant        ║
║           Powered by LangGraph + GPT-4o-mini             ║
╚══════════════════════════════════════════════════════════╝
"""


def display_result(state: dict, show_trace: bool = False) -> None:
    """Pretty-print the final response."""
    console.print()

    # Main response
    response = state.get("final_response", "No response generated.")
    console.print(
        Panel(
            Markdown(response),
            title="[bold green]🤖 Assistant Response[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # Metadata bar
    confidence = state.get("confidence_score", 0.0)
    intent = state.get("intent", "—")
    workflow = state.get("workflow_type", "—")
    revisions = state.get("revision_count", 0)
    passed = state.get("review_passed", False)

    meta = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    meta.add_column(style="bold cyan")
    meta.add_column(style="white")
    meta.add_row("Intent", intent)
    meta.add_row("Workflow", workflow)
    meta.add_row("Confidence", f"{confidence:.0%}")
    meta.add_row("Review", "✅ Passed" if passed else "⚠️  Flagged")
    meta.add_row("Revisions", str(revisions))

    eval_scores = state.get("eval_scores", {})
    if eval_scores:
        scores_str = " | ".join(f"{k}: {v:.2f}" for k, v in eval_scores.items())
        meta.add_row("Eval Scores", scores_str)

    console.print(Panel(meta, title="[bold blue]📊 Metadata[/bold blue]", border_style="blue"))

    # Agent trace (optional)
    if show_trace:
        print_agent_logs(state.get("logs", []))


def show_analytics() -> None:
    """Display session analytics."""
    records = load_analytics()
    if not records:
        console.print("[yellow]No analytics data yet. Run some queries first![/yellow]")
        return

    table = Table(title="📈 Session Analytics", box=box.ROUNDED)
    table.add_column("Timestamp", style="dim")
    table.add_column("Query (truncated)")
    table.add_column("Intent", style="cyan")
    table.add_column("Confidence", style="green")
    table.add_column("Review", style="yellow")

    for r in records[-20:]:  # show last 20
        table.add_row(
            r["timestamp"][:19],
            r["query"][:40] + "..." if len(r["query"]) > 40 else r["query"],
            r["intent"],
            f"{r['confidence']:.0%}",
            "✅" if r["review_passed"] else "⚠️",
        )

    console.print(table)
    console.print(f"\nTotal sessions logged: [bold]{len(records)}[/bold]")


def interactive_mode() -> None:
    """Run the assistant in interactive chat mode."""
    console.print(BANNER, style="bold blue")
    console.print(
        "[dim]Commands: 'quit' to exit | 'trace' to toggle agent logs | "
        "'clear' to reset history | 'analytics' to view stats[/dim]\n"
    )

    history = []
    show_trace = False

    while True:
        try:
            user_input = console.input("[bold yellow]You:[/bold yellow] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye! 👋[/dim]")
            break

        if not user_input:
            continue

        # CLI commands
        if user_input.lower() == "quit":
            console.print("[dim]Goodbye! 👋[/dim]")
            break
        elif user_input.lower() == "trace":
            show_trace = not show_trace
            console.print(f"[dim]Agent trace: {'ON' if show_trace else 'OFF'}[/dim]")
            continue
        elif user_input.lower() == "clear":
            history = []
            console.print("[dim]Conversation history cleared.[/dim]")
            continue
        elif user_input.lower() == "analytics":
            show_analytics()
            continue

        # Run the multi-agent pipeline
        with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
            state = run_query(user_input, history=history)

        # Display result
        display_result(state, show_trace=show_trace)

        # Update history for next turn (use the full history from state)
        history = state.get("conversation_history", history)

        # Log session
        log_session(state)


def single_query_mode(query: str) -> None:
    """Run a single query and exit."""
    console.print(BANNER, style="bold blue")
    console.print(f"[bold]Query:[/bold] {query}\n")

    with console.status("[bold green]Processing...[/bold green]", spinner="dots"):
        state = run_query(query)

    display_result(state, show_trace=True)
    log_session(state)


def main():
    parser = argparse.ArgumentParser(
        description="AI Multi-Agent Smart Learning Assistant"
    )
    parser.add_argument("--query", "-q", help="Run a single query and exit")
    parser.add_argument(
        "--ingest",
        "-i",
        metavar="PATH",
        help="Ingest documents from a file or directory into the vector store",
    )
    parser.add_argument(
        "--analytics",
        action="store_true",
        help="Show session analytics and exit",
    )
    args = parser.parse_args()

    if args.ingest:
        from utils.ingest import ingest
        ingest(args.ingest)

    elif args.analytics:
        show_analytics()

    elif args.query:
        single_query_mode(args.query)

    else:
        interactive_mode()


if __name__ == "__main__":
    main()

import argparse
import json
from typing import Dict, Any

from app.pipeline import TextToSQLPipeline


def print_output(output: Dict[str, Any]) -> None:
    """Pretty prints the JSON pipeline output to the console."""
    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
    )


def run_single_query(pipeline: TextToSQLPipeline, question: str) -> None:
    """Executes a single query and prints the output."""
    output = pipeline.run(question)
    print_output(output)


def run_interactive(pipeline: TextToSQLPipeline) -> None:
    """Runs a continuous interactive REPL for conversational queries."""
    print("Natural Language Data Query System")
    print("Type 'exit' to quit.")
    print("Type 'clear' to clear conversation memory.")

    while True:
        try:
            question = input("\nquery> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if question.lower() == "clear":
            pipeline.clear_memory()
            print("Conversation memory cleared.")
            continue

        try:
            output = pipeline.run(question)
            print_output(output)
        except Exception as error:
            print(f"An unexpected system error occurred: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert natural-language questions "
            "into validated SQL queries."
        )
    )

    parser.add_argument(
        "question",
        nargs="?",
        help="Natural-language question to query the database.",
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "openai", "local"],
        default="gemini",
        help="LLM provider used for SQL generation.",
    )

    parser.add_argument(
        "--max-rows",
        type=int,
        default=100,
        help="Maximum number of result rows returned.",
    )

    parser.add_argument(
        "--memory-window",
        type=int,
        default=3,
        help="Number of successful conversation turns retained.",
    )

    args = parser.parse_args()

    pipeline = TextToSQLPipeline(
        provider=args.provider,
        max_rows=args.max_rows,
        memory_window=args.memory_window,
    )

    if args.question:
        try:
            run_single_query(pipeline, args.question)
        except Exception as error:
            print(f"An unexpected system error occurred: {error}")
    else:
        run_interactive(pipeline)


if __name__ == "__main__":
    main()
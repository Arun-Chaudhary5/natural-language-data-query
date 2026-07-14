import argparse
import json
import time
from pathlib import Path

from app.executor import SQLExecutionError, SQLExecutor
from app.sql_generator import SQLGenerator, ProviderAPIError
from app.sql_validator import SQLValidationError, SQLValidator
from benchmark.evaluator import exact_match, execution_match
import re


DATASET_PATH = Path(__file__).parent / "dataset.json"
RESULTS_DIR = Path(__file__).parent / "results"

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5.0

MODEL_NAMES = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o",
    "local": "local-model",
}


def load_dataset():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_completed_ids(results_path):
    """
    Read existing JSONL results and return completed case IDs.

    This allows interrupted benchmark runs to resume without
    rerunning completed cases.
    """
    if not results_path.exists():
        return set()

    completed_ids = set()

    with results_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
                completed_ids.add(record["id"])

            except (json.JSONDecodeError, KeyError) as exc:
                raise ValueError(
                    f"Invalid result record at "
                    f"line {line_number}: {exc}"
                ) from exc

    return completed_ids


def append_result(results_path, record):
    """
    Append one completed benchmark record immediately.

    Writing after every case prevents losing completed work
    if the benchmark is interrupted.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with results_path.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )


def generate_with_retry(
    generator,
    question,
    history,
    max_retries,
    retry_delay,
):
    """
    Retry only LLM/API generation failures.

    SQL validation and execution failures are not retried,
    because giving the model multiple attempts for incorrect SQL
    would inflate benchmark accuracy.
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            predicted_sql = generator.generate(
                question=question,
                history=history,
            )

            return predicted_sql, attempt

        except Exception as exc:
            last_error = exc

            if attempt >= max_retries:
                break

            wait_seconds = retry_delay * (2 ** attempt)
            
            # Check for retry hint in error string
            error_str = str(exc)
            match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_str, re.IGNORECASE)
            if match:
                try:
                    hint = float(match.group(1))
                    wait_seconds = hint + 1.0  # add 1s buffer
                except ValueError:
                    pass

            print(f"    Generation failed: {exc}")
            print(
                f"    Retrying in {wait_seconds:.1f}s "
                f"({attempt + 1}/{max_retries})..."
            )

            time.sleep(wait_seconds)

    raise last_error


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Run the text-to-SQL benchmark and store "
            "per-case JSONL results."
        )
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "openai", "local"],
        default="gemini",
        help="LLM provider used for SQL generation.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run only the first N benchmark cases.",
    )

    parser.add_argument(
        "--output",
        default="benchmark_results.jsonl",
        help="JSONL output filename inside benchmark/results.",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help="Maximum retries for LLM/API generation failures.",
    )

    parser.add_argument(
        "--retry-delay",
        type=float,
        default=DEFAULT_RETRY_DELAY,
        help="Initial retry delay in seconds.",
    )

    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be greater than 0.")

    if args.max_retries < 0:
        raise SystemExit("--max-retries cannot be negative.")

    if args.retry_delay < 0:
        raise SystemExit("--retry-delay cannot be negative.")

    cases = load_dataset()

    if args.limit is not None:
        cases = cases[:args.limit]

    results_path = RESULTS_DIR / args.output
    completed_ids = load_completed_ids(results_path)

    generator = SQLGenerator(provider=args.provider)
    validator = SQLValidator()
    executor = SQLExecutor(max_rows=1000)

    model_name = MODEL_NAMES[args.provider]

    print(f"Provider: {args.provider}")
    print(f"Model: {model_name}")
    print(f"Cases selected: {len(cases)}")
    print(f"Already completed: {len(completed_ids)}")
    print()

    for case in cases:
        case_id = case["id"]

        if case_id in completed_ids:
            print(f"[{case_id}] SKIPPED")
            continue

        category = case["category"]
        question = case["question"]
        expected_sql = case["expected_sql"]
        history = case.get("history", [])

        print(f"[{case_id}] {question}")

        started_at = time.perf_counter()

        predicted_sql = None
        validated_sql = None

        success = False
        is_exact_match = False
        is_execution_match = False

        error = None
        retry_count = 0

        try:
            predicted_sql, retry_count = generate_with_retry(
                generator=generator,
                question=question,
                history=history,
                max_retries=args.max_retries,
                retry_delay=args.retry_delay,
            )

            # Validate predicted SQL.
            validated_sql = validator.validate(
                predicted_sql
            )

            # Execute predicted SQL.
            predicted_result = executor.execute(
                validated_sql
            )

            # Validate gold SQL.
            expected_validated_sql = validator.validate(
                expected_sql
            )

            # Execute gold SQL.
            expected_result = executor.execute(
                expected_validated_sql
            )

            success = True

            # Normalized structural SQL comparison.
            is_exact_match = exact_match(
                validated_sql,
                expected_sql,
            )

            # Database-result comparison.
            is_execution_match = execution_match(
                predicted_result,
                expected_result,
                expected_sql=expected_sql,
            )

        except (
            SQLValidationError,
            SQLExecutionError,
        ) as exc:
            error = str(exc)

        except ProviderAPIError as exc:
            error = str(exc)
            print(f"    Provider API failure: {error}")
            print("    Case not saved. Stopping benchmark so it can resume later.")
            break
            
        except Exception as exc:
            error = str(exc)


        latency_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        record = {
            "id": case_id,
            "provider": args.provider,
            "model": model_name,
            "category": category,
            "question": question,
            "expected_sql": expected_sql,
            "predicted_sql": predicted_sql,
            "validated_sql": validated_sql,
            "success": success,
            "exact_match": is_exact_match,
            "execution_match": is_execution_match,
            "latency_ms": latency_ms,
            "retry_count": retry_count,
            "error": error,
        }

        append_result(
            results_path,
            record,
        )

        # Add ID immediately so the current process state
        # remains consistent with the JSONL file.
        completed_ids.add(case_id)

        if is_exact_match:
            status = "EXACT"

        elif is_execution_match:
            status = "EXEC"

        else:
            status = "FAIL"

        print(
            f"    {status} | "
            f"{latency_ms} ms | "
            f"retries={retry_count}"
        )

        if error:
            print(f"    Error: {error}")

    print()
    print(f"Results saved to: {results_path}")


if __name__ == "__main__":
    main()
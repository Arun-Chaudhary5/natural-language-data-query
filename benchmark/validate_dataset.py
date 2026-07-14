import json
from collections import Counter
from pathlib import Path

from app.executor import SQLExecutionError, SQLExecutor
from app.sql_validator import SQLValidationError, SQLValidator


DATASET_PATH = Path(__file__).parent / "dataset.json"

EXPECTED_CATEGORY_COUNTS = {
    "basic": 30,
    "sorting_limit_distinct": 20,
    "aggregation_grouping": 30,
    "joins": 35,
    "multi_table_aggregation": 35,
    "date_time": 20,
    "subquery_cte": 15,
    "conversation": 15,
}


def load_dataset():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_dataset(cases):
    validator = SQLValidator()
    executor = SQLExecutor(max_rows=1000)

    seen_ids = set()
    errors = []

    for index, case in enumerate(cases, start=1):
        case_id = case.get("id")

        required_fields = {
            "id",
            "category",
            "question",
            "expected_sql",
        }

        missing_fields = required_fields - set(case)

        if missing_fields:
            errors.append(
                f"Case {case_id}: missing fields "
                f"{sorted(missing_fields)}"
            )
            continue

        history = case.get("history", [])

        if case_id in seen_ids:
            errors.append(f"Duplicate ID: {case_id}")

        seen_ids.add(case_id)

        if case_id != index:
            errors.append(
                f"Expected ID {index}, found {case_id}"
            )

        if not isinstance(case["question"], str):
            errors.append(
                f"Case {case_id}: question must be a string"
            )
        elif not case["question"].strip():
            errors.append(
                f"Case {case_id}: empty question"
            )

        if case["category"] not in EXPECTED_CATEGORY_COUNTS:
            errors.append(
                f"Case {case_id}: unknown category "
                f"{case['category']}"
            )

        # Conversation cases must contain history.
        if case["category"] == "conversation" and not history:
            errors.append(
                f"Case {case_id}: "
                "conversation case requires history"
            )

        # Non-conversation cases should not contain history.
        if case["category"] != "conversation" and history:
            errors.append(
                f"Case {case_id}: "
                "non-conversation case should not have history"
            )

        # Validate and execute every history turn.
        for turn_index, turn in enumerate(history, start=1):
            if not isinstance(turn, dict):
                errors.append(
                    f"Case {case_id}: history turn "
                    f"{turn_index} must be an object"
                )
                continue

            if "question" not in turn or "sql" not in turn:
                errors.append(
                    f"Case {case_id}: history turn "
                    f"{turn_index} requires question and sql"
                )
                continue

            if (
                not isinstance(turn["question"], str)
                or not turn["question"].strip()
            ):
                errors.append(
                    f"Case {case_id}: history turn "
                    f"{turn_index} has invalid question"
                )

            if (
                not isinstance(turn["sql"], str)
                or not turn["sql"].strip()
            ):
                errors.append(
                    f"Case {case_id}: history turn "
                    f"{turn_index} has invalid sql"
                )
                continue

            try:
                history_sql = validator.validate(turn["sql"])
                executor.execute(history_sql)

            except (
                SQLValidationError,
                SQLExecutionError,
            ) as error:
                errors.append(
                    f"Case {case_id}: invalid history turn "
                    f"{turn_index}: {error}"
                )

        # Validate gold SQL.
        try:
            validated_sql = validator.validate(
                case["expected_sql"]
            )

        except SQLValidationError as error:
            errors.append(
                f"Case {case_id}: invalid expected SQL: {error}"
            )
            continue

        # Execute gold SQL.
        try:
            executor.execute(validated_sql)

        except SQLExecutionError as error:
            errors.append(
                f"Case {case_id}: expected SQL "
                f"failed execution: {error}"
            )

    return errors


def print_category_counts(cases):
    counts = Counter(
        case["category"]
        for case in cases
        if "category" in case
    )

    print("\nCATEGORY COUNTS:")

    for category, expected_count in EXPECTED_CATEGORY_COUNTS.items():
        actual_count = counts.get(category, 0)

        print(
            f"- {category}: "
            f"{actual_count}/{expected_count}"
        )


def main():
    cases = load_dataset()
    errors = validate_dataset(cases)

    print(f"Cases: {len(cases)}")
    print_category_counts(cases)

    if errors:
        print("\nDATASET ERRORS:")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("\nDataset validation passed.")


if __name__ == "__main__":
    main()
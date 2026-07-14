import re

import sqlglot
from sqlglot import exp


def normalize_sql(sql):
    expression = sqlglot.parse_one(sql, read="sqlite")

    # SQL result ordering is ascending by default.
    # Canonicalize implicit ASC so:
    #
    # ORDER BY customer_name
    #
    # and
    #
    # ORDER BY customer_name ASC
    #
    # normalize to the same representation.
    for ordered in expression.find_all(exp.Ordered):
        if ordered.args.get("desc") is None:
            ordered.set("desc", False)

    normalized = expression.sql(
        dialect="sqlite",
        pretty=False,
        normalize=True,
    )

    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized


def exact_match(predicted_sql, expected_sql):
    try:
        return normalize_sql(predicted_sql) == normalize_sql(expected_sql)

    except Exception:
        return False


def normalize_value(value):
    if isinstance(value, float):
        return round(value, 6)

    return value


def normalize_row(row, columns):
    return tuple(
        normalize_value(row[column])
        for column in columns
    )


def has_order_by(sql):
    try:
        expression = sqlglot.parse_one(
            sql,
            read="sqlite",
        )

        return expression.args.get("order") is not None

    except Exception:
        return False


def execution_match(
    predicted_result,
    expected_result,
    expected_sql=None,
):
    """
    Compare two structured SQL execution results.

    Rules:
    - Column names and column order must match.
    - Number of rows must match.
    - Values must match.
    - If expected SQL contains ORDER BY, row order must match.
    - Otherwise, row order is ignored.
    """

    predicted_columns = predicted_result["columns"]
    expected_columns = expected_result["columns"]

    if predicted_columns != expected_columns:
        return False

    predicted_rows = predicted_result["rows"]
    expected_rows = expected_result["rows"]

    if len(predicted_rows) != len(expected_rows):
        return False

    predicted_normalized = [
        normalize_row(row, predicted_columns)
        for row in predicted_rows
    ]

    expected_normalized = [
        normalize_row(row, expected_columns)
        for row in expected_rows
    ]

    if expected_sql and has_order_by(expected_sql):
        return predicted_normalized == expected_normalized

    return sorted(predicted_normalized) == sorted(expected_normalized)
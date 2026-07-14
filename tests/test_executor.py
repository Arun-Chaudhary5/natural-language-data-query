import pytest

from app.executor import SQLExecutionError, SQLExecutor


def test_executor_returns_structured_result():
    executor = SQLExecutor(max_rows=10)

    result = executor.execute(
        """
        SELECT customer_name
        FROM customers
        ORDER BY customer_id;
        """
    )

    assert "columns" in result
    assert "rows" in result
    assert "row_count" in result
    assert "truncated" in result

    assert result["columns"] == ["customer_name"]
    assert result["row_count"] == 5
    assert result["truncated"] is False


def test_executor_truncates_results():
    executor = SQLExecutor(max_rows=2)

    result = executor.execute(
        "SELECT * FROM customers ORDER BY customer_id;"
    )

    assert result["row_count"] == 2
    assert result["truncated"] is True


def test_executor_rejects_unknown_table():
    executor = SQLExecutor()

    with pytest.raises(SQLExecutionError):
        executor.execute(
            "SELECT * FROM nonexistent_table;"
        )
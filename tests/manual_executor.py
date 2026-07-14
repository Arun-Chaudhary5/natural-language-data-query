from app.executor import SQLExecutionError, SQLExecutor
from app.sql_validator import SQLValidationError, SQLValidator


def test_query(validator, executor, sql):
    print("\nSQL:")
    print(sql)

    try:
        validated_sql = validator.validate(sql)

        result = executor.execute(validated_sql)

        print("\nRESULT:")
        print(result)

    except (SQLValidationError, SQLExecutionError) as error:
        print("\nERROR:")
        print(error)


def main():
    validator = SQLValidator()
    executor = SQLExecutor(max_rows=5)

    queries = [
        """
        SELECT customer_name, city
        FROM customers
        ORDER BY customer_id;
        """,

        """
        SELECT
            c.customer_name,
            SUM(oi.quantity * oi.unit_price) AS total_spent
        FROM customers AS c
        JOIN orders AS o
            ON c.customer_id = o.customer_id
        JOIN order_items AS oi
            ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        GROUP BY c.customer_id, c.customer_name
        ORDER BY total_spent DESC;
        """,

        "SELECT * FROM nonexistent_table;",

        "DELETE FROM customers;",
    ]

    for sql in queries:
        test_query(validator, executor, sql)


if __name__ == "__main__":
    main()
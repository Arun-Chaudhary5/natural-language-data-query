from app.sql_validator import SQLValidationError, SQLValidator


def main():
    validator = SQLValidator()

    queries = [
        "SELECT * FROM customers;",

        "DELETE FROM customers;",

        """
        SELECT * FROM customers;
        DROP TABLE customers;
        """,

        """
        SELECT *
        FROM products
        WHERE product_name = 'DROP TABLE customers';
        """,

        """
        WITH expensive_products AS (
            SELECT *
            FROM products
            WHERE price > 10000
        )
        SELECT *
        FROM expensive_products;
        """,

        """
        SELECT *
        FROM nonexistent_table;
        """,

        """
        SELECT *
        FROM customers AS c
        JOIN fake_orders AS f
        ON c.customer_id = f.customer_id;
        """,
    ]

    for sql in queries:
        print("\nQUERY:")
        print(sql)

        try:
            validated_sql = validator.validate(sql)
            print("RESULT: VALID")
            print(validated_sql)

        except SQLValidationError as error:
            print("RESULT: REJECTED")
            print(error)


if __name__ == "__main__":
    main()
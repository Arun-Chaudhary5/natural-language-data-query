from benchmark.evaluator import exact_match, normalize_sql


def test_normalization_ignores_formatting():
    sql_1 = """
    SELECT *
    FROM customers
    WHERE city = 'Delhi';
    """

    sql_2 = "select * from customers where city = 'Delhi'"

    assert normalize_sql(sql_1) == normalize_sql(sql_2)


def test_exact_match_accepts_same_query():
    predicted = """
    SELECT customer_name
    FROM customers
    ORDER BY customer_name;
    """

    expected = (
        "SELECT customer_name "
        "FROM customers "
        "ORDER BY customer_name;"
    )

    assert exact_match(predicted, expected) is True


def test_exact_match_rejects_different_query():
    predicted = "SELECT customer_name FROM customers;"

    expected = "SELECT * FROM customers;"

    assert exact_match(predicted, expected) is False
def test_exact_match_treats_implicit_and_explicit_ascending_order_as_equal():
    predicted = """
    SELECT *
    FROM customers
    ORDER BY customer_name;
    """

    expected = """
    SELECT *
    FROM customers
    ORDER BY customer_name ASC;
    """

    assert exact_match(predicted, expected) is True


def test_alias_differences():
    predicted = """
    SELECT c.customer_name
    FROM customers AS c;
    """

    expected = """
    SELECT customers.customer_name
    FROM customers;
    """

    assert exact_match(predicted, expected) is False


def test_different_valid_aggregation_formulations():
    predicted = """
    SELECT c.customer_name,
           SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM customers AS c
    JOIN orders AS o
        ON c.customer_id = o.customer_id
    JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY c.customer_id, c.customer_name;
    """

    expected = """
    SELECT c.customer_name,
           SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM customers AS c
    JOIN orders AS o
        ON c.customer_id = o.customer_id
    JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.status = 'completed'
    GROUP BY c.customer_name;
    """

    assert exact_match(predicted, expected) is False

from benchmark.evaluator import execution_match


def test_execution_match_accepts_same_unordered_rows():
    predicted_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Riya Mehta"},
            {"customer_name": "Aarav Sharma"},
        ],
    }

    expected_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Aarav Sharma"},
            {"customer_name": "Riya Mehta"},
        ],
    }

    expected_sql = """
    SELECT customer_name
    FROM customers;
    """

    assert execution_match(
        predicted_result,
        expected_result,
        expected_sql,
    ) is True


def test_execution_match_rejects_wrong_order_when_order_by_expected():
    predicted_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Riya Mehta"},
            {"customer_name": "Aarav Sharma"},
        ],
    }

    expected_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Aarav Sharma"},
            {"customer_name": "Riya Mehta"},
        ],
    }

    expected_sql = """
    SELECT customer_name
    FROM customers
    ORDER BY customer_name ASC;
    """

    assert execution_match(
        predicted_result,
        expected_result,
        expected_sql,
    ) is False


def test_execution_match_accepts_correct_order_when_order_by_expected():
    predicted_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Aarav Sharma"},
            {"customer_name": "Riya Mehta"},
        ],
    }

    expected_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Aarav Sharma"},
            {"customer_name": "Riya Mehta"},
        ],
    }

    expected_sql = """
    SELECT customer_name
    FROM customers
    ORDER BY customer_name ASC;
    """

    assert execution_match(
        predicted_result,
        expected_result,
        expected_sql,
    ) is True


def test_execution_match_rejects_different_columns():
    predicted_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Aarav Sharma"},
        ],
    }

    expected_result = {
        "columns": ["customer_id", "customer_name"],
        "rows": [
            {
                "customer_id": 1,
                "customer_name": "Aarav Sharma",
            },
        ],
    }

    expected_sql = """
    SELECT customer_id, customer_name
    FROM customers;
    """

    assert execution_match(
        predicted_result,
        expected_result,
        expected_sql,
    ) is False


def test_execution_match_rejects_different_values():
    predicted_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Kabir Singh"},
        ],
    }

    expected_result = {
        "columns": ["customer_name"],
        "rows": [
            {"customer_name": "Aarav Sharma"},
        ],
    }

    expected_sql = """
    SELECT customer_name
    FROM customers;
    """

    assert execution_match(
        predicted_result,
        expected_result,
        expected_sql,
    ) is False
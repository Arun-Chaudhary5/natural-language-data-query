import pytest

from app.sql_validator import SQLValidationError, SQLValidator


@pytest.fixture
def validator():
    return SQLValidator()


def test_valid_select(validator):
    sql = "SELECT * FROM customers;"

    assert validator.validate(sql) == sql


def test_rejects_delete(validator):
    with pytest.raises(SQLValidationError):
        validator.validate("DELETE FROM customers;")


def test_rejects_multiple_statements(validator):
    with pytest.raises(SQLValidationError):
        validator.validate(
            "SELECT * FROM customers; DROP TABLE customers;"
        )


def test_accepts_valid_cte(validator):
    sql = """
    WITH delhi_customers AS (
        SELECT *
        FROM customers
        WHERE city = 'Delhi'
    )
    SELECT *
    FROM delhi_customers;
    """

    assert validator.validate(sql) == sql.strip()


def test_rejects_unknown_table(validator):
    with pytest.raises(
        SQLValidationError,
        match="Unknown table",
    ):
        validator.validate(
            "SELECT * FROM nonexistent_table;"
        )
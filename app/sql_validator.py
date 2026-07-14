from typing import List, Set, Any
from sqlglot import exp, parse
from sqlglot.errors import ParseError

from app.schema import SchemaInspector
from app.errors import QuerySystemError


class SQLValidationError(QuerySystemError):
    """Raised when a SQL query fails validation."""
    pass


class SQLValidator:
    """Validates SQL queries against a safe schema-based policy."""
    
    FORBIDDEN_EXPRESSIONS = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.Command,
    )

    def __init__(self) -> None:
        with SchemaInspector() as inspector:
            self.allowed_tables: Set[str] = set(inspector.get_table_names())

    def validate(self, sql: str) -> str:
        """Validates a SQL query, ensuring it is read-only and uses allowed tables."""
        if not sql or not sql.strip():
            raise SQLValidationError("SQL query is empty.")

        cleaned_sql = sql.strip()
        expressions = self._parse_sql(cleaned_sql)

        self._validate_single_statement(expressions)
        expression = expressions[0]

        self._validate_read_only(expression)
        self._validate_tables(expression)

        return cleaned_sql

    def _parse_sql(self, sql: str) -> List[Any]:
        """Parses SQL using the SQLite dialect."""
        try:
            return parse(sql, dialect="sqlite")
        except ParseError as error:
            raise SQLValidationError(
                f"Invalid SQL syntax: {error}"
            ) from error

    def _validate_single_statement(self, expressions: List[Any]) -> None:
        """Ensures the query contains only a single statement."""
        if len(expressions) != 1:
            raise SQLValidationError(
                "Only one SQL statement is allowed."
            )

    def _validate_read_only(self, expression: Any) -> None:
        """Ensures the query does not contain destructive operations."""
        if not isinstance(expression, exp.Query):
            raise SQLValidationError(
                "Only read-only queries are allowed."
            )

        for forbidden_type in self.FORBIDDEN_EXPRESSIONS:
            if expression.find(forbidden_type):
                raise SQLValidationError(
                    "Query contains a forbidden SQL operation."
                )

    def _validate_tables(self, expression: Any) -> None:
        """Ensures physical tables referenced in the query exist in the database."""
        cte_names = {
            cte.alias_or_name
            for cte in expression.find_all(exp.CTE)
        }

        referenced_tables = {
            table.name
            for table in expression.find_all(exp.Table)
        }

        physical_tables = referenced_tables - cte_names
        unknown_tables = physical_tables - self.allowed_tables

        if unknown_tables:
            raise SQLValidationError(
                "Unknown table(s): "
                + ", ".join(sorted(unknown_tables))
            )
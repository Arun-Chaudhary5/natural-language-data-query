import sqlite3
from typing import Dict, List, Any

from app.database import DATABASE_PATH
from app.errors import QuerySystemError


class SQLExecutionError(QuerySystemError):
    """Raised when an executed SQL query fails (e.g. SQLite error)."""
    pass


class SQLExecutor:
    """Safely executes SQL queries in read-only mode and returns structured results."""
    
    def __init__(self, max_rows: int = 100) -> None:
        self.max_rows = max_rows

    def execute(self, sql: str) -> Dict[str, Any]:
        """
        Executes a SQL query in read-only mode against the SQLite database.
        Returns a dictionary containing columns, rows, row count, and a truncation flag.
        """
        connection = None
        try:
            database_uri = f"{DATABASE_PATH.as_uri()}?mode=ro"

            connection = sqlite3.connect(
                database_uri,
                uri=True,
            )
            connection.row_factory = sqlite3.Row

            cursor = connection.execute(sql)
            rows = cursor.fetchmany(self.max_rows + 1)
            truncated = len(rows) > self.max_rows
            rows = rows[:self.max_rows]

            return {
                "columns": (
                    [description[0] for description in cursor.description]
                    if cursor.description
                    else []
                ),
                "rows": [dict(row) for row in rows],
                "row_count": len(rows),
                "truncated": truncated,
            }

        except sqlite3.Error as error:
            raise SQLExecutionError(
                f"Database execution failed: {error}"
            ) from error
        finally:
            if connection is not None:
                connection.close()
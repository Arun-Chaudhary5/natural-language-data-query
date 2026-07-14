import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple


DATABASE_PATH = Path(__file__).parent.parent / "data" / "ecommerce.db"


def get_connection() -> sqlite3.Connection:
    """Creates and returns a new SQLite database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def execute_query(query: str, parameters: Tuple = ()) -> List[Dict[str, Any]]:
    """Executes a parameterized SQL query and returns the rows as a list of dictionaries."""
    connection = get_connection()
    try:
        cursor = connection.execute(query, parameters)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()
from typing import List, Dict, Any, Optional
from app.database import get_connection


class SchemaInspector:
    """
    Introspects the SQLite database to extract schema information.
    
    Can be used as a context manager to ensure safe resource handling.
    """
    def __init__(self) -> None:
        self.connection = get_connection()

    def __enter__(self) -> "SchemaInspector":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def get_table_names(self) -> List[str]:
        """Returns a list of all physical table names in the database."""
        cursor = self.connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        )
        return [row["name"] for row in cursor.fetchall()]

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Extracts column metadata for a given table."""
        cursor = self.connection.execute(
            f"PRAGMA table_info({table_name});"
        )
        columns: List[Dict[str, Any]] = []
        for row in cursor.fetchall():
            columns.append(
                {
                    "name": row["name"],
                    "type": row["type"],
                    "not_null": bool(row["notnull"]),
                    "primary_key": bool(row["pk"]),
                }
            )
        return columns

    def get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """Extracts foreign key metadata for a given table."""
        cursor = self.connection.execute(
            f"PRAGMA foreign_key_list({table_name});"
        )
        foreign_keys: List[Dict[str, str]] = []
        for row in cursor.fetchall():
            foreign_keys.append(
                {
                    "from_column": row["from"],
                    "to_table": row["table"],
                    "to_column": row["to"],
                }
            )
        return foreign_keys

    def inspect(self) -> Dict[str, Dict[str, Any]]:
        """Inspects the entire database and returns schema mapping."""
        schema: Dict[str, Dict[str, Any]] = {}
        for table_name in self.get_table_names():
            schema[table_name] = {
                "columns": self.get_columns(table_name),
                "foreign_keys": self.get_foreign_keys(table_name),
            }
        return schema

    def format_for_prompt(self) -> str:
        """Formats the database schema into a readable string for LLM context."""
        schema = self.inspect()
        lines: List[str] = []

        for table_name, table_info in schema.items():
            lines.append(f"TABLE {table_name}")
            lines.append("COLUMNS:")
            for column in table_info["columns"]:
                constraints: List[str] = []
                if column["primary_key"]:
                    constraints.append("PRIMARY KEY")
                if column["not_null"]:
                    constraints.append("NOT NULL")

                constraint_text = " ".join(constraints)
                column_line = f"- {column['name']} {column['type']}"
                if constraint_text:
                    column_line += f" {constraint_text}"
                lines.append(column_line)

            if table_info["foreign_keys"]:
                lines.append("FOREIGN KEYS:")
                for foreign_key in table_info["foreign_keys"]:
                    lines.append(
                        f"- {table_name}.{foreign_key['from_column']} "
                        f"-> {foreign_key['to_table']}.{foreign_key['to_column']}"
                    )
            lines.append("")

        return "\n".join(lines)

    def close(self) -> None:
        """Closes the underlying database connection."""
        self.connection.close()
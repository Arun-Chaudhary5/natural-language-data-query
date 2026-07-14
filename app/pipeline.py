from typing import Dict, Any

from app.executor import SQLExecutionError, SQLExecutor
from app.logger import QueryLogger
from app.memory import ConversationMemory
from app.sql_generator import SQLGenerationError, SQLGenerator
from app.sql_validator import SQLValidationError, SQLValidator
from app.errors import QuerySystemError


class TextToSQLPipeline:
    """Orchestrates the Text-to-SQL generation, validation, and execution workflow."""
    
    def __init__(
        self,
        provider: str = "gemini",
        max_rows: int = 100,
        memory_window: int = 3,
        max_retries: int = 1,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        self.generator = SQLGenerator(provider=provider)
        self.validator = SQLValidator()
        self.executor = SQLExecutor(max_rows=max_rows)
        self.memory = ConversationMemory(window_size=memory_window)
        self.logger = QueryLogger()
        self.max_retries = max_retries

    def _finalize(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Logs the final pipeline output and returns it."""
        self.logger.log(output)
        return output

    def run(self, question: str) -> Dict[str, Any]:
        """
        Runs the full text-to-SQL pipeline for a user question.
        Handles query generation, schema validation, safe execution, and error self-correction.
        """
        sql: str | None = None
        history = self.memory.format_for_prompt()
        attempts = 0

        try:
            sql = self.generator.generate(
                question=question,
                history=history,
            )

            while True:
                try:
                    validated_sql = self.validator.validate(sql)
                    result = self.executor.execute(validated_sql)
                    break
                except (
                    SQLValidationError,
                    SQLExecutionError,
                ) as error:
                    if attempts >= self.max_retries:
                        raise

                    attempts += 1
                    sql = self.generator.correct(
                        question=question,
                        previous_sql=sql,
                        error=error,
                        history=history,
                    )

            self.memory.add_turn(
                question=question,
                sql=validated_sql,
            )

            return self._finalize(
                {
                    "success": True,
                    "question": question,
                    "sql": validated_sql,
                    "result": result,
                    "error": None,
                    "retries": attempts,
                }
            )

        except QuerySystemError as error:
            return self._finalize(
                {
                    "success": False,
                    "question": question,
                    "sql": sql,
                    "result": None,
                    "error": str(error),
                    "retries": attempts,
                }
            )

    def clear_memory(self) -> None:
        """Clears the underlying conversation memory for a fresh context."""
        self.memory.clear()
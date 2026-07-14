from typing import Optional
from app.chains import (
    create_sql_correction_chain,
    create_sql_generation_chain,
)
from app.schema import SchemaInspector
from app.errors import QuerySystemError


class SQLGenerationError(QuerySystemError):
    """Raised when the LLM fails to generate a valid SQL query."""
    pass


class ProviderAPIError(QuerySystemError):
    """Raised when the underlying LLM API provider fails (e.g., quotas, network)."""
    pass


class SQLGenerator:
    """Handles prompt generation and interactions with the LLM provider."""
    
    def __init__(self, provider: str = "gemini") -> None:
        self.generation_chain = create_sql_generation_chain(provider)
        self.correction_chain = create_sql_correction_chain(provider)

    def _get_schema(self) -> str:
        """Extracts and formats the database schema for the prompt."""
        with SchemaInspector() as inspector:
            return inspector.format_for_prompt()

    def generate(
        self,
        question: str,
        history: str = "No previous conversation.",
    ) -> str:
        """Generates a SQL query based on a natural language question."""
        schema = self._get_schema()

        try:
            sql = self.generation_chain.invoke(
                {
                    "schema": schema,
                    "history": history,
                    "question": question,
                }
            )
        except Exception as error:
            error_str = str(error)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str or "Connection" in error_str or "timeout" in error_str.lower():
                raise ProviderAPIError(
                    f"Provider API failure: {error}"
                ) from error
            raise SQLGenerationError(
                f"SQL generation failed: {error}"
            ) from error

        return sql.strip()

    def correct(
        self,
        question: str,
        previous_sql: str,
        error: BaseException,
        history: str = "No previous conversation.",
    ) -> str:
        """Corrects a failed SQL query based on the error message."""
        schema = self._get_schema()

        try:
            sql = self.correction_chain.invoke(
                {
                    "schema": schema,
                    "history": history,
                    "question": question,
                    "previous_sql": previous_sql,
                    "error": str(error),
                }
            )
        except Exception as provider_error:
            error_str = str(provider_error)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str or "Connection" in error_str or "timeout" in error_str.lower():
                raise ProviderAPIError(
                    f"Provider API failure: {provider_error}"
                ) from provider_error
            raise SQLGenerationError(
                f"SQL correction failed: {provider_error}"
            ) from provider_error

        return sql.strip()
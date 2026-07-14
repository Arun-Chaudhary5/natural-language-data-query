from collections import deque
from typing import List, Dict


class ConversationMemory:
    """Manages bounded conversation history for follow-up queries."""
    
    def __init__(self, window_size: int = 3) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be greater than 0.")
        self.window_size = window_size
        self.turns: deque = deque(maxlen=window_size)

    def add_turn(self, question: str, sql: str) -> None:
        """Stores a successful question-SQL pair in memory."""
        self.turns.append(
            {
                "question": question,
                "sql": sql,
            }
        )

    def get_history(self) -> List[Dict[str, str]]:
        """Returns the raw retained conversation history."""
        return list(self.turns)

    def format_for_prompt(self) -> str:
        """Formats the retained conversation history as a string for the LLM prompt."""
        if not self.turns:
            return "No previous conversation."

        lines: List[str] = []
        for index, turn in enumerate(self.turns, start=1):
            lines.append(f"Turn {index}")
            lines.append(f"User question: {turn['question']}")
            lines.append(f"Generated SQL: {turn['sql']}")
            lines.append("")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clears the conversation memory entirely."""
        self.turns.clear()
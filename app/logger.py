import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Union


LOG_PATH = Path(__file__).parent.parent / "logs" / "queries.jsonl"


class QueryLogger:
    """Logs pipeline execution results into a JSON Lines file."""
    
    def __init__(self, log_path: Union[str, Path] = LOG_PATH) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, pipeline_output: Dict[str, Any]) -> None:
        """Appends a single structured JSON record to the log file."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": pipeline_output.get("success", False),
            "question": pipeline_output.get("question", ""),
            "sql": pipeline_output.get("sql", None),
            "result": pipeline_output.get("result", None),
            "error": pipeline_output.get("error", None),
        }

        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )
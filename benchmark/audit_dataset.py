import json
from pathlib import Path
from app.executor import SQLExecutor, SQLExecutionError
from app.sql_validator import SQLValidator, SQLValidationError
from app.errors import QuerySystemError

DATASET_PATH = Path(__file__).parent / "dataset.json"

def main():
    try:
        with DATASET_PATH.open("r", encoding="utf-8") as file:
            dataset = json.load(file)
    except FileNotFoundError:
        print(f"Error: Could not find {DATASET_PATH}")
        return

    executor = SQLExecutor(max_rows=10)
    validator = SQLValidator()
    
    failures = []
    
    for case in dataset:
        case_id = case.get("id")
        sql = case.get("expected_sql", "")
        
        try:
            # We also validate it to make sure the tables exist and it's a safe query
            validated_sql = validator.validate(sql)
            executor.execute(validated_sql)
        except QuerySystemError as error:
            failures.append({
                "id": case_id,
                "question": case.get("question"),
                "sql": sql,
                "error": str(error)
            })

    if not failures:
        print(f"All {len(dataset)} queries executed successfully!")
    else:
        print(f"Found {len(failures)} failing queries out of {len(dataset)}:\n")
        for f in failures:
            print(f"ID {f['id']}: {f['question']}")
            print(f"SQL: {f['sql']}")
            print(f"ERROR: {f['error']}\n")
            print("-" * 40)

if __name__ == "__main__":
    main()

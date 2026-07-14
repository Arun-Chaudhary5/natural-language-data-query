import json

from app.logger import QueryLogger


def main():
    logger = QueryLogger()

    successful_output = {
        "success": True,
        "question": "Show customers from Delhi.",
        "sql": "SELECT * FROM customers WHERE city = 'Delhi';",
        "result": {
            "columns": ["customer_id", "customer_name"],
            "rows": [],
            "row_count": 0,
            "truncated": False,
        },
        "error": None,
    }

    failed_output = {
        "success": False,
        "question": "Run an invalid query.",
        "sql": "SELECT * FROM nonexistent_table;",
        "result": None,
        "error": "Unknown table(s): nonexistent_table",
    }

    logger.log(successful_output)
    logger.log(failed_output)

    with logger.log_path.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            print(record)


if __name__ == "__main__":
    main()
from app.schema import SchemaInspector


def main():
    inspector = SchemaInspector()

    try:
        prompt_schema = inspector.format_for_prompt()
        print(prompt_schema)

    finally:
        inspector.close()


if __name__ == "__main__":
    main()
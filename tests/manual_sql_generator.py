from app.sql_generator import SQLGenerator


def main():
    generator = SQLGenerator(provider="gemini")

    questions = [
        "Show me all customers from Delhi.",

        "Which customer spent the most money?",

        "Which category generated the highest revenue?",
    ]

    for question in questions:
        print("\nQUESTION:")
        print(question)

        sql = generator.generate(question)

        print("\nGENERATED SQL:")
        print(sql)

        print("-" * 60)


if __name__ == "__main__":
    main()
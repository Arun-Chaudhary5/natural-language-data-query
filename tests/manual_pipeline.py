from pprint import pprint

from app.pipeline import TextToSQLPipeline


def main():
    pipeline = TextToSQLPipeline(
        provider="gemini",
        max_rows=10,
    )

    questions = [
        "Show me all customers from Delhi.",

        "Which customer spent the most money?",

        "Which category generated the highest revenue?",

        "Show the total revenue generated in each month.",
    ]

    for question in questions:
        print("\n" + "=" * 70)
        print("QUESTION:")
        print(question)

        output = pipeline.run(question)

        print("\nPIPELINE OUTPUT:")
        pprint(output)


if __name__ == "__main__":
    main()
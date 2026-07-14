from pprint import pprint

from app.pipeline import TextToSQLPipeline


def main():
    pipeline = TextToSQLPipeline(
        provider="gemini",
        max_rows=10,
        memory_window=3,
    )

    questions = [
        "Which customer spent the most money?",
        "Show me the top 3 instead.",
        "Only show their names.",
        "Now sort those names alphabetically.",
    ]

    for question in questions:
        print("\n" + "=" * 70)
        print("QUESTION:")
        print(question)

        output = pipeline.run(question)

        print("\nSQL:")
        print(output["sql"])

        print("\nRESULT:")
        pprint(output["result"])

        print("\nCURRENT MEMORY:")
        print(pipeline.memory.format_for_prompt())


if __name__ == "__main__":
    main()
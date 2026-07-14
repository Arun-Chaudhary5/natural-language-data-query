from app.llm import ask_model


def main():
    system_prompt = """
    You are a helpful assistant.
    Answer concisely.
    """

    user_prompt = """
    Explain what SQL is in one sentence.
    """

    response = ask_model(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        provider="gemini",
    )

    print(response)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
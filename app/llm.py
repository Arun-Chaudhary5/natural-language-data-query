from openai import OpenAI
from google import genai

from app.config import OPENAI_API_KEY, GEMINI_API_KEY


def ask_openai(system_prompt, user_prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        model="gpt-4o",
        instructions=system_prompt,
        input=user_prompt,
        temperature=0,
    )

    return response.output_text


def ask_gemini(system_prompt, user_prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config={
            "system_instruction": system_prompt,
            "temperature": 0,
        },
    )

    return response.text


def ask_model(system_prompt, user_prompt, provider="gemini"):
    if provider == "openai":
        return ask_openai(system_prompt, user_prompt)

    if provider == "gemini":
        return ask_gemini(system_prompt, user_prompt)

    raise ValueError(f"Unsupported LLM provider: {provider}")
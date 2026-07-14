from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import GEMINI_API_KEY, OPENAI_API_KEY, LOCAL_API_BASE, LOCAL_MODEL_NAME
from app.prompts import SQL_SYSTEM_PROMPT


def create_model(provider):
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0,
        )

    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4o",
            api_key=OPENAI_API_KEY,
            temperature=0,
        )

    if provider == "local":
        return ChatOpenAI(
            model=LOCAL_MODEL_NAME,
            api_key="not-needed",
            base_url=LOCAL_API_BASE,
            temperature=0,
        )

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )


def create_sql_generation_chain(provider="gemini"):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SQL_SYSTEM_PROMPT,
            ),
            (
                "human",
                """
DATABASE SCHEMA:

{schema}

RECENT CONVERSATION HISTORY:

{history}

CURRENT USER QUESTION:

{question}

Use the conversation history only when the current question depends on previous turns.

Generate the SQLite query.
""",
            ),
        ]
    )

    model = create_model(provider)
    parser = StrOutputParser()

    return prompt | model | parser
    

def create_sql_correction_chain(provider="gemini"):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SQL_SYSTEM_PROMPT,
            ),
            (
                "human",
                """
DATABASE SCHEMA:

{schema}

RECENT CONVERSATION HISTORY:

{history}

USER QUESTION:

{question}

PREVIOUS GENERATED SQL:

{previous_sql}

ERROR:

{error}

The previous SQL query failed validation or execution.

Correct the SQL query while preserving the user's original intent.

Return only the corrected SQLite query.
""",
            ),
        ]
    )

    model = create_model(provider)
    parser = StrOutputParser()

    return prompt | model | parser
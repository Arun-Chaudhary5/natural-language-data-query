# Nexus AI: Natural Language Data Query System

Nexus AI is an enterprise-grade, natural language to SQL (Text-to-SQL) engine. It allows users to converse with a relational database using plain English. 

Built with **Python, FastAPI, and LangChain**, it features a highly robust evaluation pipeline, an intelligent error-correction loop, and a stunning Cyberpunk-inspired glassmorphism web interface built without heavy frontend frameworks.

![Nexus AI Demo](./static/demo-placeholder.png) <!-- Update this path with an actual screenshot of your UI -->

## 🚀 Key Features

*   **Multi-Provider LLM Support**: Seamlessly switch between OpenAI (`gpt-4o`), Google Gemini (`gemini-2.5-flash`), or any local LLM (via Ollama/vLLM) by changing a single environment variable.
*   **Self-Correcting SQL Generation**: If the LLM generates an invalid SQL query (e.g., hallucinated columns, syntax errors), the system catches the SQLite error and automatically re-prompts the model with the traceback for self-correction before returning a failure.
*   **Advanced Evaluation Suite**: Includes a rigorous 200-question automated benchmark testing framework to measure exact-match accuracy, execution accuracy, P50/P95 latencies, and error rates.
*   **Premium Web UI**: A beautiful, highly engaging, dynamic frontend built with pure HTML, CSS, and Vanilla JavaScript. Features interactive SQL rendering, dynamic tables, and responsive glassmorphism aesthetics.
*   **Production-Ready Engineering**: Implements Context Managers for safe database resource handling, comprehensive Python type-hinting, centralized domain exceptions (`QuerySystemError`), and full `pytest` coverage.

## 🛠️ Architecture

*   **Backend**: FastAPI, Python 3.11+
*   **LLM Orchestration**: LangChain
*   **Database**: SQLite (`ecommerce.db`)
*   **Frontend**: Vanilla HTML / CSS / JS
*   **Testing**: Pytest

## 📦 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Arun-Chaudhary5/natural-language-data-query-system.git
    cd natural-language-data-query-system
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Copy the `.env.example` file to a new file named `.env` and fill in your API keys.
    ```bash
    cp .env.example .env
    ```
    *Inside `.env`:*
    ```env
    OPENAI_API_KEY=your_openai_key_here
    GEMINI_API_KEY=your_gemini_key_here
    DEFAULT_PROVIDER=openai  # or gemini, local
    ```

## 🎮 Running the Application

To launch the beautiful web interface, run the FastAPI server:

```bash
python -m uvicorn app.api:app --reload
```

Open your browser and navigate to **http://127.0.0.1:8000** to interact with your data using natural language.

## 📊 Running the Evaluation Benchmark

To verify the system's accuracy against the 200-question dataset:

1.  **Run the benchmark:**
    ```bash
    python -m benchmark.run_benchmark --provider openai
    ```
2.  **Generate the summary report:**
    ```bash
    python -m benchmark.summarize_results
    ```
    This will produce a detailed `benchmark/results/benchmark_summary.md` detailing the execution match rate and latencies.

## 🧪 Testing

The codebase is thoroughly tested to ensure stability and correctness of the SQL validation and LLM pipeline. Run the test suite using:

```bash
pytest -v
```

## 📝 License

This project is licensed under the MIT License.

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.pipeline import TextToSQLPipeline

app = FastAPI(title="Natural Language Data Query System")

# Initialize the pipeline globally (using environment variables if they exist, or defaults)
provider = os.getenv("DEFAULT_PROVIDER", "local")
try:
    pipeline = TextToSQLPipeline(provider=provider)
except Exception as e:
    # If the provider initialization fails, we still want the app to start so we can show UI errors
    pipeline = None

# Create static directory if it doesn't exist
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

class QueryRequest(BaseModel):
    question: str
    
class QueryResponse(BaseModel):
    success: bool
    question: str
    sql: str | None = None
    result: dict | None = None
    error: str | None = None
    retries: int | None = None

@app.post("/api/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline failed to initialize (check provider configuration).")
    
    output = pipeline.run(request.question)
    
    return QueryResponse(
        success=output.get("success", False),
        question=output.get("question", ""),
        sql=output.get("sql"),
        result=output.get("result"),
        error=output.get("error"),
        retries=output.get("retries", 0),
    )

@app.post("/api/clear")
def clear_memory():
    if pipeline:
        pipeline.clear_memory()
    return {"status": "memory cleared"}

# Mount the static directory to serve HTML/CSS/JS
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    """Serves the main index.html file."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "index.html not found in static/ directory"}

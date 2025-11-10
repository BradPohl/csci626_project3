import os
import json
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

ROOT = Path(__file__).resolve().parent.parent

dotenv_path = ROOT / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path=str(dotenv_path))
    print("Loaded .env from:", dotenv_path)
else:
    # fallback to automatic search
    found = find_dotenv()
    if found:
        load_dotenv(found)
        print("Loaded .env via find_dotenv():", found)
    else:
        print("No .env found at", dotenv_path, "or by find_dotenv()")

# Load OpenAI API key from env
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    print("Warning: OPENAI_API_KEY not set. /api/ask will fail until it's provided.")
client = OpenAI(api_key=OPENAI_KEY)


DATA_PATH = ROOT / "dataset.json"

app = FastAPI(title="LLM helper for Papers Knowledge Graph")

# Allow local testing from any origin (dev). Lock this down in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Serve static files (index.html + scripts + json files) from the repo root
# Mount after routes is fine; FastAPI will match API paths first.
# app.mount("/", StaticFiles(directory=str(ROOT), html=True), name="static")


# In-memory map from ID -> document object
docs_by_id = {}

def load_dataset():
    global docs_by_id
    docs_by_id = {}
    if not DATA_PATH.exists():
        print(f"dataset.json not found at {DATA_PATH}")
        return
    raw = DATA_PATH.read_text(encoding="utf-8")
    try:
        arr = json.loads(raw)
    except Exception as e:
        print("Error parsing dataset.json:", e)
        return
    if isinstance(arr, list):
        for item in arr:
            if isinstance(item, dict) and item.get("ID"):
                docs_by_id[item["ID"]] = item
    else:
        # fallback: not an array — wrap keys as docs
        for k, v in (arr.items() if isinstance(arr, dict) else []):
            docs_by_id[k] = v

# Load at startup
load_dataset()

class AskRequest(BaseModel):
    question: str
    docIds: Optional[List[str]] = []

class AskResponse(BaseModel):
    answer: str

@app.get("/__reload_dataset")
def reload_dataset():
    load_dataset()
    return {"ok": True, "count": len(docs_by_id)}

def build_context(doc_ids: List[str], max_total_chars: int = 3500, per_doc_limit: int = 1500) -> str:
    """
    Build a concatenated context from the selected docs.
    Limits per-doc text and stops when max_total_chars reached.
    """
    parts = []
    total = 0
    for doc_id in doc_ids:
        doc = docs_by_id.get(doc_id)
        if not doc:
            continue
        # prefer REPORTDESCRIPTION field (your dataset uses REPORTDESCRIPTION)
        text = doc.get("REPORTDESCRIPTION") or doc.get("text") or json.dumps(doc)
        truncated = text[:per_doc_limit]
        header = f"DOC ID: {doc_id}\nREPORTDATE: {doc.get('REPORTDATE','')}\nSOURCE: {doc.get('REPORTSOURCE','')}\n"
        part = header + truncated
        if total + len(part) > max_total_chars:
            # stop adding more docs once we exceed budget
            break
        parts.append(part)
        total += len(part)
    return "\n\n---\n\n".join(parts)

@app.post("/api/ask", response_model=AskResponse)
def api_ask(payload: AskRequest):
    question = (payload.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question required")

    # Build context (truncated)
    context = build_context(payload.docIds or [])

    system_prompt = (
        "You are a helpful assistant that answers questions using ONLY the provided document context. "
        "If the answer is not contained in the context, say you don't know. When you reference facts, "
        "include the DOC ID in brackets (e.g., [FBI_3]). Be concise."
    )

    user_prompt = f"Question:\n{question}\n\nContext:\n{context or '[no documents provided]'}\n\nAnswer concisely."

    if not OPENAI_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured on server")

    try:
        # Classic ChatCompletion call using the python openai client
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2000,
            temperature=0.0,
        )

        # extract text — the object has choices -> message -> content
        answer = resp.choices[0].message.content.strip()
    except Exception as e:
        # Log server-side, return 500
        print("OpenAI error:", getattr(e, "args", e))
        raise HTTPException(status_code=500, detail="LLM provider error")

    return {"answer": answer}


app.mount("/", StaticFiles(directory=str(ROOT), html=True), name="static")

# If you want to run via `python server.py`, provide an entrypoint at the bottom.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
# Papers Knowledge Graph

An interactive D3-based web app that visualizes co-occurrence relationships (people / places) and lets you query selected documents with an LLM (OpenAI).

- Frontend: single-page `index.html` plus `scripts` (D3 visualizations, interactions).
- Backend: lightweight FastAPI app at `backend/server.py` that serves static files and proxies LLM requests to OpenAI.
- Data: `dataset.json` (array of documents, each with an `ID` and `REPORTDESCRIPTION`).

## Features

- Force-directed knowledge graph (center).
- Bar charts for top people & top places (left).
- Right panel: selected documents list and "Ask the LLM" input.
- Backend endpoint `/api/ask` accepts selected `docIds` + `question` and returns an LLM answer.

---

## Quick start (Windows cmd.exe)

1. Open a cmd.exe and change to the project root:

```bat
cd /d "route/to/project/csci626_project3"
```

2. Create and activate a virtual environment (recommended):

```bat
uv venv
.venv/Scripts/activate
```

3. Install dependencies:

```bat
pip install -r requirements.txt
```

4. Create `.env` in the project root (do NOT commit this):

```
OPENAI_API_KEY=sk-<your_api_key_here>
```

5. Start the server (FastAPI serves static files + API):

```bat
uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```
OR from the project root (Recommended)
```bat
python backend/server.py
```

6. Open the app:

- http://localhost:8000

---

## API

- POST `/api/ask`  
  Request JSON:
  ```json
  {
    "docIds": ["FBI_1", "CIA_2"],
    "question": "What happened with X?"
  }
  ```
  Response JSON:
  ```json
  { "answer": "..." }
  ```

- GET `/__reload_dataset`  
  Reloads `dataset.json` into memory and returns `{"ok": true, "count": N}`.

---

## Data format

The app expects `dataset.json` to be an array of objects. Each object should include at least:

```json
{
  "ID": "FBI_1",
  "REPORTDATE": "...",
  "REPORTSOURCE": "...",
  "REPORTDESCRIPTION": "Full text...",
  "PERSONS": [...],
  "PLACES": [...]
}
```

The backend maps documents by their `ID` (e.g., `FBI_1`). The frontend `selectedDocIds` sends these IDs to `/api/ask`.

---

## Dev notes & common troubleshooting

- 405 / 501 on `/api/ask`: this usually means a plain static server (e.g., `python -m http.server`) is running on the same port and rejecting POST/OPTIONS. Stop any static server and start uvicorn as above so the FastAPI app handles API routes and static files.

- StaticFiles mount ordering: ensure `app.mount("/", StaticFiles(...))` is located *after* your route definitions in `backend/server.py`. If mounted first, StaticFiles will capture `/api/ask` and refuse POST.

- `.env` not loaded in VS Code integrated terminal:
  - Option 1 (recommended): `backend/server.py` calls `load_dotenv()` and explicitly loads `.env` from the project root (already implemented in `backend/server.py`).
  - Option 2: enable VS Code workspace setting `python.terminal.useEnvFile` and restart the integrated terminal.
  - Option 3: set variable manually in the shell before starting uvicorn:
    ```bat
    set OPENAI_API_KEY=sk-...
    uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
    ```

- OpenAI SDK errors (migration): The modern `openai` client (v1+) uses `from openai import OpenAI` and `client.chat.completions.create(...)`. If your environment has the older v0.28 API, either update code (preferred) or pin the old version:
  ```bat
  pip install "openai==0.28.0"
  ```

- Confirm OpenAI key visible:
  ```bat
  python -c "import os; print('OPENAI_API_KEY=' + str(os.getenv('OPENAI_API_KEY')))"
  ```

---

## Generating `requirements.txt`

- If you want an exact snapshot of your venv:
  ```bat
  pip freeze > requirements.txt
  ```

- Or create a minimal `requirements.in` and pin with `pip-tools`:
  ```bat
  pip install pip-tools
  echo fastapi > requirements.in
  echo uvicorn[standard] >> requirements.in
  echo python-dotenv >> requirements.in
  echo openai >> requirements.in
  pip-compile requirements.in --output-file=requirements.txt
  ```

---

## Security & cost

- Never commit `.env` or `OPENAI_API_KEY` to version control. Add `.env` to `.gitignore`.
- LLM usage incurs cost. Use `gpt-3.5-turbo` for dev; set `temperature` low to reduce hallucinations.

---

## File layout (quick)

- `index.html` — main UI
- `scripts` — `scripts/state.js`, `scripts/graph.js`, `scripts/bar.js`, `scripts/interactions.js`, `scripts/init.js`
- `backend/server.py` — FastAPI backend + OpenAI integration
- `dataset.json` — documents array (IDs + descriptions)
- other data files: `bars1.json`, `graph1.json`

---

## Example curl test

```bat
curl -i -X POST http://localhost:8000/api/ask -H "Content-Type: application/json" -d "{\"question\":\"Who appears in FBI_1?\",\"docIds\":[\"FBI_1\"]}"
```

---

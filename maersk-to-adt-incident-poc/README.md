# Maersk to ADT Incident POC

This proof-of-concept project ingests Maersk survey reports (PDF or image), extracts vessel metadata and defects, maps data to ADT incident fields, and synchronizes with the ADT API. The full workflow is stored in a SQLite database.

## Structure

```
maersk-to-adt-incident-poc/
  app/                # application code
  config/             # mapping and other configuration
  data/               # SQLite database file (created at runtime)
  tests/              # unit tests
  Dockerfile
  docker-compose.yml
  requirements.txt
```

## Environment Variables

- `ADT_BASE_URL` – base URL for ADT API
- `ADT_AUTH_HEADER` – authorization header (e.g. `Bearer ...`)
- `DB_URL` – SQLAlchemy URL (e.g. `postgresql+psycopg2://user:pass@host/db` or `sqlite:///./data/poc.db`)
- `OCR_ENABLED` – `true`/`false` to enable OCR fallback
- `TESSERACT_CMD` – path to tesseract binary if nonstandard
- `MOCK_ADT` – `true` to run internal mock ADT service
- `adt_timeout`, `adt_retries` – client timeouts

### Azure OpenAI

- `AZURE_OPENAI_ENDPOINT` – full endpoint URL for Azure OpenAI
- `AZURE_OPENAI_API_KEY` – API key
- `AZURE_OPENAI_DEPLOYMENT_NAME` – deployment/model name (e.g. `gpt-4o`)
- `AZURE_OPENAI_API_VERSION` – (optional) API version, default `2023-05-15`

### PostgreSQL

Set `DB_URL` appropriately and ensure Postgres is running. The provided `docker-compose.yml` can spin up a database:

```bash
docker-compose up -d db
# wait a moment, then (from host) export DB_URL=postgresql+psycopg2://user:pass@localhost/maersk
```

Tables are created automatically on first access.

## Setup

```bash
git clone <repo>
cd maersk-to-adt-incident-poc
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

### CLI

```bash
# set environment variables as appropriate (use mock if you don't have real API)
export MOCK_ADT=true
# or specify a real base URL and auth header
# export ADT_BASE_URL=https://api.example.com
# export ADT_AUTH_HEADER="Bearer ..."

python -m app.cli ingest --file path/to/report.pdf
```
Outputs `extracted.json`, `mapped_payload.json`, `adt_result.json` in CWD.

### Gradio UI

Requires Azure environment variables and a working DB connection. Launch:

```bash
# e.g. using sqlite or postgres
export DB_URL=sqlite:///./data/poc.db
export AZURE_OPENAI_ENDPOINT=https://...
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

python -m app.gradio_app
```

Open browser at the printed URL, upload a report, and view outputs.

### FastAPI service

```bash
uvicorn app.main:app --reload
```

- `POST /ingest` accepts multipart file uploads; returns extraction/ADT result
- `GET /runs/{id}` returns stored data

### Docker

```bash
docker-compose up --build
```

API will be available at `http://localhost:8000`.

## Tests

```bash
pytest
```

## Notes

- Extraction is naive and may require extension with regex patterns or NLP.
- Mapping rules live in `config/mapping.yaml` and can be extended.
- Mock ADT server runs when `MOCK_ADT=true` and stores incidents in memory.
- Database tables created automatically on first run.

---

Enjoy the POC!

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .config import settings
from .extractor.ingest import process_file
from .db.repository import create_extraction_run, get_extraction_run
from .adt.client import sync_incident
import hashlib
import json

app = FastAPI(title="Maersk to ADT Incident POC")

@app.on_event("startup")
def startup_event():
    # ensure database tables exist
    from .db.session import init_db
    init_db()

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    contents = await file.read()
    # hash
    file_hash = hashlib.sha256(contents).hexdigest()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(contents)
    try:
        extracted = process_file(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # map
    from .mapper.map_to_adt import map_extraction
    mapped = map_extraction(extracted)
    # store run
    run = create_extraction_run(file.filename, file_hash, extracted, mapped)
    # call ADT
    adt_resp = sync_incident(mapped)
    from .db.repository import log_adt_sync
    try:
        log_adt_sync(run.id, adt_resp.get('action'),
                     adt_resp.get('response', {}).get('id'),
                     mapped, adt_resp.get('response'), 200, True)
    except Exception:
        pass
    return {
        "extracted": extracted,
        "mapped": mapped,
        "adt": adt_resp,
        "extraction_run_id": run.id,
    }

@app.get("/runs/{id}")
def get_run(id: int):
    run = get_extraction_run(id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.to_dict()
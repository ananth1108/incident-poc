import requests
from ..config import settings
from . import mock_server


def _headers():
    h = {}
    if settings.adt_auth_header:
        h['Authorization'] = settings.adt_auth_header
    return h


def search_incident(imo: str, job_number: str):
    if settings.mock_adt:
        return mock_server.search(imo, job_number)
    params = {'imo': imo, 'jobNumber': job_number}
    r = requests.get(f"{settings.adt_base_url}/incidents/search", params=params,
                     headers=_headers(), timeout=settings.adt_timeout)
    r.raise_for_status()
    return r.json()


def create_incident(payload: dict):
    if settings.mock_adt:
        return mock_server.create(payload)
    r = requests.post(f"{settings.adt_base_url}/incidents", json=payload,
                      headers=_headers(), timeout=settings.adt_timeout)
    r.raise_for_status()
    return r.json()


def update_incident(incident_id: str, payload: dict):
    if settings.mock_adt:
        return mock_server.update(incident_id, payload)
    r = requests.put(f"{settings.adt_base_url}/incidents/{incident_id}", json=payload,
                     headers=_headers(), timeout=settings.adt_timeout)
    r.raise_for_status()
    return r.json()


def sync_incident(mapped: dict):
    imo = mapped.get('imo') or (mapped.get('vessel', {}) or {}).get('imo')
    job = mapped.get('job_number')
    existing = None
    if imo and job:
        try:
            res = search_incident(imo, job)
            if res and isinstance(res, list) and res:
                existing = res[0]
        except Exception:
            existing = None
    if existing:
        resp = update_incident(existing.get('id'), mapped)
        action = 'update'
    else:
        resp = create_incident(mapped)
        action = 'create'
    # log to DB if available
    try:
        from ..db.repository import log_adt_sync
        log_adt_sync(
            run_id=None,
            action=action,
            incident_id=resp.get('id'),
            request_json=mapped,
            response_json=resp,
            status_code=200,
            success=True,
        )
    except Exception:
        pass
    return {'action': action, 'response': resp}

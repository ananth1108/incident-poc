# simple in-memory mock
mock_db = []

def search(imo, job):
    return [r for r in mock_db if r.get('imo') == imo and r.get('job_number') == job]

def create(payload):
    payload = payload.copy()
    payload['id'] = str(len(mock_db)+1)
    mock_db.append(payload)
    return payload

def update(incident_id, payload):
    for i, r in enumerate(mock_db):
        if r.get('id') == incident_id:
            mock_db[i].update(payload)
            return mock_db[i]
    raise ValueError('not found')

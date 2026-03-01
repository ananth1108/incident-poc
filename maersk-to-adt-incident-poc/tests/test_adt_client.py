import os
from app.adt import client
from app.config import settings

def test_mock_create_update(monkeypatch):
    # ensure mock enabled
    settings.mock_adt = True
    settings.adt_base_url = "http://example"
    # create first
    payload = {'imo': '123', 'job_number': 'J1'}
    res1 = client.sync_incident(payload)
    assert res1['action'] == 'create'
    assert res1['response']['id'] == '1'
    # update same
    res2 = client.sync_incident(payload)
    assert res2['action'] == 'update'
    assert res2['response']['id'] == '1'
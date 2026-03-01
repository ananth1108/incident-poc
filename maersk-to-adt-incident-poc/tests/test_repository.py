from app.db import session
from app.db import repository
from app.config import settings
import os



def test_save_and_query(tmp_path):
    # use a fresh sqlite file per test
    from app.config import settings
    dbfile = tmp_path / "db.sqlite"
    settings.db_url = f"sqlite:///{dbfile}"
    session._init_engine()
    session.init_db()
    ext = {
        "vessel": {"name": "X", "imo": "999", "flag": "F", "vessel_type": "T"},
        "report": {"job_number": "J9", "report_number": "R9"},
        "defects": [{"defect_summary": "D1", "severity": "Low", "evidence_quote": "Quote"}]
    }
    run = repository.save_extraction("file.pdf", "rawtext", ext)
    assert run.id is not None
    defects = repository.get_latest_defects(5)
    assert len(defects) == 1
    assert defects[0]["defect_summary"] == "D1"

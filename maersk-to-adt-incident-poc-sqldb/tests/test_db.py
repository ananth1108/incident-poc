import os


def test_db_create(tmp_path, monkeypatch):
    # override DB_URL before modules create engines
    from app.config import settings
    dbfile = tmp_path / "test.db"
    settings.db_url = f"sqlite:///{dbfile}"
    # now import repository and session
    from app.db import session
    from app.db.repository import save_extraction, get_extraction_run
    session.init_db()
    # use the new save_extraction signature
    run = save_extraction('file.pdf', 'raw', {'vessel': {}, 'report': {}, 'defects': []})
    fetched = get_extraction_run(run.id)
    assert fetched['file_name'] == 'file.pdf'
    assert fetched['extracted_json'] == {'vessel': {}, 'report': {}, 'defects': []}

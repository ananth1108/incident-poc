import json
from .models import Vessel, Report, Defect, ExtractionRun

# functions will import SessionLocal/init_db lazily to avoid early engine creation


# legacy helper removed; use save_extraction for new schema

def save_extraction(file_name, raw_text, extraction: dict):
    """Persist a run plus vessel/report/defects into DB."""
    from . import session
    session._init_engine()
    session.init_db()
    db = session.SessionLocal()
    try:
        # vessel
        vessel_data = extraction.get('vessel', {})
        vessel = None
        if vessel_data.get('imo'):
            vessel = db.query(Vessel).filter(Vessel.imo == vessel_data.get('imo')).first()
        if not vessel:
            vessel = Vessel(
                name=vessel_data.get('name'),
                imo=vessel_data.get('imo'),
                flag=vessel_data.get('flag'),
                vessel_type=vessel_data.get('vessel_type'),
            )
            db.add(vessel)
            db.commit()
            db.refresh(vessel)
        # report
        report_data = extraction.get('report', {})
        report = Report(
            vessel_id=vessel.id,
            job_number=report_data.get('job_number'),
            report_number=report_data.get('report_number'),
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        # defects
        for d in extraction.get('defects', []):
            def_obj = Defect(
                report_id=report.id,
                defect_summary=d.get('defect_summary'),
                defect_type=d.get('defect_type'),
                location=d.get('location'),
                location_detail=d.get('location_detail'),
                severity=d.get('severity'),
                recommended_action=d.get('recommended_action'),
                evidence_quote=d.get('evidence_quote'),
            )
            db.add(def_obj)
        db.commit()
        # run entry
        run = ExtractionRun(
            file_name=file_name,
            status='completed',
            raw_text=raw_text,
            extracted_json=json.dumps(extraction),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run
    finally:
        db.close()


def get_latest_defects(limit=10):
    from . import session
    session._init_engine()
    db = session.SessionLocal()
    try:
        rows = db.query(Defect).order_by(Defect.id.desc()).limit(limit).all()
        result = []
        for r in rows:
            entry = {c.name: getattr(r, c.name) for c in r.__table__.columns}
            result.append(entry)
        return result
    finally:
        db.close()


def get_extraction_run(id):
    from . import session
    session._init_engine()
    session.init_db()
    db = session.SessionLocal()
    try:
        run = db.query(ExtractionRun).filter(ExtractionRun.id == id).first()
        if run:
            return {
                'id': run.id,
                'file_name': run.file_name,
                'status': run.status,
                'raw_text': run.raw_text,
                'extracted_json': json.loads(run.extracted_json),
                'created_at': run.created_at.isoformat() if run.created_at else None,
            }
        return None
    finally:
        db.close()


def log_adt_sync(run_id, action, incident_id, request_json, response_json, status_code, success):
    from . import session
    session._init_engine()
    db = session.SessionLocal()
    from .models import ADTSync
    try:
        sync = ADTSync(
            extraction_run_id=run_id,
            action=action,
            incident_id=incident_id,
            request_json=json.dumps(request_json),
            response_json=json.dumps(response_json),
            status_code=status_code,
            success=success,
        )
        db.add(sync)
        db.commit()
        db.refresh(sync)
        return sync
    finally:
        db.close()


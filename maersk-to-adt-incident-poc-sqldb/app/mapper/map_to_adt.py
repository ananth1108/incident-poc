from ..config import settings
import yaml
import os
from datetime import datetime

def load_mapping():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'mapping.yaml'))
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def summarize_defects(defects):
    if not defects:
        return None
    summaries = [d.get('defect_summary') for d in defects if d.get('defect_summary')]
    top = summaries[:3]
    return '; '.join(top)[:500]


def determine_incident_type(defects):
    text = ' '.join([d.get('defect_summary','').lower() for d in defects])
    if 'anchor' in text:
        return 'ANCHOR FAILURE'
    if 'ballast' in text and 'structural' in text:
        return 'STRUCTURAL DEFECT'
    return 'OTHER'


def map_extraction(extraction: dict) -> dict:
    mapping = load_mapping()
    # direct conversions
    adt = {
        'imo': extraction.get('vessel', {}).get('imo'),
        'request_date': extraction.get('report', {}).get('request_date'),
        'reported_date': extraction.get('report', {}).get('reported_date'),
        'type': 'Ship Defect - Hull',
        'problem_summary': summarize_defects(extraction.get('defects', [])),
        'severity': extraction.get('defects', [{}])[0].get('severity') or 'NOT KNOWN',
        'status': 'Open',
        'job_number': extraction.get('report', {}).get('job_number'),
        'incident_type': determine_incident_type(extraction.get('defects', [])),
        'incident_date': extraction.get('report', {}).get('reported_date'),
        'incident_group': 'OTHER',
    }
    return adt

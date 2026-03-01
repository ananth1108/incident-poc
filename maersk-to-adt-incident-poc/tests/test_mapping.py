from app.mapper.map_to_adt import map_extraction

def test_mapping_simple():
    extraction = {
        'report': {'job_number': 'J1', 'reported_date': '02/02/2020', 'request_date': '01/02/2020'},
        'defects': [
            {'defect_summary': 'Anchor damaged'},
            {'defect_summary': 'Ballast tank structural wastage'}
        ]
    }
    mapped = map_extraction(extraction)
    assert mapped['job_number'] == 'J1'
    assert 'Anchor' in mapped['problem_summary'] or mapped['incident_type']
    assert mapped['incident_type'] in ['ANCHOR FAILURE','STRUCTURAL DEFECT','OTHER']

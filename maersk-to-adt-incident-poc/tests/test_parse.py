from app.extractor.parse import parse_text

def test_simple_parse():
    text = """
Vessel Name: TestShip
IMO: 1234567
Job Number: JOB123
Request Date: 01/01/2020
- Defect one
- Defect two
"""
    result = parse_text(text)
    assert result['vessel']['name'] == 'TestShip'
    assert result['vessel']['imo'] == '1234567'
    assert result['report']['job_number'] == 'JOB123'
    assert len(result['defects']) == 2
    assert result['defects'][0]['defect_summary'] == 'Defect one'

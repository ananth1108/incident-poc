import re
from .schema import Extraction


def parse_text(text: str) -> dict:
    # simple line-based parsing
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    vessel = {}
    report = {}
    sections = []
    defects = []

    # patterns
    imo_re = re.compile(r'IMO\s*[:\-]?\s*(\d{7})', re.IGNORECASE)
    name_re = re.compile(r'Vessel\s+Name\s*[:\-]?\s*(.+)', re.IGNORECASE)
    job_re = re.compile(r'(Job|Report)\s*Number\s*[:\-]?\s*(\S+)', re.IGNORECASE)
    date_re = re.compile(r'(Request|Reported|Incident)\s+Date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{2,4})', re.IGNORECASE)

    current_section = None
    current_text = []

    for line in lines:
        # metadata
        m = imo_re.search(line)
        if m:
            vessel['imo'] = m.group(1)
        m = name_re.search(line)
        if m:
            vessel['name'] = m.group(1)
        m = job_re.search(line)
        if m:
            report['job_number'] = m.group(2)
        m = date_re.search(line)
        if m:
            key = m.group(1).lower() + '_date'
            report[key] = m.group(2)
        # section headings
        if re.match(r'(Survey Code|Section)[:]?\s*', line, re.IGNORECASE):
            if current_section:
                sections.append(current_section)
            current_section = {'survey_code': None, 'title': line, 'text': ''}
        elif current_section:
            current_section['text'] += line + '\n'
        # defects - bullet points
        if line.startswith('-') or line.startswith('*'):
            summary = line.lstrip('-* ').strip()
            defects.append({
                'defect_summary': summary,
                'evidence_quote': summary
            })
    if current_section:
        sections.append(current_section)
    extraction = Extraction(
        vessel=vessel,
        report=report,
        sections=sections,
        defects=defects
    )
    # return plain dict for compatibility
    return extraction.model_dump()

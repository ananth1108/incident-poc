from typing import List, Optional
from pydantic import BaseModel


class Vessel(BaseModel):
    name: Optional[str] = None
    imo: Optional[str] = None
    flag: Optional[str] = None
    vessel_type: Optional[str] = None


class Report(BaseModel):
    job_number: Optional[str] = None
    report_number: Optional[str] = None
    request_date: Optional[str] = None
    reported_date: Optional[str] = None


class Section(BaseModel):
    survey_code: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None


class Defect(BaseModel):
    defect_summary: Optional[str] = None
    defect_type: Optional[str] = None
    location: Optional[str] = None
    location_detail: Optional[str] = None
    severity: Optional[str] = None
    recommended_action: Optional[str] = None
    evidence_quote: Optional[str] = None


class Extraction(BaseModel):
    vessel: Vessel
    report: Report
    sections: List[Section] = []
    defects: List[Defect] = []

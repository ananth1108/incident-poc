from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


def now():
    return datetime.datetime.utcnow()


class Vessel(Base):
    __tablename__ = 'vessels'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    imo = Column(String, index=True)
    flag = Column(String)
    vessel_type = Column(String)
    created_at = Column(DateTime, default=now)
    reports = relationship('Report', back_populates='vessel')


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    vessel_id = Column(Integer, ForeignKey('vessels.id'))
    job_number = Column(String)
    report_number = Column(String)
    created_at = Column(DateTime, default=now)
    vessel = relationship('Vessel', back_populates='reports')
    defects = relationship('Defect', back_populates='report')


class Defect(Base):
    __tablename__ = 'defects'
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'))
    defect_summary = Column(Text)
    defect_type = Column(String)
    location = Column(String)
    location_detail = Column(String)
    severity = Column(String)
    recommended_action = Column(Text)
    evidence_quote = Column(Text)
    created_at = Column(DateTime, default=now)
    report = relationship('Report', back_populates='defects')


class ExtractionRun(Base):
    __tablename__ = 'extraction_runs'
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    status = Column(String)
    raw_text = Column(Text)
    extracted_json = Column(Text)
    created_at = Column(DateTime, default=now)


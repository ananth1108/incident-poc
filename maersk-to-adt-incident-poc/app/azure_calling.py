import os
import json
from typing import List, Optional
from pydantic import BaseModel

import openai


class VesselModel(BaseModel):
    name: Optional[str]
    imo: Optional[str]
    flag: Optional[str]
    vessel_type: Optional[str]


class ReportModel(BaseModel):
    job_number: Optional[str]
    report_number: Optional[str]


class DefectModel(BaseModel):
    defect_summary: Optional[str]
    defect_type: Optional[str]
    location: Optional[str]
    location_detail: Optional[str]
    severity: Optional[str]
    recommended_action: Optional[str]
    evidence_quote: Optional[str]


class ExtractionModel(BaseModel):
    vessel: VesselModel
    report: ReportModel
    defects: List[DefectModel]


def _configure_client():
    openai.api_type = "azure"
    openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
    openai.api_key = os.environ.get("AZURE_OPENAI_API_KEY")


def parse_with_gpt(text: str) -> dict:
    """Call Azure GPT-4o with function calling to parse the given text."""
    # allow mocking without actual Azure call
    if os.environ.get("MOCK_GPT", "").lower() == "true":
        # simple dummy responder - real deployments should supply a key
        return {"vessel": {"name": None, "imo": None, "flag": None, "vessel_type": None},
                "report": {"job_number": None, "report_number": None},
                "defects": []}
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not deployment:
        raise RuntimeError("AZURE_OPENAI_DEPLOYMENT_NAME env var not set")
    _configure_client()
    # use v2 API; schema() still works but warn, so switch to model_json_schema
    schema = ExtractionModel.model_json_schema()
    function = {
        "name": "parse_report",
        "description": "Extract vessel and defect details from the survey report text",
        "parameters": schema,
    }
    resp = openai.ChatCompletion.create(
        engine=deployment,
        messages=[
            {"role": "system", "content": "You are an assistant that extracts vessel metadata and defect information from Maersk survey reports."},
            {"role": "user", "content": text},
        ],
        functions=[function],
        function_call="auto",
        temperature=0,
    )
    choice = resp.choices[0]
    msg = choice.message
    if msg.get("function_call"):
        args = msg["function_call"]["arguments"]
        parsed = json.loads(args)
        validated = ExtractionModel(**parsed)
        # v2 uses model_dump
        return validated.model_dump()
    raise ValueError("No function call returned by model")

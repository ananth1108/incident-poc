import json
from app.azure_calling import parse_with_gpt, ExtractionModel

class DummyResponse:
    def __init__(self, arguments):
        self.choices = [self]
        self.message = {"function_call": {"arguments": arguments}}


def test_parse_with_gpt(monkeypatch):
    sample_text = "Vessel Name: A\nIMO: 111\nJob Number: J1\n- Defect x"
    expected = {
        "vessel": {"name": "A", "imo": "111", "flag": None, "vessel_type": None},
        "report": {"job_number": "J1", "report_number": None},
        "defects": [{"defect_summary": "Defect x", "defect_type": None, "location": None, "location_detail": None, "severity": None, "recommended_action": None, "evidence_quote": None}]
    }
    # patch openai
    def fake_create(**kwargs):
        return DummyResponse(json.dumps(expected))
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_NAME","dummy")
    import openai
    monkeypatch.setattr(openai.ChatCompletion, 'create', staticmethod(fake_create))
    result = parse_with_gpt(sample_text)
    assert result == expected

    # also verify mock mode returns minimal structure
    monkeypatch.setenv("MOCK_GPT","true")
    mock_res = parse_with_gpt(sample_text)
    assert mock_res.get("defects") == []

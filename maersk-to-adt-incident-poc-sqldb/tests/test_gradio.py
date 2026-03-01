from app import gradio_app
from app.azure_calling import ExtractionModel


def test_process_report(monkeypatch, tmp_path):
    # create a dummy file that will be "uploaded"
    tmp = tmp_path / "report.pdf"
    tmp.write_text("dummy content")

    # stub out the text extraction so we don't need real PDF processing
    monkeypatch.setattr(gradio_app, "extract_text_from_pdf", lambda path: "extracted text")
    monkeypatch.setattr(gradio_app, "extract_text_from_image", lambda path: "extracted text")

    # stub out the GPT caller to return a predictable structure
    def fake_extract_with_gpt(text):
        model = ExtractionModel(
            vessel={"name": "Vessel123", "imo": None, "flag": None, "vessel_type": None},
            report={"job_number": None, "report_number": None},
            defects=[{"defect_summary": "scratch", "defect_type": None, "location": None, "location_detail": None, "severity": None, "recommended_action": None, "evidence_quote": None}],
        )
        return model.model_dump()

    # patch the function that gradio_app actually calls (imported at module level)
    monkeypatch.setattr(gradio_app, "parse_with_gpt", fake_extract_with_gpt)

    # stub out the repository calls that gradio_app imported at module load
    monkeypatch.setattr(gradio_app, "save_extraction", lambda *args, **kwargs: None)
    monkeypatch.setattr(gradio_app, "get_latest_defects", lambda limit: [])

    json_output, tables, status = gradio_app.process_report(tmp)

    # ensure structure is present
    assert isinstance(json_output, dict)
    assert json_output.get("vessel", {}).get("name") == "Vessel123"
    assert json_output.get("defects", [])[0].get("defect_summary") == "scratch"
    assert status == "Success"
    # tables is a list of defect dicts
    assert isinstance(tables, list)

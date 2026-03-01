import os
import json
import gradio as gr
from .extractor.ingest import extract_text_from_pdf, extract_text_from_image
from .azure_calling import parse_with_gpt
from .db.repository import save_extraction, get_latest_defects


def process_report(uploaded_file):
    if uploaded_file is None:
        return {}, [], "No file provided"
    path = uploaded_file.name
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(path)
    else:
        text = extract_text_from_image(path)
    try:
        result = parse_with_gpt(text)
    except Exception as e:
        return {}, [], f"GPT error: {e}"
    # persist to db
    save_extraction(os.path.basename(path), text, result)
    defects = get_latest_defects(20)
    return result, defects, "Success"


def launch():
    with gr.Blocks() as demo:
        gr.Markdown("# Maersk Survey → ADT Extractor")
        upload = gr.File(label="Upload report (PDF/image)")
        process_btn = gr.Button("Process Report")
        output_json = gr.JSON(label="Extracted JSON")
        output_table = gr.Dataframe(label="Latest defects",
                                   headers=["id","report_id","defect_summary","severity","created_at"],
                                   datatype="auto")
        status = gr.Textbox(label="Status")
        process_btn.click(fn=process_report,
                          inputs=upload,
                          outputs=[output_json, output_table, status])
    demo.launch()


if __name__ == "__main__":
    launch()

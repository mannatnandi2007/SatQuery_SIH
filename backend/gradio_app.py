"""
SatQuery AI — Gradio Chat QA Surface
Provides conversational satellite question answering with:
- Image upload (single, bi-temporal, optical+SAR)
- Chat QA with multi-box visual grounding overlays
- Dynamic next-query recommendation chips that re-submit to N1
"""

import os
import sys
from io import BytesIO
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    import gradio as gr  # type: ignore
    GRADIO_AVAILABLE = True
except ImportError:
    gr = None  # type: ignore
    GRADIO_AVAILABLE = False



def create_gradio_app():
    if not GRADIO_AVAILABLE:
        print("[Gradio] Gradio not installed. Run `pip install gradio` to launch chat surface.")
        return None

    import asyncio
    from orchestrator import orchestrator

    async def chat_handler(message: str, history: List, image_files: Optional[List[str]]):
        if not image_files or len(image_files) == 0:
            return history + [(message, "Please upload at least one satellite image file to begin analysis.")], None, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

        filenames = [os.path.basename(f) for f in image_files]
        file_contents = []
        for f in image_files:
            with open(f, "rb") as fp:
                file_contents.append(fp.read())

        status_code, response = await orchestrator.process_query(filenames, file_contents, message)
        data = response.to_dict()

        if status_code != 200 or data.get("error"):
            error_msg = data.get("answer", "Pipeline error during processing.")
            return history + [(message, f"**Error:** {error_msg}")], None, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

        answer_text = data.get("answer", "")
        overlay_url = data.get("evidence", {}).get("overlay_image_url")
        overlay_path = None
        if overlay_url:
            clean_name = os.path.basename(overlay_url)
            cand = os.path.join(os.path.dirname(__file__), "static", "overlays", clean_name)
            if os.path.exists(cand):
                overlay_path = cand

        suggestions = data.get("suggestions", [])
        chip_updates = [gr.update(visible=False, value="")] * 3
        for i, s in enumerate(suggestions[:3]):
            chip_updates[i] = gr.update(visible=True, value=f"[{s['task_type']}] {s['text']}")

        new_history = history + [(message, answer_text)]
        return new_history, overlay_path, chip_updates[0], chip_updates[1], chip_updates[2]

    with gr.Blocks(title="SatQuery AI — Chat QA Surface") as demo:
        gr.Markdown("# 🛰️ SatQuery AI — Conversational Earth Observation QA")
        gr.Markdown("Visual Question Answering & Multi-Box Grounding with Dynamic Follow-Up Recommendations")

        with gr.Row():
            with gr.Column(scale=1):
                image_upload = gr.File(label="Upload Satellite Images", file_count="multiple", file_types=[".png", ".jpg", ".tif", ".tiff"])
                evidence_preview = gr.Image(label="Multi-Box Grounding Overlay (Node N11)", interactive=False)

            with gr.Column(scale=2):
                chatbot = gr.Chatbot(label="SatQuery Telemetry Chat", height=480)
                query_box = gr.Textbox(label="Visual Query (Node N1)", placeholder="Inquire about objects, buildings, bi-temporal changes...")

                gr.Markdown("### Recommended Next Queries (Node N10)")
                with gr.Row():
                    chip1 = gr.Button(visible=False, variant="secondary", size="sm")
                    chip2 = gr.Button(visible=False, variant="secondary", size="sm")
                    chip3 = gr.Button(visible=False, variant="secondary", size="sm")

                submit_btn = gr.Button("Submit Query", variant="primary")

        async def run_query(q, hist, imgs):
            return await chat_handler(q, hist, imgs)

        submit_btn.click(run_query, inputs=[query_box, chatbot, image_upload], outputs=[chatbot, evidence_preview, chip1, chip2, chip3])

        # Chip click handlers (click-to-resubmit to N1)
        def click_chip(chip_label):
            # Extract query text after "[task_type] "
            if "]" in chip_label:
                return chip_label.split("]", 1)[1].strip()
            return chip_label

        chip1.click(click_chip, inputs=[chip1], outputs=[query_box])
        chip2.click(click_chip, inputs=[chip2], outputs=[query_box])
        chip3.click(click_chip, inputs=[chip3], outputs=[query_box])

    return demo


if __name__ == "__main__":
    app = create_gradio_app()
    if app:
        app.launch(server_name="0.0.0.0", server_port=7860)

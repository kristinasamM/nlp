"""
=============================================================================
VivaPrep: NLP-Powered Viva Voce Preparation & Assessment System
FastAPI Backend & Pipeline Web Server
=============================================================================
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from pipeline import VivaPipeline
from config import TEAM_MODULE_MAP

app = FastAPI(
    title="VivaPrep: NLP Viva Voce Preparation & Document Verification System",
    description="A student-built NLP system for oral exam practice, citation grounding, and rubric-based answer evaluation."
)

# Pipeline instance
pipeline = VivaPipeline()

# Paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
SAMPLES_DIR = BASE_DIR / "sample_documents"

# Ensure directories exist
try:
    STATIC_DIR.mkdir(exist_ok=True)
    SAMPLES_DIR.mkdir(exist_ok=True)
except Exception:
    pass

# Pre-load default sample document on startup
default_sample = SAMPLES_DIR / "transformers_and_attention.txt"
if default_sample.exists():
    default_text = default_sample.read_text(encoding="utf-8")
    pipeline.process_text(default_text, document_name="Transformers Capstone Report")


# Request Models
class ProcessRequest(BaseModel):
    text: str
    document_name: Optional[str] = "Pasted Technical Document"


class EvaluateRequest(BaseModel):
    question_id: str
    student_answer: str


# ---------------------------------------------------------------------------
# REST API ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/api/samples")
async def list_samples():
    """List all available sample documents."""
    samples = []
    for f in SAMPLES_DIR.glob("*.txt"):
        samples.append({
            "filename": f.name,
            "title": f.stem.replace("_", " ").title(),
            "size_kb": round(f.stat().st_size / 1024, 1)
        })
    return {"samples": samples}


@app.get("/api/sample/{filename}")
async def get_sample(filename: str):
    """Retrieve text content of a specific sample document."""
    file_path = SAMPLES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample not found")
    try:
        content = file_path.read_text(encoding="utf-8")
        return {"filename": filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process")
async def process_document(payload: ProcessRequest):
    """Run full NLP pipeline on provided raw text."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")
    summary = pipeline.process_text(payload.text, document_name=payload.document_name)
    return summary


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload PDF, Markdown, or TXT file and run pipeline."""
    import tempfile
    temp_dir = Path(tempfile.gettempdir()) / "vivacraft_upload"
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_dest = temp_dir / file.filename

    try:
        content = await file.read()
        file_dest.write_bytes(content)

        raw_text = pipeline.preprocessor.extract_text_from_file(str(file_dest))
        summary = pipeline.process_text(raw_text, document_name=file.filename)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        if file_dest.exists():
            try:
                os.remove(file_dest)
            except Exception:
                pass


@app.get("/api/state")
async def get_pipeline_state():
    """Fetch current pipeline state, question bank, and document text."""
    return pipeline.get_summary()


@app.post("/api/evaluate")
async def evaluate_answer(payload: EvaluateRequest):
    """Evaluate student oral response against question citation."""
    res = pipeline.evaluate_answer(payload.question_id, payload.student_answer)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@app.get("/api/download")
async def download_questions(include_answers: bool = False):
    """Download questions or questions and suggested answers as formatted text."""
    doc_name = pipeline.document_name or "VivaCraft_Notes"
    lines = [
        f"VivaCraft: Viva Voce Practice Questions",
        f"Notes: {doc_name}",
        "=" * 60,
        ""
    ]
    for idx, q in enumerate(pipeline.questions):
        diff = q.get("difficulty", "Medium")
        topic = q.get("section_title", "General")
        lines.append(f"Question {idx + 1} [{diff}] - Topic: {topic}")
        lines.append(f"Q: {q.get('question_text')}")
        if include_answers:
            ans = q.get("suggested_answer") or q.get("model_answer", "")
            lines.append(f"\nSuggested Answer:\n{ans}")
            citation = q.get("source_citation", "")
            if citation:
                lines.append(f"\nFrom Your Notes:\n\"{citation}\"")
        lines.append("-" * 50)
        lines.append("")

    from fastapi.responses import Response
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', doc_name)
    suffix = "with_answers" if include_answers else "questions_only"
    filename = f"{safe_name}_{suffix}.txt"

    return Response(
        content="\n".join(lines),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/api/notes")
async def get_easy_notes(regenerate: bool = False):
    """Retrieve structured Easy Notes for the active document."""
    first_sec = pipeline.easy_notes.get("sections", [{}])[0] if pipeline.easy_notes else {}
    if regenerate or not pipeline.easy_notes or not pipeline.easy_notes.get("sections") or not first_sec.get("what_is"):
        pipeline.easy_notes = pipeline.easy_notes_generator.generate_all_notes(
            pipeline.chunks, pipeline.preprocessor, pipeline.document_name
        )
    return pipeline.easy_notes


@app.get("/api/download-notes-pdf")
async def download_notes_pdf():
    """Generate and download Easy Notes as a styled, publication-quality PDF."""
    from io import BytesIO
    from fastapi.responses import Response

    first_sec = pipeline.easy_notes.get("sections", [{}])[0] if pipeline.easy_notes else {}
    if not pipeline.easy_notes or not pipeline.easy_notes.get("sections") or not first_sec.get("what_is"):
        pipeline.easy_notes = pipeline.easy_notes_generator.generate_all_notes(
            pipeline.chunks, pipeline.preprocessor, pipeline.document_name
        )

    buffer = BytesIO()
    try:
        pipeline.easy_notes_generator.generate_notes_pdf(pipeline.easy_notes, buffer)
        pdf_bytes = buffer.getvalue()
        doc_name = pipeline.document_name or "VivaCraft_Notes"
        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', doc_name)
        filename = f"{safe_name}_Easy_Notes.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/api/download-notes-txt")
async def download_notes_txt():
    """Download Easy Notes as clean formatted markdown/text."""
    from fastapi.responses import Response

    first_sec = pipeline.easy_notes.get("sections", [{}])[0] if pipeline.easy_notes else {}
    if not pipeline.easy_notes or not pipeline.easy_notes.get("sections") or not first_sec.get("what_is"):
        pipeline.easy_notes = pipeline.easy_notes_generator.generate_all_notes(
            pipeline.chunks, pipeline.preprocessor, pipeline.document_name
        )

    txt_content = pipeline.easy_notes_generator.generate_notes_txt(pipeline.easy_notes)
    doc_name = pipeline.document_name or "VivaCraft_Notes"
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', doc_name)
    filename = f"{safe_name}_Easy_Notes.txt"

    return Response(
        content=txt_content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/api/team")
async def get_team_info():
    """Retrieve team member roles, module files, and algorithm justifications."""
    return {
        "team_name": "VivaCraft Team",
        "members": [
            {
                "name": "Komal",
                "role": "Reading notes and finding topics",
                "description": "Document ingestion, sentence splitting, Flesch readability, and TF-IDF / TextRank keyphrase extraction."
            },
            {
                "name": "Anushka",
                "role": "Creating questions and supported answers",
                "description": "Bloom's taxonomy viva question formulation, suggested answer synthesis, and semantic deduplication."
            },
            {
                "name": "Kristina",
                "role": "Practice feedback and revision suggestions",
                "description": "Multi-criteria rubric scoring, concept recall checking, semantic alignment, and respectful feedback."
            },
            {
                "name": "Parth",
                "role": "Interface, navigation, and downloads",
                "description": "Student-friendly study interface, 4-step workflow, dictation audio capture, and text exports."
            }
        ],
        "team_modules": TEAM_MODULE_MAP
    }


# Serve index.html directly
@app.get("/")
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

# Mount static directory for CSS/JS
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

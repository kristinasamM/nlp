# VivaCraft: Viva Voce Study Companion

VivaCraft is a local, privacy-first NLP web application designed to help engineering and computer science students prepare thoroughly for oral examinations (viva voce) on their projects, capstone reports, and coursework.

---

## Key Features

1. **Multi-Format Document Ingestion**
   - Clean, large upload interface at the top of the workspace.
   - Supports PDF, Word (`.docx`), TXT, and Markdown (`.md`) files up to 10MB.
   - Pre-loaded capstone sample documents (*Transformers & Attention*, *Raft Consensus Algorithm*) for instant testing.

2. **Section-by-Section Easy Notes**
   - **Table of Contents Navigation**: Quick sidebar to jump across document sections.
   - **Page References**: Every section card is anchored to its original page or section number.
   - **Important Points & Definitions**: Plain explanations of key terms without loss of technical meaning.
   - **How It Works**: Procedural step-by-step mechanism breakdown.
   - **Key Formulas & Equations**: Detected mathematical formulations, asymptotic complexity, and variable definitions.
   - **Comparisons & Trade-offs**: Architecture comparisons and engineering trade-offs.
   - **Viva Focus Tips**: Highlighted pointers on what examiners typically inspect in each section.
   - **PDF Export**: Download clean, publication-ready study notes as a ReportLab PDF.

3. **Authentic Viva Question Bank**
   - Questions categorized across Core Concepts, Step-by-Step Mechanisms, and Architectural Trade-offs.
   - Search by keyword or filter by section topic and difficulty level.
   - **Revealable Suggested Answers**: Expand model answers grounded in the source text.
   - **Source Grounding**: Inspect exact verbatim passages in the source document.
   - **Revision Bookmarks**: Save challenging questions to a persistent revision list stored locally in the browser.

4. **Interactive Viva Practice (Oral & Written)**
   - 1-by-1 oral examination simulation.
   - **Voice Dictation**: Dictate answers orally using the browser Web Speech API, or type freely.
   - **Structure Hints**: Expandable hints and expected discussion points before answering.
   - **Constructive Evaluation**: Highlights points covered, points to add to strengthen the answer, and the suggested reference answer.

5. **Progress & Revision Dashboard**
   - Session telemetry: questions answered, questions skipped, topics covered well, and topics to review.
   - Dedicated revision list with instant 1-click practice launch.

---

## Technical Architecture & NLP Pipeline

VivaCraft operates through an explainable 4-stage offline NLP pipeline:

1. **Document Ingestion & Preprocessing**:
   - Page-by-page text extraction (`pypdf`, `python-docx` XML parsing).
   - Ligature normalization and whitespace cleaning.
   - Abbreviation-safe sentence boundary detection.
   - Heading-aware chunking preserving exact character offsets.

2. **Topic Extraction & Keyphrase Mining**:
   - Sublinear TF-IDF scoring across document chunks.
   - TextRank graph centrality algorithm with PageRank power iteration for multi-word keyphrase extraction.
   - Definitional pattern matching for glossary synthesis.

3. **Bloom's Taxonomy Question Synthesis**:
   - Linguistic pattern generation aligned with university oral exam cognitive levels (Recall, Mechanisms, Trade-offs, Critical Defense).
   - Jaccard similarity and Bloom alignment deduplication filter to eliminate redundant prompts.

4. **Answer Evaluation & Feedback Engine**:
   - Multi-criteria academic scoring:
     - Stemmed Concept Recall (40%)
     - TF-IDF Cosine Similarity (35%)
     - Elaboration Depth (15%)
     - Discourse Reasoning Markers (10%)
   - Constructive missing-concept analysis and adaptive follow-up probing.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/kristinasamM/nlp.git
cd nlp
```

### 2. Install Dependencies
Ensure Python 3.9+ is installed. Install the requirements:
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## Running Automated Tests

To run the automated test suite covering all pipeline stages:
```bash
python -m unittest tests/test_pipeline_stages.py
```

---

## Privacy & Local Execution

VivaCraft runs entirely locally using deterministic, standard NLP algorithms. It requires no external API keys, third-party cloud subscriptions, or GPU accelerators, keeping student reports and unpublished research completely private.

# VivaCraft: Your Viva Voce Study Companion

VivaCraft is a clean, student-friendly web application designed to help engineering and computer science students prepare thoroughly for oral examinations (viva voce) on their projects, capstone reports, and coursework.

Built with an offline, transparent NLP pipeline by a 4-person student team:
- **Komal**: Document Reading, Preprocessing, and Easy Notes Generation
- **Anushka**: Topic Extraction, Viva Question Generation, and Deduplication
- **Kristina**: Answer Evaluation, Rubric Scoring, and Revision Guidance
- **Parth**: Interactive UI, Voice Dictation, Navigation, and PDF Export

---

## Key Features

1. **Prominent Study Material Upload**
   - Clean, large upload box at the top of the home screen.
   - Accepts **PDF**, Word (**`.docx`**), **TXT**, and Markdown (**`.md`**) files up to 10MB.
   - Quick-load sample capstones (*Transformers & Attention*, *Raft Consensus Algorithm*) and past session notes.

2. **Three Core Preparation Paths**
   - **1. Make Easy Notes**: Generates section-by-section study notes organized by topics and headings with exact page references, plain-English explanations, definitions, step-by-step mechanisms, formulas, and comparisons.
   - **2. Create Viva Questions**: Generates authentic oral exam questions categorized across Core Concepts, How It Works, and Trade-Offs with complete suggested answers.
   - **3. Make Both (Recommended)**: Produces the entire revision toolkit in one click.

3. **Readable "Easy Notes" Tab**
   - **Table of Contents (TOC) Sidebar**: Jump straight to any section.
   - **Page References**: Every section card is tagged with its original page/section reference.
   - **Important Definitions**: Plain explanations of key terms without changing technical meaning.
   - **How It Works**: Procedural step-by-step mechanism breakdown.
   - **Formulas & Equations**: Detected mathematical formulations and computational complexity.
   - **Comparisons & Trade-offs**: Architecture comparisons and engineering decisions.
   - **Viva Tips**: What examiners typically look for in each section.
   - **Unreadable Pages Flagged**: Scanned or unreadable pages are clearly identified.
   - **Action Buttons**: Direct links to download notes as PDF, generate questions, or start practice.

4. **"Viva Questions" Tab**
   - Search by keyword or filter by section topic and difficulty level.
   - **Revealable Suggested Answers**: Click "Show answer" to see the model answer.
   - **Source Grounding**: Click "Find it in my notes &rarr;" to inspect the exact verbatim source excerpt.
   - **Revision Bookmarks**: Click "Save for revision" to bookmark challenging questions (persisted in `localStorage`).

5. **"Practise Viva" Tab**
   - Focused 1-by-1 oral practice interface.
   - **Speech Dictation**: Dictate answers orally using browser Web Speech API or type freely.
   - **Intuition Hints**: Expandable hints and expected discussion points.
   - **Respectful Feedback**: Highlights *"Key points you covered"*, *"What to add to strengthen your answer"*, and the suggested answer without harsh failure screens.

6. **"My Progress" Tab**
   - Session stats: Questions answered, skipped, topics covered well, and topics to revise.
   - Dedicated *"Saved for Revision"* queue with instant 1-click practice launch.

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

### 2. Run the Local Development Server
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

### 3. Run Pipeline Tests
To verify all 4 team pipeline modules:
```bash
python -m unittest tests/test_pipeline_stages.py
```

---

## Team Module Architecture

| Member | Module File | NLP Role & Algorithms |
| :--- | :--- | :--- |
| **Komal** | [`modules/member1_preprocessing.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member1_preprocessing.py)<br>[`modules/member1_chunker.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member1_chunker.py)<br>[`modules/member1_easy_notes.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member1_easy_notes.py) | **Document Reading & Easy Notes**: PDF page extraction (`pypdf`), Word `.docx` XML parsing, ligature cleaning, abbreviation-safe sentence splitting, heading-aware chunking, and Easy Notes synthesis with ReportLab PDF export. |
| **Anushka** | [`modules/member2_topic_extraction.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member2_topic_extraction.py)<br>[`modules/member3_question_generator.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member3_question_generator.py)<br>[`modules/member3_duplicate_filter.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member3_duplicate_filter.py) | **Topic Mining & Question Generation**: Sublinear TF-IDF, TextRank PageRank graph model, Bloom's cognitive taxonomy question generation, and token Jaccard semantic deduplication. |
| **Kristina** | [`modules/member4_answer_evaluator.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member4_answer_evaluator.py) | **Oral Answer Evaluation**: Stemmed concept recall (40%), TF-IDF cosine similarity (35%), elaboration depth (15%), discourse balance (10%), and constructive feedback suggestions. |
| **Parth** | [`static/index.html`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/static/index.html)<br>[`static/style.css`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/static/style.css)<br>[`static/app.js`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/static/app.js)<br>[`app.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/app.py) | **Interface & Experience**: 5-tab student-friendly interface, Table of Contents sidebar, Web Speech dictation, modal citation reader, and native REST API integration. |

---

## Zero Hallucination Guarantee

VivaCraft grounds all questions, suggested answers, and easy notes directly in the text extracted from the student's uploaded document. Original excerpts and exact character offsets are preserved throughout all processing steps.

================================================================================
VIVACRAFT: VIVA VOCE STUDY COMPANION & REVISION SYSTEM
================================================================================

GitHub Repository:
https://github.com/kristinasamM/nlp.git

--------------------------------------------------------------------------------
1. PROJECT OVERVIEW
--------------------------------------------------------------------------------
VivaCraft is a local, privacy-first NLP study companion designed for engineering 
and computer science students to prepare thoroughly for oral examinations 
(viva voce) on their projects, capstone reports, and coursework.

Key Capabilities:
- Section-by-section Easy Notes organized by topics and page references.
- Authentic Bloom's Taxonomy Viva Questions with grounded answers.
- 1-by-1 Oral Practice mode with browser voice dictation.
- Constructive feedback showing covered concepts and what to add.
- High-quality downloadable ReportLab study PDF.
- 100% offline and transparent NLP (no external APIs, no cloud dependency).

--------------------------------------------------------------------------------
2. TEAM CONTRIBUTIONS & MODULE RESPONSIBILITIES
--------------------------------------------------------------------------------
- Komal:
  Document Reading, Preprocessing & Easy Notes
  Files: modules/member1_preprocessing.py, member1_chunker.py, member1_easy_notes.py
  Role: Multi-format parsing (PDF, Word docx, TXT, MD), ligature cleaning,
        abbreviation-safe sentence splitting, section chunking, and ReportLab PDF.

- Anushka:
  Topic Mining & Viva Question Generation
  Files: modules/member2_topic_extraction.py, member3_question_generator.py,
         member3_duplicate_filter.py
  Role: Sublinear TF-IDF, TextRank PageRank graph model, Bloom's Taxonomy question
        synthesis, and semantic deduplication.

- Kristina:
  Oral Answer Evaluation & Revision Guidance
  Files: modules/member4_answer_evaluator.py
  Role: Multi-criteria oral assessment (Concept Recall 40%, Cosine Similarity 35%,
        Depth 15%, Discourse Markers 10%), follow-up questions, and revision tracking.

- Parth:
  Interactive Frontend, Dictation & UX
  Files: static/index.html, static/style.css, static/app.js, app.py
  Role: 5-tab student interface, Web Speech API microphone dictation, TOC sidebar,
        modal citation reader, and FastAPI REST endpoints.

--------------------------------------------------------------------------------
3. HOW TO RUN THE PROJECT (QUICK START)
--------------------------------------------------------------------------------
Step 1: Ensure Python 3.9+ is installed on your computer.

Step 2: Clone the repository (or extract the folder):
   git clone https://github.com/kristinasamM/nlp.git
   cd nlp

Step 3: Install the required dependencies:
   pip install -r requirements.txt

Step 4: Start the application server:
   python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

Step 5: Open your web browser and navigate to:
   http://127.0.0.1:8000

--------------------------------------------------------------------------------
4. HOW TO RUN UNIT TESTS
--------------------------------------------------------------------------------
To run the automated test suite covering all 4 pipeline stages:
   python -m unittest tests/test_pipeline_stages.py

--------------------------------------------------------------------------------
5. SAMPLE DOCUMENTS INCLUDED FOR TESTING
--------------------------------------------------------------------------------
You can test the pipeline immediately using the pre-loaded capstone files:
- sample_documents/transformers_and_attention.txt
- sample_documents/distributed_systems_raft.txt
================================================================================

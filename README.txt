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
2. TECHNICAL ARCHITECTURE & NLP PIPELINE
--------------------------------------------------------------------------------
1. Document Ingestion & Preprocessing:
   - Multi-format extraction (PDF via pypdf, Word .docx XML, TXT, Markdown).
   - Ligature normalization, whitespace cleaning, and abbreviation-safe sentence splitting.
   - Heading-aware chunking preserving exact character offsets.

2. Topic Extraction & Keyphrase Mining:
   - Sublinear TF-IDF scoring across document chunks.
   - TextRank graph centrality algorithm with PageRank power iteration.
   - Definitional pattern matching for automated glossary generation.

3. Question Generation & Deduplication:
   - Authentic viva questions generated across Bloom's Taxonomy cognitive levels:
     Recall & Definitions, Step-by-Step Mechanisms, Trade-offs & Comparisons.
   - Semantic deduplication filter using Jaccard similarity and Bloom alignment.

4. Oral Answer Evaluation:
   - Composite academic rubric scoring:
     * Stemmed Concept Recall: 40%
     * TF-IDF Cosine Similarity: 35%
     * Technical Elaboration Depth: 15%
     * Discourse Reasoning Markers: 10%
   - Missing-concept breakdown and adaptive follow-up questions.

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
To run the automated test suite covering all pipeline stages:
   python -m unittest tests/test_pipeline_stages.py

--------------------------------------------------------------------------------
5. SAMPLE DOCUMENTS INCLUDED FOR TESTING
--------------------------------------------------------------------------------
You can test the pipeline immediately using the pre-loaded capstone files:
- sample_documents/transformers_and_attention.txt
- sample_documents/distributed_systems_raft.txt
================================================================================

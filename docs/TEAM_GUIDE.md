# VivaPrep: Team Member Guide & Customization Roadmap

This guide explains how each module in **VivaPrep** works in plain, simple language. It identifies which files each of the 4 team members owns, what they need to study to answer oral examination questions, and practical customization tasks they can perform to make the project distinctly their own.

---

## Team Overview & Architecture Map

| Member | Module Focus | Primary Source Files | Core Responsibility |
| :--- | :--- | :--- | :--- |
| **Member 1** | **Data Ingestion & Text Processing** | [`modules/member1_preprocessing.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member1_preprocessing.py)<br>[`modules/member1_chunker.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member1_chunker.py) | Ingests PDF/TXT, cleans text, splits sentences safely, creates heading-aware chunks with character offsets. |
| **Member 2** | **Topic Mining & Keyphrase Extraction** | [`modules/member2_topic_extraction.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member2_topic_extraction.py) | Computes TF-IDF scores, runs the TextRank graph algorithm, clusters topics, and builds the auto-glossary. |
| **Member 3** | **Viva Question Generation & Filtering** | [`modules/member3_question_generator.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member3_question_generator.py)<br>[`modules/member3_duplicate_filter.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member3_duplicate_filter.py) | Generates multi-level Bloom's taxonomy questions, anchors citations, and prunes duplicate prompts. |
| **Member 4** | **Answer Evaluation & Feedback Engine** | [`modules/member4_answer_evaluator.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member4_answer_evaluator.py) | Multi-criteria scoring (Concept Recall 40%, Cosine 35%, Depth 15%, Discourse 10%), examiner remarks & follow-ups. |

---

## Member 1: Data Ingestion & Preprocessing Lead

### How It Works in Plain Language
When a student uploads a report (PDF or TXT), raw text contains messy artifacts: Windows line breaks (`\r\n`), ligature characters (`fi`, `fl`), page numbers, and abbreviation periods (`e.g.`, `et al.`).
1. **Normalization**: Replaces typographic ligatures and cleans whitespace while preserving technical acronyms (`BERT`, `LSTM`, `VRAM`).
2. **Abbreviation Protection**: Prevents sentence splitting on periods inside academic abbreviations (`i.e.`, `et al.`, `Fig. 2`).
3. **Heading-Aware Chunking**: Scans markdown and numbered headers (`1. Introduction`, `2. Methodology`). Chunks are grouped by section rather than blindly slicing across arbitrary word counts.
4. **Source Offsets**: Saves the exact character start and end positions (`start_char`, `end_char`) so the user interface can highlight the exact passage in the original document.

### Files to Study
- [`modules/member1_preprocessing.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member1_preprocessing.py) (Lines 50–150): `clean_text()`, `split_into_sentences()`, `compute_document_stats()`
- [`modules/member1_chunker.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member1_chunker.py) (Lines 30–120): `detect_sections()`, `create_chunks()`

### Practical Customization Tasks for Member 1
1. **Add Custom Abbreviations**:
   Open `member1_preprocessing.py` and expand the `ABBREVIATIONS` set with domain terms specific to your department (e.g. `approx.`, `vs.`, `dept.`, `eq.`, `alg.`).
2. **Adjust Chunk Word Budget**:
   Open `config.py` and adjust `target_chunk_words` (e.g., from 220 to 180 words) and observe how the number of generated viva questions changes in the UI.
3. **Add OCR or Image Handling**:
   Integrate a check for scanned PDFs that alerts the student if a PDF is image-based rather than text-based.

---

## Member 2: Topic Extraction & Keyphrase Mining Lead

### How It Works in Plain Language
To generate good examination questions, the system must know what technical topics are in each chapter. Member 2 implements dual complementary NLP approaches:
1. **Statistical Frequency (TF-IDF)**: Computes Term Frequency–Inverse Document Frequency across all document chunks. Words that appear frequently within one chunk but rarely across others get high TF-IDF scores (e.g., `softmax`, `scaled`).
2. **Graph Centrality (TextRank)**: Builds an undirected co-occurrence graph where words are nodes and sliding window adjacencies form edges. Runs the PageRank algorithm until scores converge. Collapses adjacent high-scoring words into multi-word keyphrases (e.g., `scaled dot-product attention`, `positional encoding`).
3. **Auto-Glossary**: Scans the text for definitional trigger phrases (`is defined as`, `refers to`, `represents`) to produce instant revision definitions for each key term.

### Files to Study
- [`modules/member2_topic_extraction.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member2_topic_extraction.py):
  - `extract_tfidf_keywords()`: TF-IDF math and sublinear scaling.
  - `extract_textrank_keyphrases()`: PageRank power iteration loop.
  - `cluster_topics()`: Jaccard overlap topic grouping.
  - `build_glossary()`: Definitional pattern matching.

### Practical Customization Tasks for Member 2
1. **Tune the Sliding Window Size**:
   Change `textrank_window_size` in `config.py` from 4 to 3 or 5, and compare how many 2-word vs 3-word keyphrases are discovered.
2. **Experiment with Damping Factor**:
   Test damping factor `d = 0.85` vs `d = 0.90` and record the number of iterations required for PageRank convergence in your report.
3. **Add Sublinear TF Scaling**:
   Modify TF calculation to use $1 + \log(TF)$ to reduce the influence of repeated buzzwords in poorly formatted student drafts.

---

## Member 3: Question Generation & Deduplication Lead

### How It Works in Plain Language
University viva examiners do not ask simple multiple-choice questions; they test understanding across multiple cognitive levels. Member 3 grounds questions in Bloom's Taxonomy:
1. **Recall & Intuition (Bloom Level 1–2)**: Tests definitions and motivations (*"How would you explain the core intuition of {concept}?"*).
2. **Mechanisms & Flow (Bloom Level 3–4)**: Tests procedural understanding (*"Walk me through the exact step-by-step mechanism of {concept}."*).
3. **Trade-offs & Comparison (Bloom Level 5)**: Tests critical architectural judgment (*"Why did you choose {concept} over simpler alternatives?"*).
4. **Critical Viva Defense (Bloom Level 6)**: Tests edge cases and failure modes (*"What potential bottlenecks or failure modes arise with {concept}?"*).
5. **Deduplication Filter**: Compares question concepts and Bloom categories. If two questions in the same section target the same concept with the same question type, the redundant one is pruned, and the reason is logged in the telemetry audit.

### Files to Study
- [`modules/member3_question_generator.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member3_question_generator.py):
  - `generate_questions_for_chunk()`: Linguistic question patterns, expected points generator.
- [`modules/member3_duplicate_filter.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member3_duplicate_filter.py):
  - `_compute_question_similarity()`: Structured conceptual Jaccard similarity and Bloom alignment.
  - `filter_and_diversify()`: Rejection logging and retention audit.

### Practical Customization Tasks for Member 3
1. **Add Department-Specific Question Templates**:
   Add new oral defense patterns in `member3_question_generator.py` (e.g. for hardware/embedded projects: *"What is the clock cycle overhead of {concept}?"*; for web/cloud: *"How does {concept} handle network partitions?"*).
2. **Tweak the Deduplication Threshold**:
   Change `duplicate_similarity_threshold` in `config.py` from 0.65 to 0.50 and observe how many questions are filtered out in the Question Bank.
3. **Add Question Difficulty Calibrator**:
   Dynamically assign `Basic`, `Intermediate`, or `Challenging` based on the readability score of the source chunk.

---

## Member 4: Answer Evaluation & Feedback Engine Lead

### How It Works in Plain Language
When a student speaks or types an oral defense, Member 4's engine evaluates it using a 4-pillar academic rubric:
1. **Concept Recall (40% Weight)**: Verifies whether the student explicitly mentioned the essential technical terms from the verified passage. Uses the Porter Stemmer so variations like *scale* vs *scaled* or *gradient* vs *gradients* are recognized fairly.
2. **Semantic Cosine Alignment (35% Weight)**: Computes vector cosine similarity between the student's answer and the reference passage.
3. **Technical Depth & Completeness (15% Weight)**: Ensures the student provided sufficient explanation (optimal: 40–120 words) rather than a 5-word dismissal or a 400-word ramble.
4. **Discourse Reasoning Markers (10% Weight)**: Rewards causal connectives (*because*, *therefore*, *consequently*, *in contrast*, *due to*) indicating logical technical explanation.
5. **Adaptive Follow-Up Probe**: Automatically identifies which key terms the student omitted and crafts a realistic follow-up question pushing deeper into the gap.

### Files to Study
- [`modules/member4_answer_evaluator.py`](file:///c:/Users/Kristina/OneDrive/Desktop/NLP/modules/member4_answer_evaluator.py):
  - `_evaluate_concept_coverage()`: Stemmed keyword recall logic.
  - `_compute_semantic_similarity()`: Vector cosine calculation.
  - `_evaluate_discourse_precision()`: Causal connective analyzer.
  - `evaluate_response()`: Composite score, grade assignment, and adaptive follow-up generator.

### Practical Customization Tasks for Member 4
1. **Adjust Rubric Weights**:
   In `config.py`, customize the weights (e.g., increase `weight_concept_coverage` to 0.50 or `weight_discourse_precision` to 0.15) to match your university's oral defense criteria.
2. **Expand the Reasoning Markers Dictionary**:
   Add domain discourse connectives in `member4_answer_evaluator.py` (e.g. `mitigates`, `ensures`, `leads to`, `trade-off between`).
3. **Grade Threshold Customization**:
   Adjust the distinction, proficient, and satisfactory cutoffs in `config.py`.

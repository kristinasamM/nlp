"""
=============================================================================
MODULE: member3_question_generator.py
AUTHOR: Anushka (Creating Questions & Supported Answers Lead)
PURPOSE:
    Generate authentic oral examination (viva voce) questions mapped to
    student-friendly study dimensions:
    1. Core Concept (Must-Know Intuition & Motivation)
    2. How It Works (Step-by-Step Mechanism & Flow)
    3. Comparisons & Trade-Offs (Why this vs alternatives)
    4. Tough Defense (Edge Cases & Limitations)

    Each question includes:
    - Clear, natural question prompt
    - Suggested answer (concise, technically accurate response)
    - Study hints (how to structure verbal defense)
    - Key topics to mention
    - Grounding citation from the notes with section reference
=============================================================================
"""

import re
from typing import List, Dict, Any
from config import QuestionConfig


class VivaQuestionGenerator:
    """
    Anushka's Module: Question Generation & Suggested Answer Engine.
    Extracts conceptual anchors from document chunks and creates natural,
    student-friendly viva questions grounded in the notes.
    """

    def __init__(self, config: QuestionConfig = None):
        self.config = config or QuestionConfig()

    def _extract_clean_section_topic(self, section_title: str) -> str:
        """Strip markdown markers, numbers, and chapter boilerplate."""
        cleaned = re.sub(r'^[#0-9.\s]+', '', section_title).strip()
        cleaned = re.sub(r'[:\-–—]\s*$', '', cleaned).strip()
        return cleaned if cleaned else "Core System Architecture"

    def _extract_technical_terms(self, text: str, section_topic: str) -> List[str]:
        """
        Extract meaningful multi-word and acronym technical terms from chunk text.
        Excludes generic verbs, adverbs, and single non-technical words.
        """
        discourse_stops = {
            "rather", "furthermore", "however", "consequently", "given", "because",
            "moreover", "specifically", "secondly", "firstly", "additionally",
            "therefore", "despite", "whereas", "swapping", "dividing", "suppose",
            "sequential", "under", "within", "during", "across", "between",
            "dominated", "linearly", "historically", "precludes", "yields", "operates",
            "involves", "counteracts", "adopting", "relying", "consists", "relates",
            "long", "different", "multiple", "single", "distinct", "extended",
            "step", "steps", "context", "contexts", "approach", "effects", "part",
            "model", "sequence", "task", "tasks", "design", "order", "addition"
        }

        # 1. Capitalized compound phrases (e.g., 'Scaled Dot-Product', 'Multi-Head Attention')
        compounds = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        
        # 2. Hyphenated technical words (e.g., 'Dot-Product', 'Multi-Head', 'Append-Only')
        hyphenated = re.findall(r'\b[A-Za-z0-9]+-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b', text)
        
        # 3. Capitalized acronyms (e.g., 'RNNs', 'LSTM', 'RPCs', 'CFT', 'VRAM', 'GPU')
        acronyms = re.findall(r'\b[A-Z]{2,6}s?\b', text)

        # 4. Domain specific patterns
        special = []
        if re.search(r'\bsoftmax\b', text, re.I):
            special.append("Softmax Function")
        if re.search(r'\bqueries|keys|values\b', text, re.I):
            special.append("Queries, Keys, and Values (Q, K, V)")
        if re.search(r'\bsqrt\(d_k\)|\bscaling factor\b', text, re.I):
            special.append("Scaling Factor (1 / sqrt(d_k))")
        if re.search(r'\bheartbeat|election timeout\b', text, re.I):
            special.append("Randomized Election Timeouts")
        if re.search(r'\bappendentries\b', text, re.I):
            special.append("AppendEntries RPCs")
        if re.search(r'\bmajority|quorum\b', text, re.I):
            special.append("Quorum Majority")

        pool = []
        for t in compounds + hyphenated + acronyms + special:
            t_clean = t.strip()
            if (
                t_clean.lower() not in discourse_stops 
                and len(t_clean) >= 3 
                and t_clean.lower() not in [x.lower() for x in pool]
            ):
                pool.append(t_clean)

        if not pool and section_topic:
            pool.append(section_topic)

        return pool

    def generate_questions_for_chunk(
        self, chunk: Dict[str, Any], key_terms: List[str], chunk_idx: int
    ) -> List[Dict[str, Any]]:
        """
        Generate authentic, student-friendly viva questions grounded in a document chunk.
        """
        chunk_text = chunk["text"]
        section_title = chunk["section_title"]
        chunk_id = chunk["chunk_id"]
        sentences = chunk.get("sentences", [])

        section_topic = self._extract_clean_section_topic(section_title)
        technical_terms = self._extract_technical_terms(chunk_text, section_topic)
        primary_term = technical_terms[0] if technical_terms else section_topic
        secondary_term = technical_terms[1] if len(technical_terms) > 1 else section_topic

        # Find the best grounding sentence from the chunk
        supporting_sentence = sentences[0] if sentences else chunk_text[:140]
        for s in sentences:
            if any(term.lower() in s.lower() for term in [primary_term, section_topic]):
                if len(s) > 35:
                    supporting_sentence = s.strip()
                    break

        # Curate 3-4 key topics
        ui_terms = []
        for t in [primary_term, secondary_term, section_topic] + technical_terms[:2]:
            if t and t not in ui_terms and len(t) > 2:
                ui_terms.append(t)
        ui_terms = ui_terms[:4]

        questions = []
        low_title = section_topic.lower()

        # ===================================================================
        # Question 1: Core Concept (Must-Know) - Bloom: Recall & Definition
        # ===================================================================
        if "introduction" in low_title or "motivation" in low_title:
            q1_prompt = (
                f"What was the main motivation for adopting {primary_term} in your project, "
                f"and what limitations of traditional approaches did it solve?"
            )
        elif "formulation" in low_title or "attention" in low_title or "algorithm" in low_title:
            q1_prompt = (
                f"How would you explain the core idea of {section_topic} in plain English? "
                f"What specific role does {primary_term} play?"
            )
        elif "consensus" in low_title or "election" in low_title:
            q1_prompt = (
                f"What fundamental challenge does {section_topic} solve, "
                f"and why was this approach chosen over traditional alternatives?"
            )
        else:
            q1_prompt = (
                f"Can you explain the main idea behind {section_topic} in plain English? "
                f"Why is {primary_term} necessary in your architecture?"
            )

        q1_ans = (
            f"{section_topic} solves the primary architectural challenge in this part of the system. "
            f"As stated in our notes: \"{supporting_sentence}\". "
            f"Rather than relying on older sequential models that cause processing bottlenecks, "
            f"{primary_term} provides direct connections and predictable scaling. When explaining this, "
            f"focus on why traditional methods were inadequate and how this design resolves that limitation."
        )

        questions.append({
            "bloom_level": "Recall & Definition",
            "category_label": "Core Concept",
            "difficulty": "Easy",
            "question_text": q1_prompt,
            "target_concept": primary_term,
            "section_title": section_topic,
            "source_chunk_id": chunk_id,
            "source_citation": supporting_sentence,
            "suggested_answer": q1_ans,
            "model_answer": q1_ans,
            "key_terms": ui_terms,
            "expected_points": [
                f"Explain the core purpose of {primary_term} clearly",
                f"Connect it to the main problem addressed in {section_topic}",
                "State why simpler baseline approaches fall short"
            ],
            "study_tips": {
                "intuition": f"Start with a 30-second summary: What does {primary_term} do, and what problem does it eliminate?",
                "technical_focus": "Mention the primary inputs, dimensions, or states involved.",
                "examiner_trap": "Don't just repeat definitions—explain the 'why' behind using it in your project."
            }
        })

        # ===================================================================
        # Question 2: How It Works - Bloom: Mechanisms & Flow
        # ===================================================================
        if "attention" in low_title or "formulation" in low_title:
            q2_prompt = (
                f"Walk me through the step-by-step mechanism of {section_topic}. "
                f"How do the input vectors transform through {primary_term}?"
            )
        elif "election" in low_title or "replication" in low_title:
            q2_prompt = (
                f"Walk me through the step-by-step sequence of events during {section_topic}. "
                f"How do nodes transition states when {primary_term} is triggered?"
            )
        else:
            q2_prompt = (
                f"If you had to sketch {section_topic} on a whiteboard, "
                f"what are the key components and how does information flow through {primary_term}?"
            )

        q2_ans = (
            f"The mechanism of {section_topic} operates in distinct stages: "
            f"First, inputs are mapped into intermediate representations. "
            f"Second, {primary_term} processes these representations to establish core relationships, "
            f"as grounded in our notes: \"{supporting_sentence}\". "
            f"Finally, the aggregated results are normalized and passed forward to the next stage."
        )

        questions.append({
            "bloom_level": "Mechanisms & Flow",
            "category_label": "How It Works",
            "difficulty": "Medium",
            "question_text": q2_prompt,
            "target_concept": f"{primary_term} & {secondary_term}",
            "section_title": section_topic,
            "source_chunk_id": chunk_id,
            "source_citation": supporting_sentence,
            "suggested_answer": q2_ans,
            "model_answer": q2_ans,
            "key_terms": ui_terms,
            "expected_points": [
                "Describe the step-by-step processing pipeline",
                f"Explain how information flows between {primary_term} and {secondary_term}",
                "Mention intermediate representations or state transitions"
            ],
            "study_tips": {
                "intuition": "Describe it like a visual flowchart: Step 1 (Input) -> Step 2 (Core Logic) -> Step 3 (Output).",
                "technical_focus": "Be specific about formulas, dimensions, or message exchanges.",
                "examiner_trap": "Examiners often ask what happens right between step 1 and step 2—know that transition."
            }
        })

        # ===================================================================
        # Question 3: Trade-Offs & Defense - Bloom: Trade-offs & Comparison
        # ===================================================================
        if "complexity" in low_title or "limitations" in low_title or "safety" in low_title:
            q3_prompt = (
                f"What is the primary computational bottleneck or failure mode in {section_topic}, "
                f"and how would you defend your project against scalability critiques?"
            )
        elif "scaling" in low_title or "factor" in low_title or "timeout" in low_title:
            q3_prompt = (
                f"Why is {primary_term} a critical numerical or timing design choice? "
                f"What would happen to system stability if this parameter were omitted?"
            )
        else:
            q3_prompt = (
                f"Why did you choose {primary_term} instead of a simpler alternative? "
                f"What computational, memory, or architectural trade-offs did you consider?"
            )

        q3_ans = (
            f"When evaluating {primary_term}, the main trade-off is between computational cost and stability. "
            f"As noted in our project text: \"{supporting_sentence}\". "
            f"Without this mechanism, the system would risk gradient saturation or synchronization conflicts. "
            f"While there is a modest computational overhead, it guarantees stable training and reliable operation."
        )

        questions.append({
            "bloom_level": "Trade-offs & Comparison",
            "category_label": "Trade-offs & Defense",
            "difficulty": "Challenging",
            "question_text": q3_prompt,
            "target_concept": primary_term,
            "section_title": section_topic,
            "source_chunk_id": chunk_id,
            "source_citation": supporting_sentence,
            "suggested_answer": q3_ans,
            "model_answer": q3_ans,
            "key_terms": ui_terms,
            "expected_points": [
                f"Identify computational complexity or memory trade-offs of {primary_term}",
                "Justify why benefits outweigh the added implementation complexity",
                "Explain the exact failure mode or instability prevented by this design"
            ],
            "study_tips": {
                "intuition": "Don't claim the design is flawless. Strong candidates acknowledge trade-offs and explain why they accepted them.",
                "technical_focus": "Cite complexity classes (e.g. O(n^2), O(log n)) or specific failure bounds.",
                "examiner_trap": "If asked 'Could you do this without X?', answer with the exact technical consequence."
            }
        })

        return questions[:self.config.max_questions_per_chunk]

    def generate_all_questions(
        self, chunks: List[Dict[str, Any]], key_terms: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Orchestrate question generation across all document chunks and assign IDs.
        """
        all_questions = []
        q_id = 1

        for idx, chunk in enumerate(chunks):
            chunk_qs = self.generate_questions_for_chunk(chunk, key_terms, idx)
            for q in chunk_qs:
                q["question_id"] = f"VIVA-{q_id:03d}"
                all_questions.append(q)
                q_id += 1

        return all_questions

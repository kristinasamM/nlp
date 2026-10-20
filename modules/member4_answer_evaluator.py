"""
=============================================================================
MODULE: member4_answer_evaluator.py
AUTHOR: Kristina (Practice Feedback & Revision Suggestions Lead)
PURPOSE:
    Multi-criteria assessment of student viva responses against notes.
    Evaluates concept coverage, semantic alignment, technical depth,
    and discourse reasoning markers. Provides actionable, respectful feedback:
    - "You covered the main idea."
    - "Good start — add how this works."
    - "Review this topic and try again."
    Shows what you covered, what to add, and a short suggested answer.
=============================================================================
"""

import math
import re
from typing import List, Dict, Any, Tuple
from config import EvaluationConfig


class VivaAnswerEvaluator:
    """
    Kristina's Module: Practice Feedback & Answer Assessment Engine.
    Provides transparent, helpful feedback for oral and typed viva responses.
    """

    def __init__(self, config: EvaluationConfig = None):
        self.config = config or EvaluationConfig()

        # Discourse markers that indicate reasoned explanation rather than rote buzzwords
        self.reasoning_markers = {
            "because", "therefore", "thus", "consequently", "in contrast",
            "specifically", "whereas", "as a result", "due to", "furthermore",
            "in order to", "mitigates", "ensures", "leads to", "since"
        }

    # -----------------------------------------------------------------------
    # 1. RUBRIC METRICS CALCULATION
    # -----------------------------------------------------------------------
    def _evaluate_concept_coverage(
        self, student_answer: str, reference_text: str, preprocessor
    ) -> Tuple[float, List[str], List[str]]:
        """
        Metric 1: Concept & Keyword Recall (Weight: 40%).
        Checks for presence of key concepts using stemming to handle natural variations.
        """
        ref_tokens = preprocessor.tokenize(reference_text, lower=True, remove_stopwords=True, stem=False)
        student_stems = set(preprocessor.tokenize(student_answer, lower=True, remove_stopwords=True, stem=True))
        student_raw = student_answer.lower()

        # Count frequencies of reference content words (length >= 3)
        freq = {}
        for t in ref_tokens:
            if len(t) >= 3:
                freq[t] = freq.get(t, 0) + 1

        sorted_concepts = sorted(freq.items(), key=lambda x: (x[1], len(x[0])), reverse=True)
        target_concepts = []
        seen_stems = set()
        for t, _ in sorted_concepts:
            st = preprocessor.stem_token(t)
            if st not in seen_stems:
                target_concepts.append(t)
                seen_stems.add(st)
            if len(target_concepts) >= 10:
                break

        if not target_concepts:
            return 1.0, [], []

        covered = []
        missing = []
        for c in target_concepts:
            c_stem = preprocessor.stem_token(c)
            if c_stem in student_stems or c in student_raw:
                covered.append(c)
            else:
                missing.append(c)

        coverage_ratio = len(covered) / len(target_concepts)
        return coverage_ratio, covered, missing

    def _compute_semantic_similarity(
        self, student_answer: str, reference_text: str, preprocessor
    ) -> float:
        """
        Metric 2: Semantic Alignment via Cosine Similarity (Weight: 35%).
        """
        tokens_s = preprocessor.tokenize(student_answer, lower=True, remove_stopwords=True, stem=True)
        tokens_r = preprocessor.tokenize(reference_text, lower=True, remove_stopwords=True, stem=True)

        if not tokens_s or not tokens_r:
            return 0.0

        vocab = sorted(list(set(tokens_s + tokens_r)))
        vec_s = [tokens_s.count(w) for w in vocab]
        vec_r = [tokens_r.count(w) for w in vocab]

        dot = sum(s * r for s, r in zip(vec_s, vec_r))
        norm_s = math.sqrt(sum(s * s for s in vec_s))
        norm_r = math.sqrt(sum(r * r for r in vec_r))

        if norm_s == 0.0 or norm_r == 0.0:
            return 0.0

        return dot / (norm_s * norm_r)

    def _evaluate_depth_and_length(self, student_answer: str) -> float:
        """
        Metric 3: Technical Depth & Completeness (Weight: 15%).
        """
        words = len(student_answer.split())
        if words < 10:
            return 0.30
        elif words < 25:
            return 0.70
        elif words <= 160:
            return 1.00
        else:
            return 0.85

    def _evaluate_discourse_precision(self, student_answer: str) -> float:
        """
        Metric 4: Reasoning Markers (Weight: 10%).
        """
        lower = student_answer.lower()
        found_markers = [m for m in self.reasoning_markers if m in lower]

        if len(found_markers) >= 2:
            return 1.0
        elif len(found_markers) >= 1:
            return 0.75
        else:
            return 0.50

    # -----------------------------------------------------------------------
    # 2. STUDENT-FRIENDLY EVALUATION & ACTIONABLE FEEDBACK
    # -----------------------------------------------------------------------
    def evaluate_response(
        self,
        question: Dict[str, Any],
        student_answer: str,
        reference_chunk: Dict[str, Any],
        preprocessor
    ) -> Dict[str, Any]:
        """
        Assess student response and synthesize clear, actionable feedback.
        """
        cleaned_answer = student_answer.strip()
        ref_text = reference_chunk.get("text", "")
        citation = question.get("source_citation", ref_text[:200])
        section_title = question.get("section_title", reference_chunk.get("section_title", "Your Notes"))
        suggested_ans = question.get("suggested_answer") or question.get("model_answer", citation)

        if not cleaned_answer:
            return {
                "final_score": 0,
                "grade": "Needs Revision",
                "verdict_message": "Type your answer in your own words to see feedback.",
                "covered_concepts": [],
                "missing_concepts": [],
                "key_points_covered": [],
                "what_to_add": ["Key concepts from this section"],
                "suggested_answer": suggested_ans,
                "examiner_remarks": "No answer provided yet.",
                "followup_question": "Can you define the core term in your own words?",
                "source_citation": citation,
                "section_title": section_title,
                "uncertainty_note": "Feedback is a study aid and may sometimes miss a correct answer."
            }

        # Pillar 1: Concept Recall
        cov_score, covered, missing = self._evaluate_concept_coverage(
            cleaned_answer, ref_text, preprocessor
        )

        # Pillar 2: Semantic Alignment
        sem_score = self._compute_semantic_similarity(cleaned_answer, ref_text, preprocessor)

        # Pillar 3: Depth & Completeness
        depth_score = self._evaluate_depth_and_length(cleaned_answer)

        # Pillar 4: Discourse Precision
        discourse_score = self._evaluate_discourse_precision(cleaned_answer)

        # Weighted calculation
        cfg = self.config
        composite = (
            (cov_score * cfg.weight_concept_coverage) +
            (sem_score * cfg.weight_semantic_similarity) +
            (depth_score * cfg.weight_depth_completeness) +
            (discourse_score * cfg.weight_discourse_precision)
        ) * 100.0

        final_score = int(round(min(100.0, max(0.0, composite))))

        # Determine academic grade
        if final_score >= cfg.grade_thresholds["Distinction"]:
            grade = "Distinction"
        elif final_score >= cfg.grade_thresholds["Proficient"]:
            grade = "Proficient"
        elif final_score >= cfg.grade_thresholds["Satisfactory"]:
            grade = "Satisfactory"
        else:
            grade = "Needs Revision"

        # Determine user-friendly, respectful feedback headline
        word_count = len(cleaned_answer.split())
        if final_score >= 75 or (cov_score >= 0.55 and sem_score >= 0.4):
            verdict_message = "You covered the main idea."
        elif final_score >= 50 or cov_score >= 0.35:
            verdict_message = "Good start — add how this works."
        else:
            verdict_message = "Review this topic and try again."

        # Uncertainty handling: If student wrote a substantive response but statistical similarity is low
        uncertainty_note = "Feedback is a study aid and may sometimes miss a correct answer."
        if word_count >= 20 and final_score < 45 and sem_score < 0.2:
            uncertainty_note = "We may not have assessed this answer fully. Compare it with the suggested answer."

        # Remarks
        remarks = []
        if covered:
            remarks.append(f"Well explained: {', '.join(covered[:3])}.")
        if missing:
            remarks.append(f"Consider mentioning: {', '.join(missing[:3])}.")
        examiner_feedback = " ".join(remarks) if remarks else verdict_message

        # Follow-up probe
        target_concept = question.get("target_concept", section_title)
        if missing:
            followup = f"How does {missing[0]} relate to {target_concept} in your notes?"
        else:
            followup = f"How would you explain the trade-offs of {target_concept} if an examiner asks for practical limitations?"

        return {
            "final_score": final_score,
            "grade": grade,
            "verdict_message": verdict_message,
            "metric_breakdown": {
                "concept_coverage_score": round(cov_score * 100, 1),
                "semantic_similarity_score": round(sem_score * 100, 1),
                "depth_completeness_score": round(depth_score * 100, 1),
                "discourse_reasoning_score": round(discourse_score * 100, 1)
            },
            "covered_concepts": covered,
            "missing_concepts": missing,
            "key_points_covered": covered,
            "what_to_add": missing[:4] if missing else ["Review details in the suggested answer"],
            "suggested_answer": suggested_ans,
            "examiner_remarks": examiner_feedback,
            "followup_question": followup,
            "source_citation": citation,
            "section_title": section_title,
            "source_chunk_id": question.get("source_chunk_id", ""),
            "uncertainty_note": uncertainty_note
        }

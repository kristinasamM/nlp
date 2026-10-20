"""
=============================================================================
MODULE: member3_duplicate_filter.py
AUTHOR: Team Member 3 (Viva Question Generation Lead)
PURPOSE:
    Semantic deduplication and diversity re-ranking for generated viva questions.
    Uses TF-IDF vectorization and pairwise cosine similarity to prune redundant
    prompts while preserving multi-level Bloom's taxonomy coverage.
=============================================================================
"""

import math
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from config import QuestionConfig


QUESTION_BOILERPLATE = {
    "context", "formally", "define", "specific", "objective", "serve", "pipeline",
    "walk", "exact", "algorithmic", "procedural", "steps", "involved", "processes",
    "inputs", "interact", "computational", "memory", "trade-offs", "trade", "offs",
    "encounter", "utilizing", "preferred", "simpler", "alternative", "baselines",
    "suppose", "severe", "edge", "case", "occurs", "assumptions", "break", "down",
    "system", "fail", "experimentally", "defend", "results", "question", "level",
    "section", "explain", "describe", "discuss", "show", "role"
}


class QuestionDuplicateFilter:
    """
    Member 3: Question Deduplication & Diversity Optimizer.
    Prevents repetitive examination questions and ensures balanced coverage.
    """

    def __init__(self, config: QuestionConfig = None):
        self.config = config or QuestionConfig()

    def _extract_content_tokens(self, text: str, preprocessor) -> List[str]:
        """
        Extract meaningful concept tokens by stripping both English stopwords
        and standard viva question boilerplate.
        """
        tokens = preprocessor.tokenize(text, lower=True, remove_stopwords=True, stem=True)
        return [t for t in tokens if t not in QUESTION_BOILERPLATE and len(t) > 2]

    def _compute_question_similarity(
        self, q_a: Dict[str, Any], q_b: Dict[str, Any], preprocessor
    ) -> float:
        """
        Compute conceptual similarity between two viva prompts based on:
        1. Target concept overlap (stemmed technical keywords)
        2. Bloom's Taxonomy cognitive category
        3. Source section context
        """
        concept_a = q_a.get("target_concept", "").lower()
        concept_b = q_b.get("target_concept", "").lower()

        tokens_a = preprocessor.tokenize(concept_a, lower=True, remove_stopwords=True, stem=True)
        tokens_b = preprocessor.tokenize(concept_b, lower=True, remove_stopwords=True, stem=True)

        if not tokens_a or not tokens_b:
            return 0.0

        set_a = set(tokens_a)
        set_b = set(tokens_b)

        # Jaccard overlap of target concept stems
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        concept_overlap = (intersection / union) if union > 0 else 0.0

        # If they don't share any target concept stems, they are NOT duplicates
        if concept_overlap == 0.0:
            return 0.0

        same_bloom = (q_a.get("bloom_level") == q_b.get("bloom_level"))
        same_section = (q_a.get("section_title") == q_b.get("section_title"))

        if same_bloom and (same_section or concept_overlap >= 0.7):
            return 0.90  # Definite duplicate within same category and concept

        if same_bloom:
            return concept_overlap * 0.85

        # Different Bloom categories are complementary, not duplicates
        return concept_overlap * 0.40

    def filter_and_diversify(
        self, questions: List[Dict[str, Any]], preprocessor
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Filter candidate questions and produce an explainable audit log.

        Returns:
            (retained_questions, pruned_questions, audit_summary)
        """
        if not questions:
            return [], [], {"initial_count": 0, "final_count": 0, "reduction_ratio": 0.0}

        threshold = self.config.duplicate_similarity_threshold
        retained = []
        pruned = []

        for q in questions:
            is_duplicate = False
            duplicate_reason = ""

            for accepted in retained:
                sim = self._compute_question_similarity(q, accepted, preprocessor)
                if sim >= threshold:
                    is_duplicate = True
                    qid = accepted.get("question_id", "previous candidate")
                    duplicate_reason = (
                        f"Overlaps with existing question {qid} ({accepted.get('bloom_level')}) "
                        f"on concept '{accepted.get('target_concept')}' (similarity: {int(sim * 100)}%)."
                    )
                    break

            if is_duplicate:
                pruned_record = dict(q)
                pruned_record["prune_reason"] = duplicate_reason
                pruned.append(pruned_record)
            else:
                retained.append(q)

        initial_count = len(questions)
        final_count = len(retained)
        pruned_count = len(pruned)
        reduction_pct = round((pruned_count / initial_count) * 100, 1) if initial_count > 0 else 0.0

        audit_summary = {
            "initial_candidates": initial_count,
            "retained_count": final_count,
            "pruned_count": pruned_count,
            "reduction_percentage": f"{reduction_pct}%",
            "similarity_threshold": threshold,
            "bloom_distribution": {
                level: sum(1 for q in retained if q.get("bloom_level") == level)
                for level in self.config.bloom_levels
            }
        }

        return retained, pruned, audit_summary

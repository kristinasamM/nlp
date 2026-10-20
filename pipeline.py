"""
=============================================================================
PIPELINE ORCHESTRATOR: pipeline.py
PURPOSE:
    Unifies the 4 team member modules into an end-to-end, inspectable NLP
    pipeline for viva preparation and document evaluation.
=============================================================================
"""

import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from config import (
    PreprocessingConfig,
    ChunkingConfig,
    TopicConfig,
    QuestionConfig,
    EvaluationConfig
)
from modules.member1_preprocessing import DocumentPreprocessor
from modules.member1_chunker import DocumentChunker
from modules.member1_easy_notes import EasyNotesGenerator
from modules.member2_topic_extraction import TopicExtractor
from modules.member3_question_generator import VivaQuestionGenerator
from modules.member3_duplicate_filter import QuestionDuplicateFilter
from modules.member4_answer_evaluator import VivaAnswerEvaluator


class VivaPipeline:
    """
    Unified Pipeline Manager.
    Exposes clean inspection hooks into every NLP stage.
    """

    def __init__(self):
        # Initialize modules for all 4 team members
        self.preprocessor = DocumentPreprocessor(PreprocessingConfig())
        self.chunker = DocumentChunker(ChunkingConfig())
        self.easy_notes_generator = EasyNotesGenerator()
        self.topic_extractor = TopicExtractor(TopicConfig())
        self.question_generator = VivaQuestionGenerator(QuestionConfig())
        self.duplicate_filter = QuestionDuplicateFilter(QuestionConfig())
        self.answer_evaluator = VivaAnswerEvaluator(EvaluationConfig())

        # Document State Store
        self.current_document_text: str = ""
        self.document_name: str = "Untitled Document"
        self.sentences: List[str] = []
        self.stats: Dict[str, Any] = {}
        self.chunks: List[Dict[str, Any]] = []
        self.easy_notes: Dict[str, Any] = {}
        self.tfidf_keywords: List[Dict[str, Any]] = []
        self.textrank_keyphrases: List[Dict[str, Any]] = []
        self.topic_clusters: List[Dict[str, Any]] = []
        self.glossary: List[Dict[str, str]] = []
        self.questions: List[Dict[str, Any]] = []
        self.pruned_questions: List[Dict[str, Any]] = []
        self.filter_audit: Dict[str, Any] = {}
        self.last_pipeline_runtime_ms: float = 0.0

    def process_text(self, raw_text: str, document_name: str = "Technical Document") -> Dict[str, Any]:
        """
        Execute full end-to-end NLP workflow.
        Returns a comprehensive state object containing all intermediate results.
        """
        start_time = time.perf_counter()
        self.document_name = document_name

        # --- Stage 1 & 2: Preprocessing & Chunking (Member 1) ---
        cleaned_text = self.preprocessor.clean_text(raw_text)
        self.current_document_text = cleaned_text
        self.sentences = self.preprocessor.split_into_sentences(cleaned_text)
        self.stats = self.preprocessor.compute_document_stats(cleaned_text, self.sentences)
        self.chunks = self.chunker.create_chunks(cleaned_text, self.preprocessor)

        # --- Stage 3: Topic & Keyphrase Extraction (Member 2) ---
        self.tfidf_keywords = self.topic_extractor.extract_tfidf_keywords(self.chunks, self.preprocessor)
        self.textrank_keyphrases = self.topic_extractor.extract_textrank_keyphrases(cleaned_text, self.preprocessor)

        # Merge unique top terms from both methods (prioritizing descriptive multi-word TextRank phrases)
        combined_terms = []
        seen = set()
        for item in self.textrank_keyphrases:
            phrase = item["keyphrase"]
            if phrase not in seen and len(phrase) >= 3:
                combined_terms.append(phrase)
                seen.add(phrase)
        for item in self.tfidf_keywords:
            term = item["term"]
            if term not in seen and len(term) >= 3:
                combined_terms.append(term)
                seen.add(term)

        self.topic_clusters = self.topic_extractor.cluster_topics(self.chunks, combined_terms[:20])
        self.glossary = self.topic_extractor.build_glossary(cleaned_text, combined_terms[:12], self.preprocessor)

        # --- Stage 4: Easy Notes Generation (Member 1 - Komal) ---
        self.easy_notes = self.easy_notes_generator.generate_all_notes(
            self.chunks, self.preprocessor, self.document_name
        )

        # --- Stage 5 & 6: Viva Question Generation & Deduplication (Member 3 - Anushka) ---
        raw_questions = self.question_generator.generate_all_questions(self.chunks, combined_terms[:25])
        self.questions, self.pruned_questions, self.filter_audit = self.duplicate_filter.filter_and_diversify(
            raw_questions, self.preprocessor
        )

        end_time = time.perf_counter()
        self.last_pipeline_runtime_ms = round((end_time - start_time) * 1000, 2)

        return self.get_summary()

    def evaluate_answer(self, question_id: str, student_answer: str) -> Dict[str, Any]:
        """
        Member 4: Evaluate student oral response for a specific viva question.
        """
        # Find question
        matched_q = next((q for q in self.questions if q["question_id"] == question_id), None)
        if not matched_q:
            return {"error": f"Question ID '{question_id}' not found."}

        # Find reference chunk
        chunk_id = matched_q.get("source_chunk_id")
        matched_chunk = next((c for c in self.chunks if c["chunk_id"] == chunk_id), None)
        if not matched_chunk:
            # Fallback to entire text or first chunk
            matched_chunk = self.chunks[0] if self.chunks else {"text": self.current_document_text}

        return self.answer_evaluator.evaluate_response(
            question=matched_q,
            student_answer=student_answer,
            reference_chunk=matched_chunk,
            preprocessor=self.preprocessor
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Return structured state for API responses and UI dashboards.
        """
        return {
            "document_name": self.document_name,
            "runtime_ms": self.last_pipeline_runtime_ms,
            "stats": self.stats,
            "chunk_count": len(self.chunks),
            "chunks": self.chunks,
            "easy_notes": self.easy_notes,
            "tfidf_keywords": self.tfidf_keywords,
            "textrank_keyphrases": self.textrank_keyphrases,
            "topic_clusters": self.topic_clusters,
            "glossary": self.glossary,
            "question_count": len(self.questions),
            "questions": self.questions,
            "pruned_questions_count": len(self.pruned_questions),
            "pruned_questions": self.pruned_questions,
            "filter_audit": self.filter_audit,
            "document_text": self.current_document_text
        }

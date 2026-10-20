"""
=============================================================================
TEST SUITE: test_pipeline_stages.py
PURPOSE:
    Unit and integration tests validating each team member's NLP stage:
    - Member 1: Preprocessing & Chunking
    - Member 2: Topic Extraction & Keyphrase Mining
    - Member 3: Question Generation & Deduplication
    - Member 4: Answer Evaluation & Examiner Feedback
=============================================================================
"""

import unittest
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
from modules.member2_topic_extraction import TopicExtractor
from modules.member3_question_generator import VivaQuestionGenerator
from modules.member3_duplicate_filter import QuestionDuplicateFilter
from modules.member4_answer_evaluator import VivaAnswerEvaluator
from pipeline import VivaPipeline


class TestMember1PreprocessingAndChunking(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DocumentPreprocessor(PreprocessingConfig())
        self.chunker = DocumentChunker(ChunkingConfig())

    def test_clean_text_removes_ligatures_and_whitespace(self):
        raw = "This is a \ufb01le with   excessive  spaces and\r\nnewlines.\n\n\n\nNew section."
        cleaned = self.preprocessor.clean_text(raw)
        self.assertIn("file", cleaned)
        self.assertNotIn("\r", cleaned)
        self.assertNotIn("\n\n\n", cleaned)

    def test_sentence_splitting_preserves_abbreviations(self):
        sample = "The model (e.g. BERT) achieves 98.5% accuracy. It was introduced by Devlin et al. in 2018."
        sentences = self.preprocessor.split_into_sentences(sample)
        # Should NOT split on e.g. or et al.
        self.assertEqual(len(sentences), 2)
        self.assertIn("e.g. BERT", sentences[0])
        self.assertIn("Devlin et al.", sentences[1])

    def test_compute_document_stats(self):
        sample = "Artificial Intelligence represents a broad field of computational logic. It drives modern innovations."
        cleaned = self.preprocessor.clean_text(sample)
        sents = self.preprocessor.split_into_sentences(cleaned)
        stats = self.preprocessor.compute_document_stats(cleaned, sents)
        self.assertGreater(stats["total_words"], 10)
        self.assertGreater(stats["type_token_ratio"], 0.5)
        self.assertIn("flesch_reading_ease", stats)

    def test_chunking_respects_sections(self):
        doc = (
            "# Section 1: Foundations\n\n"
            "Natural language processing bridges computers and human communication. "
            "It incorporates syntactic and semantic analysis across multiple layers.\n\n"
            "## Section 2: Embeddings\n\n"
            "Vector embeddings map tokens into dense continuous vector spaces. "
            "Cosine similarity quantifies semantic proximity between term vectors."
        )
        cleaned = self.preprocessor.clean_text(doc)
        chunks = self.chunker.create_chunks(cleaned, self.preprocessor)
        self.assertGreaterEqual(len(chunks), 2)
        titles = [c["section_title"] for c in chunks]
        self.assertTrue(any("Foundations" in t for t in titles))
        self.assertTrue(any("Embeddings" in t for t in titles))


class TestMember2TopicExtraction(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DocumentPreprocessor(PreprocessingConfig())
        self.chunker = DocumentChunker(ChunkingConfig())
        self.extractor = TopicExtractor(TopicConfig())

    def test_tfidf_and_textrank_extraction(self):
        doc = (
            "Scaled dot-product attention computes query key interactions. "
            "The query and key matrices determine weights for value vectors. "
            "Self-attention allows parallel training across all tokens without recurrent delays. "
            "Multi-head attention projects vectors into multiple subspaces."
        )
        cleaned = self.preprocessor.clean_text(doc)
        chunks = self.chunker.create_chunks(cleaned, self.preprocessor)
        tfidf_res = self.extractor.extract_tfidf_keywords(chunks, self.preprocessor, top_n=5)
        textrank_res = self.extractor.extract_textrank_keyphrases(cleaned, self.preprocessor, top_k=5)

        self.assertTrue(len(tfidf_res) > 0)
        self.assertTrue(len(textrank_res) > 0)
        extracted_terms = [t["term"] for t in tfidf_res] + [t["keyphrase"] for t in textrank_res]
        # Should capture 'attention', 'query', 'vectors', or 'attention'
        self.assertTrue(any("attention" in t.lower() for t in extracted_terms))


class TestMember3QuestionGeneratorAndFilter(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DocumentPreprocessor(PreprocessingConfig())
        self.generator = VivaQuestionGenerator(QuestionConfig())
        self.filter = QuestionDuplicateFilter(QuestionConfig())

    def test_question_generation_and_deduplication(self):
        sample_chunk = {
            "chunk_id": "CHK-001",
            "section_title": "Attention Mechanism",
            "text": "Self-attention computes alignment weights across all token pairs.",
            "sentences": ["Self-attention computes alignment weights across all token pairs."]
        }
        raw_qs = self.generator.generate_questions_for_chunk(sample_chunk, ["self-attention", "weights"], 0)
        self.assertTrue(len(raw_qs) >= 2)

        # Ensure bloom levels are assigned
        levels = [q["bloom_level"] for q in raw_qs]
        self.assertIn("Recall & Definition", levels)

        # Test duplicate filter on intentional duplicate
        dup_chunk_qs = list(raw_qs) + [dict(raw_qs[0])]
        dup_chunk_qs[-1]["question_id"] = "VIVA-DUP"
        retained, pruned, audit = self.filter.filter_and_diversify(dup_chunk_qs, self.preprocessor)
        self.assertEqual(len(pruned), 1)
        self.assertEqual(len(retained), len(raw_qs))


class TestMember4AnswerEvaluator(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DocumentPreprocessor(PreprocessingConfig())
        self.evaluator = VivaAnswerEvaluator(EvaluationConfig())

    def test_answer_scoring_rubric(self):
        ref_chunk = {
            "text": (
                "Scaled dot-product attention divides dot products by the square root of d_k "
                "to prevent vanishing gradients when the softmax saturates under high dimensionality."
            )
        }
        question = {
            "question_id": "VIVA-001",
            "target_concept": "Scaling Factor",
            "source_citation": ref_chunk["text"]
        }

        # Strong answer covering concepts and discourse reasoning
        good_answer = (
            "We scale the dot products by sqrt(d_k) because when dimensionality d_k is large, "
            "the magnitude of dot products grows excessively. Consequently, this pushes the softmax "
            "into regions with extremely small gradients, causing vanishing gradients."
        )

        res = self.evaluator.evaluate_response(question, good_answer, ref_chunk, self.preprocessor)
        self.assertGreaterEqual(res["final_score"], 65)
        self.assertIn("covered_concepts", res)
        self.assertTrue(len(res["covered_concepts"]) > 0)
        self.assertIn("followup_question", res)


class TestFullPipelineIntegration(unittest.TestCase):
    def test_pipeline_end_to_end(self):
        pipeline = VivaPipeline()
        sample_doc_path = Path("sample_documents/transformers_and_attention.txt")
        text = sample_doc_path.read_text(encoding="utf-8")
        summary = pipeline.process_text(text, document_name="Transformers Capstone")

        self.assertGreater(summary["chunk_count"], 0)
        self.assertGreater(summary["question_count"], 0)
        self.assertGreater(len(summary["tfidf_keywords"]), 0)
        self.assertGreater(len(summary["textrank_keyphrases"]), 0)

        # Evaluate one question
        q0 = summary["questions"][0]
        eval_res = pipeline.evaluate_answer(
            q0["question_id"],
            "Self-attention relates all positions in a sequence simultaneously using queries, keys, and values."
        )
        self.assertIn("final_score", eval_res)
        self.assertIn("examiner_remarks", eval_res)


if __name__ == "__main__":
    unittest.main()

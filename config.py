"""
=============================================================================
VivaPrep: NLP-Powered Viva Voce Preparation & Assessment System
Configuration & Hyperparameter Defaults
=============================================================================
This file centralizes all pipeline settings, NLP hyperparameters, and team
module ownership metadata so any team member can easily tune, inspect, and
explain thresholds during viva evaluation.
"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class PreprocessingConfig:
    """Member 1 Ownership: Ingestion, Normalization & Cleaning Parameters"""
    min_sentence_length: int = 15          # Discard stray fragments shorter than 15 chars
    max_sentence_length: int = 600         # Flag unusually long run-on sentences
    preserve_case_for_acronyms: bool = True # Keep 'BERT', 'NLP', 'API' uppercase
    strip_header_footer_numbers: bool = True
    flesch_reading_target: float = 45.0    # Baseline academic readability score

@dataclass
class ChunkingConfig:
    """Member 1 Ownership: Structural & Semantic Chunking Parameters"""
    target_chunk_words: int = 220          # Sweet-spot context window for focused viva questions
    chunk_overlap_words: int = 35          # Overlap to prevent boundary splitting of definitions
    min_chunk_words: int = 60              # Avoid solitary orphaned headers or sentences
    split_by_headings_first: bool = True   # Respect markdown and numbered chapter headings

@dataclass
class TopicConfig:
    """Member 2 Ownership: Keyphrase Mining & Graph Topic Extraction"""
    tfidf_max_features: int = 80           # Size of global vocabulary dictionary
    tfidf_ngram_range: tuple = (1, 3)      # Extract unigrams, bigrams, and trigrams
    textrank_window_size: int = 4          # Co-occurrence sliding window for word graph
    textrank_damping: float = 0.85         # PageRank damping factor (standard literature baseline)
    textrank_top_k: int = 12               # Number of salient keyphrases to surface per section
    cluster_similarity_threshold: float = 0.35 # Cosine cut-off for grouping related topics

@dataclass
class QuestionConfig:
    """Member 3 Ownership: Viva Question Generation & Filtering"""
    max_questions_per_chunk: int = 3       # Prevent cognitive overload per concept
    bloom_levels: List[str] = field(default_factory=lambda: [
        "Recall & Definition",
        "Mechanisms & Flow",
        "Trade-offs & Comparison",
        "Critical Viva Defense"
    ])
    duplicate_similarity_threshold: float = 0.65  # Questions with TF-IDF cosine similarity >= 0.65 are pruned
    min_question_char_len: int = 20        # Discard degenerate short prompts

@dataclass
class EvaluationConfig:
    """Member 4 Ownership: Multi-Rubric Answer Scoring & Feedback Engine"""
    # Weight distribution across the 4 assessment pillars (Total = 1.0)
    weight_concept_coverage: float = 0.40   # Recall of critical technical keywords/entities
    weight_semantic_similarity: float = 0.35 # Cosine similarity between student text and reference
    weight_depth_completeness: float = 0.15  # Sufficient explanation length without fluff
    weight_discourse_precision: float = 0.10 # Presence of reasoning markers ("because", "due to", "in contrast")
    
    # Grading cutoffs
    grade_thresholds: Dict[str, int] = field(default_factory=lambda: {
        "Distinction": 85,
        "Proficient": 70,
        "Satisfactory": 55,
        "Needs Revision": 0
    })

# Team Division Metadata (for transparent code ownership and viva defense)
TEAM_MODULE_MAP = {
    "Member 1": {
        "role": "Data Ingestion, Text Preprocessing & Heading-Aware Chunking",
        "files": ["modules/member1_preprocessing.py", "modules/member1_chunker.py"],
        "key_algorithms": ["Regex Normalization", "Sentence Boundary Disambiguation", "Sliding Window Offset Anchoring"]
    },
    "Member 2": {
        "role": "Topic Extraction, TF-IDF Keyphrase Mining & TextRank Graph Model",
        "files": ["modules/member2_topic_extraction.py"],
        "key_algorithms": ["Sublinear TF-IDF Vectorization", "PageRank Co-occurrence Graph", "Jaccard/Cosine Topic Clustering"]
    },
    "Member 3": {
        "role": "Viva Question Generation & Semantic Deduplication Engine",
        "files": ["modules/member3_question_generator.py", "modules/member3_duplicate_filter.py"],
        "key_algorithms": ["Syntactic Pattern Matcher", "Bloom's Taxonomy Heuristics", "Pairwise Cosine Deduplication"]
    },
    "Member 4": {
        "role": "Answer Evaluation, Rubric Scoring & Examiner Follow-Up Probing",
        "files": ["modules/member4_answer_evaluator.py"],
        "key_algorithms": ["Concept Keyword Recall", "Cosine Semantic Alignment", "Discourse Analysis", "Adaptive Probe Generation"]
    }
}

"""
=============================================================================
MODULE: member2_topic_extraction.py
AUTHOR: Team Member 2 (Topic Extraction & Keyphrase Mining Lead)
PURPOSE:
    Extract salient keyphrases, technical topics, and conceptual relationships
    using dual complementary methods:
    1. Statistical Frequency: TF-IDF n-gram scoring
    2. Graph Centrality: TextRank algorithm (PageRank on co-occurrence graph)
    Also groups related terms into topic clusters and builds an auto-glossary.
=============================================================================
"""

import math
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Set
from config import TopicConfig


class TopicExtractor:
    """
    Member 2: Topic & Keyphrase Extraction Engine.
    Combines statistical TF-IDF ranking with graph-theoretic TextRank to extract
    both frequent technical terms and structurally central concepts.
    """

    def __init__(self, config: TopicConfig = None):
        self.config = config or TopicConfig()

    # -----------------------------------------------------------------------
    # 1. TF-IDF KEYPHRASE MINING (Statistical Method)
    # -----------------------------------------------------------------------
    def extract_tfidf_keywords(
        self, chunks: List[Dict[str, Any]], preprocessor, top_n: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Compute TF-IDF across document chunks to surface terms that are
        specifically informative to each section rather than globally generic.

        Formula:
            TF(t, d) = count(t in d) / total_words(d)
            IDF(t) = log((1 + N) / (1 + DF(t))) + 1
            TF-IDF(t, d) = TF(t, d) * IDF(t)
        """
        if not chunks:
            return []

        doc_count = len(chunks)
        tokenized_docs = []
        for chk in chunks:
            tokens = preprocessor.tokenize(chk["text"], lower=True, remove_stopwords=True)
            tokenized_docs.append(tokens)

        # Document Frequency (DF)
        df = defaultdict(int)
        for tokens in tokenized_docs:
            unique_in_doc = set(tokens)
            for t in unique_in_doc:
                df[t] += 1

        # Global TF-IDF accumulator
        global_scores = defaultdict(float)

        for tokens in tokenized_docs:
            if not tokens:
                continue
            doc_len = len(tokens)
            tf = defaultdict(int)
            for t in tokens:
                tf[t] += 1

            for t, count in tf.items():
                tf_val = count / doc_len
                # Smooth IDF formula matching scikit-learn standard
                idf_val = math.log((1 + doc_count) / (1 + df[t])) + 1.0
                score = tf_val * idf_val
                global_scores[t] += score

        sorted_terms = sorted(global_scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for term, score in sorted_terms[:top_n]:
            results.append({
                "term": term,
                "score": round(score, 4),
                "doc_frequency": df[term],
                "method": "TF-IDF (Statistical)"
            })

        return results

    # -----------------------------------------------------------------------
    # 2. TEXTRANK KEYPHRASE EXTRACTION (Graph-Based Method)
    # -----------------------------------------------------------------------
    def extract_textrank_keyphrases(
        self, text: str, preprocessor, top_k: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Graph-based keyphrase ranking (Mihalcea & Tarau, 2004).
        
        1. Tokens become nodes in an undirected graph.
        2. Edges connect tokens that co-occur within a sliding window (default: 4).
        3. Score each node using PageRank iteration until convergence.
        4. Synthesize adjacent high-scoring words into multi-word keyphrases.
        """
        sentences = preprocessor.split_into_sentences(text)
        if not sentences:
            return []

        # Build vocabulary of candidate content words (non-stopwords, alphabetic)
        graph = defaultdict(lambda: defaultdict(int))
        nodes = set()
        window_size = self.config.textrank_window_size

        for sent in sentences:
            tokens = preprocessor.tokenize(sent, lower=True, remove_stopwords=True)
            # Add co-occurrence edges within window
            for i in range(len(tokens)):
                w1 = tokens[i]
                if len(w1) < 3:
                    continue
                nodes.add(w1)
                for j in range(i + 1, min(i + window_size, len(tokens))):
                    w2 = tokens[j]
                    if len(w2) < 3 or w1 == w2:
                        continue
                    nodes.add(w2)
                    graph[w1][w2] += 1
                    graph[w2][w1] += 1

        if not nodes:
            return []

        # Initialize PageRank scores uniformly: 1.0 / N
        d = self.config.textrank_damping
        scores = {node: 1.0 / len(nodes) for node in nodes}
        max_iterations = 35
        convergence_threshold = 1e-4

        # Power iteration
        for _ in range(max_iterations):
            new_scores = {}
            max_diff = 0.0

            for node in nodes:
                incoming_sum = 0.0
                for neighbor, weight in graph[node].items():
                    out_weight_sum = sum(graph[neighbor].values())
                    if out_weight_sum > 0:
                        incoming_sum += (weight / out_weight_sum) * scores[neighbor]

                new_score = (1 - d) + d * incoming_sum
                max_diff = max(max_diff, abs(new_score - scores[node]))
                new_scores[node] = new_score

            scores = new_scores
            if max_diff < convergence_threshold:
                break

        # Non-keyphrase words: adverbs, verbs, or meta-words that shouldn't anchor topics
        GENERIC_FILTER = {
            "dominated", "linearly", "historically", "precludes", "yields", "operates",
            "involves", "swapping", "dividing", "counteracts", "adopting", "relying",
            "consists", "relates", "relating", "tends", "tending", "imposing", "imposes",
            "long", "different", "multiple", "single", "distinct", "extended", "arbitrary",
            "prior", "initial", "principal", "substantially", "rapidly", "easily", "crucially",
            "step", "steps", "context", "contexts", "approach", "alternative", "effects", 
            "part", "ways", "order", "version", "manner", "addition"
        }

        # Re-construct multi-word keyphrases by scanning original text
        # If two adjacent words both have above-median scores, merge them
        median_score = sorted(scores.values())[len(scores) // 2] if scores else 0.0
        words_in_text = re.findall(r'\b[a-zA-Z0-9-]+\b', text.lower())

        candidate_phrases = defaultdict(float)
        i = 0
        while i < len(words_in_text):
            word = words_in_text[i]
            if (
                word in scores 
                and scores[word] >= median_score 
                and word not in preprocessor.stopwords 
                and word not in GENERIC_FILTER
                and not word.endswith("ly")
                and len(word) >= 3
            ):
                phrase = [word]
                phrase_score = scores[word]
                j = i + 1
                while j < min(i + 3, len(words_in_text)):
                    next_word = words_in_text[j]
                    if (
                        next_word in scores 
                        and scores[next_word] >= median_score 
                        and next_word not in preprocessor.stopwords 
                        and next_word not in GENERIC_FILTER
                        and not next_word.endswith("ly")
                        and len(next_word) >= 3
                    ):
                        phrase.append(next_word)
                        phrase_score += scores[next_word]
                        j += 1
                    else:
                        break
                
                # Check that phrase doesn't end with generic filter word
                while phrase and phrase[-1] in GENERIC_FILTER:
                    phrase.pop()
                    
                full_phrase = " ".join(phrase)
                if len(full_phrase) >= 4 and len(phrase) >= 1:
                    # Give bonus to 2-word and 3-word technical phrases
                    bonus = 1.4 if len(phrase) >= 2 else 1.0
                    candidate_phrases[full_phrase] = max(candidate_phrases[full_phrase], phrase_score * bonus)
                i = j
            else:
                i += 1

        sorted_phrases = sorted(candidate_phrases.items(), key=lambda x: x[1], reverse=True)

        results = []
        for phrase, score in sorted_phrases[:top_k]:
            results.append({
                "keyphrase": phrase,
                "score": round(score, 4),
                "method": "TextRank (Graph Centrality)"
            })

        return results

    # -----------------------------------------------------------------------
    # 3. TOPIC CLUSTERING & CO-OCCURRENCE THEMES
    # -----------------------------------------------------------------------
    def cluster_topics(
        self, chunks: List[Dict[str, Any]], keyphrases: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Group individual keyphrases into macro topic themes based on co-occurrence.
        If terms frequently appear in the same chunk, they belong to the same concept cluster.
        """
        if not keyphrases or not chunks:
            return []

        clusters = []
        # Matrix of chunk presence: term -> set of chunk_ids
        term_presence = defaultdict(set)
        for chk in chunks:
            c_text = chk["text"].lower()
            for kp in keyphrases:
                if kp.lower() in c_text:
                    term_presence[kp].add(chk["chunk_id"])

        assigned = set()
        cluster_id = 1

        for i, term_a in enumerate(keyphrases):
            if term_a in assigned:
                continue

            current_cluster = [term_a]
            assigned.add(term_a)
            chunks_a = term_presence[term_a]

            for term_b in keyphrases[i + 1:]:
                if term_b in assigned:
                    continue
                chunks_b = term_presence[term_b]
                # Jaccard overlap of hosting chunks
                union_len = len(chunks_a | chunks_b)
                if union_len > 0:
                    jaccard = len(chunks_a & chunks_b) / union_len
                    if jaccard >= self.config.cluster_similarity_threshold:
                        current_cluster.append(term_b)
                        assigned.add(term_b)

            # Assign human-readable cluster label
            primary_label = current_cluster[0].title()
            clusters.append({
                "cluster_id": f"TOPIC-{cluster_id:02d}",
                "theme_name": f"{primary_label} Focus",
                "terms": current_cluster,
                "supporting_chunks": list(chunks_a)
            })
            cluster_id += 1

        return clusters

    # -----------------------------------------------------------------------
    # 4. AUTO-GLOSSARY BUILDER
    # -----------------------------------------------------------------------
    def build_glossary(
        self, full_text: str, key_terms: List[str], preprocessor
    ) -> List[Dict[str, str]]:
        """
        Locate the definitive sentence in the document that defines each key term.
        Looks for definitional trigger words: 'is', 'refers to', 'defined as', 'represents'.
        """
        sentences = preprocessor.split_into_sentences(full_text)
        glossary = []

        definitional_patterns = [
            r'\b(?:is defined as|refers to|is a|is an|represents|consists of|denotes)\b'
        ]

        for term in key_terms:
            term_clean = term.lower()
            best_def = ""

            for sent in sentences:
                s_lower = sent.lower()
                if term_clean in s_lower:
                    # Check if sentence has definitional phrasing
                    has_marker = any(re.search(pat, s_lower) for pat in definitional_patterns)
                    if has_marker:
                        best_def = sent.strip()
                        break
                    elif not best_def:
                        best_def = sent.strip()

            if best_def:
                glossary.append({
                    "term": term,
                    "definition_sentence": best_def
                })

        return glossary

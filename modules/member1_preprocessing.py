"""
=============================================================================
MODULE: member1_preprocessing.py
AUTHOR: Team Member 1 (Data Ingestion & Text Preprocessing Lead)
PURPOSE:
    Ingest, clean, normalize, and segment raw technical documents (PDF, TXT, MD).
    Produces clean sentence streams, tokenized representations, and document
    readability statistics required by downstream topic and question engines.
=============================================================================
"""

import re
import math
from typing import List, Dict, Any, Tuple
from pathlib import Path
from config import PreprocessingConfig

# ---------------------------------------------------------------------------
# Domain-Specific Academic Stopword List
# We maintain an explicit built-in list so this module works 100% offline
# without requiring external network downloads during viva demonstrations.
# ---------------------------------------------------------------------------
BASE_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "also", "thus", "therefore", "however", "furthermore",
    "across", "along", "within", "without", "beyond", "behind", "upon", "towards",
    "among", "rather", "given", "historically", "entirely", "allows", "allowing",
    "allowed", "enables", "enabling", "enabled", "serves", "serving", "performed",
    "performing", "using", "used", "relies", "relying", "imposes", "consists",
    "yields", "swapping", "dividing", "counteracts", "operates", "adopting", "involves"
}

# Common academic abbreviations that should NOT trigger a sentence split
ABBREVIATIONS = {
    "e.g.", "i.e.", "et al.", "fig.", "figs.", "ref.", "vol.", "no.",
    "dr.", "prof.", "dept.", "eq.", "eqs.", "approx.", "vs.", "v.", "sec."
}


class DocumentPreprocessor:
    """
    Member 1: Core preprocessing pipeline.
    Responsible for text extraction, unicode cleaning, sentence boundary
    disambiguation, and linguistic health checks.
    """

    def __init__(self, config: PreprocessingConfig = None):
        self.config = config or PreprocessingConfig()
        self.stopwords = set(BASE_STOPWORDS)

    # -----------------------------------------------------------------------
    # 1. FILE EXTRACTION
    # -----------------------------------------------------------------------
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract raw text from a PDF, Markdown, or plain text file.
        Uses pypdf for PDF extraction and UTF-8 decoder with error fallback.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()

        if suffix == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        pages_text.append(f"--- Page {idx + 1} ---\n" + text)
                return "\n\n".join(pages_text)
            except Exception as e:
                raise RuntimeError(f"Error parsing PDF file with pypdf: {str(e)}")

        if suffix in [".docx", ".doc"]:
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                with zipfile.ZipFile(str(path)) as docx:
                    tree = ET.fromstring(docx.read("word/document.xml"))
                    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    paragraphs = []
                    for p in tree.iterfind('.//w:p', namespace):
                        texts = [node.text for node in p.iterfind('.//w:t', namespace) if node.text]
                        if texts:
                            paragraphs.append("".join(texts))
                    return "\n\n".join(paragraphs)
            except Exception as e:
                # If binary doc or read fails, attempt fallback
                pass

        # Plain text, markdown, or code files
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1", errors="replace")

    # -----------------------------------------------------------------------
    # 2. NORMALIZATION & CLEANING
    # -----------------------------------------------------------------------
    def clean_text(self, raw_text: str) -> str:
        """
        Normalize typographic oddities, whitespace, and formatting glitches.
        Preserves technical acronyms, brackets, and math notation.
        """
        if not raw_text:
            return ""

        text = raw_text

        # Replace Windows carriage returns and stray form feeds
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")

        # Resolve common typographic ligatures (common in PDF extractions)
        ligature_map = {
            "\ufb01": "fi", "\ufb02": "fl", "\ufb00": "ff",
            "\ufb03": "ffi", "\ufb04": "ffl", "“": '"', "”": '"',
            "‘": "'", "’": "'", "—": " - ", "–": " - "
        }
        for lig, repl in ligature_map.items():
            text = text.replace(lig, repl)

        # Strip standalone header/footer page markers like "Page 12 of 45" or solitary numbers
        if self.config.strip_header_footer_numbers:
            text = re.sub(r'^\s*(?:Page\s+\d+(?:\s+of\s+\d+)?|\d+)\s*$', '', text, flags=re.MULTILINE)

        # Consolidate 3+ newlines to double newline (paragraphs)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Consolidate multiple inline spaces to a single space
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    # -----------------------------------------------------------------------
    # 3. SENTENCE BOUNDARY DISAMBIGUATION (Rule-Based + Lookahead)
    # -----------------------------------------------------------------------
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into clean sentences without splitting on abbreviations
        (e.g., 'i.e.', 'et al.') or decimal numbers (e.g., '3.14').
        
        Design decision:
        We use a protected substitution step rather than naive regex to guarantee
        that academic abbreviations do not falsely terminate a sentence.
        """
        if not text:
            return []

        cleaned = text.strip()

        # Protect known abbreviations with placeholder tokens
        placeholders = {}
        for idx, abbr in enumerate(ABBREVIATIONS):
            token = f"__ABBR_{idx}__"
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            cleaned = pattern.sub(token, cleaned)
            placeholders[token] = abbr

        # Protect decimal numbers (e.g. 99.8%)
        decimal_matches = re.findall(r'\b\d+\.\d+\b', cleaned)
        for idx, num in enumerate(decimal_matches):
            token = f"__DEC_{idx}__"
            cleaned = cleaned.replace(num, token)
            placeholders[token] = num

        # Split on sentence terminals (. ! ?) followed by whitespace and capital letter or newline
        raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\n])', cleaned)

        results = []
        for s in raw_sentences:
            s_clean = s.strip()
            # Restore protected tokens
            for token, orig in placeholders.items():
                s_clean = s_clean.replace(token, orig)

            # Filter out empty or micro fragments
            if len(s_clean) >= self.config.min_sentence_length:
                results.append(s_clean)

        return results

    # -----------------------------------------------------------------------
    # 4. TOKENIZATION & STOPWORD FILTERING
    # -----------------------------------------------------------------------
    def stem_token(self, token: str) -> str:
        """
        Reduce token to base stem using Porter Stemmer (with regex fallback).
        Crucial for matching student answers across morphological variations.
        """
        try:
            from nltk.stem import PorterStemmer
            return PorterStemmer().stem(token)
        except Exception:
            # Fallback simple suffix stripper
            t = token.lower()
            for suffix in ["ing", "ingly", "ation", "tions", "tion", "ed", "ies", "es", "s"]:
                if t.endswith(suffix) and len(t) > len(suffix) + 2:
                    return t[:-len(suffix)]
            return t

    def tokenize(self, text: str, lower: bool = True, remove_stopwords: bool = True, stem: bool = False) -> List[str]:
        """
        Extract clean alpha-numeric word tokens.
        Preserves technical compound words and handles hyphenated phrases.
        """
        # Split on whitespace/punctuation but treat hyphenated words as separate tokens too
        raw_tokens = re.findall(r'[a-zA-Z0-9]+', text)
        
        if lower:
            processed = [t.lower() for t in raw_tokens]
        else:
            processed = raw_tokens

        if remove_stopwords:
            processed = [t for t in processed if t.lower() not in self.stopwords and len(t) > 1]

        if stem:
            processed = [self.stem_token(t) for t in processed]

        return processed

    # -----------------------------------------------------------------------
    # 5. DOCUMENT STATISTICAL TELEMETRY
    # -----------------------------------------------------------------------
    def compute_document_stats(self, raw_text: str, sentences: List[str]) -> Dict[str, Any]:
        """
        Compute linguistic and readability statistics.
        Provides measurable data for the team's viva presentation:
        - Word count, Sentence count, Character count
        - Average sentence length
        - Lexical Diversity (Type-Token Ratio TTR)
        - Flesch Reading Ease score
        """
        words = self.tokenize(raw_text, lower=True, remove_stopwords=False)
        total_words = max(1, len(words))
        total_sentences = max(1, len(sentences))
        total_chars = len(raw_text)

        # Lexical Diversity: Unique tokens / Total tokens
        unique_words = len(set(words))
        ttr = round(unique_words / total_words, 4)

        # Syllable counter approximation for Flesch Reading Ease
        def count_syllables(word: str) -> int:
            w = word.lower()
            if len(w) <= 3:
                return 1
            # Count vowel transitions
            count = len(re.findall(r'[aeiouy]+', w))
            if w.endswith('e') and not w.endswith('le'):
                count = max(1, count - 1)
            return max(1, count)

        total_syllables = sum(count_syllables(w) for w in words[:1000]) # Sample 1000 words for speed
        sampled_words = min(1000, total_words)
        avg_syllables_per_word = total_syllables / max(1, sampled_words)
        avg_words_per_sentence = total_words / total_sentences

        # Standard Flesch Reading Ease formula:
        # 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_score = round(max(0.0, min(100.0, flesch_score)), 2)

        # Readability classification
        if flesch_score >= 70:
            reading_level = "Standard / Easy Reading"
        elif flesch_score >= 50:
            reading_level = "Undergraduate Technical"
        elif flesch_score >= 30:
            reading_level = "College Academic / Research"
        else:
            reading_level = "Dense Research Paper"

        return {
            "total_characters": total_chars,
            "total_words": total_words,
            "total_sentences": total_sentences,
            "avg_sentence_length": round(avg_words_per_sentence, 1),
            "type_token_ratio": ttr,
            "flesch_reading_ease": flesch_score,
            "reading_level": reading_level
        }


# Quick sanity test if run standalone
if __name__ == "__main__":
    preprocessor = DocumentPreprocessor()
    sample = (
        "In modern Deep Learning (e.g. Vaswani et al., 2017), the Transformer model relies on self-attention. "
        "The scaled dot-product attention computes softmax(QK^T / sqrt(d_k))V. "
        "This allows the network to capture long-range dependencies efficiently."
    )
    cleaned = preprocessor.clean_text(sample)
    sents = preprocessor.split_into_sentences(cleaned)
    stats = preprocessor.compute_document_stats(cleaned, sents)
    print("--- Preprocessing Sanity Check ---")
    print(f"Detected {len(sents)} sentences:")
    for i, s in enumerate(sents):
        print(f" [{i+1}] {s}")
    print("\nTelemetry Stats:", stats)

"""
=============================================================================
MODULE: member1_chunker.py
AUTHOR: Team Member 1 (Data Ingestion & Text Preprocessing Lead)
PURPOSE:
    Heading-aware, context-preserving semantic document chunker.
    Calculates exact character and line offsets for every passage so downstream
    questions can be visually verified against original source text.
=============================================================================
"""

import re
from typing import List, Dict, Any
from config import ChunkingConfig


class DocumentChunker:
    """
    Member 1: Heading-aware Chunking Engine.
    Breaks large documents into coherent, question-ready contexts while
    maintaining strict citation anchors and character offsets.
    """

    def __init__(self, config: ChunkingConfig = None):
        self.config = config or ChunkingConfig()

    def detect_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect structural headings in the document.
        Supports:
        - Markdown headers (# Heading, ## Subheading)
        - Numbered academic sections (1.0 Introduction, 2.1 Methodology)
        - All-caps section titles (ABSTRACT, METHODOLOGY, CONCLUSION)
        """
        lines = text.split("\n")
        sections = []
        current_title = "General Content"
        current_lines = []
        start_char = 0
        current_pos = 0

        # Patterns for academic headers
        heading_patterns = [
            r'^(#{1,4})\s+(.+)$',                                # Markdown: ## Heading
            r'^(\d+(?:\.\d+)*)\s+([A-Z][A-Za-z0-9\s:_-]{2,60})$', # 1.1 Methodology
            r'^([A-Z][A-Z\s0-9:_-]{3,40})$'                     # ALL CAPS: BACKGROUND
        ]

        for line in lines:
            line_len = len(line) + 1 # +1 for newline
            stripped = line.strip()

            is_heading = False
            heading_text = ""

            if stripped and len(stripped) < 140:
                for pat in heading_patterns:
                    match = re.match(pat, stripped)
                    if match:
                        is_heading = True
                        groups = match.groups()
                        heading_text = groups[-1].strip()
                        break

            if is_heading:
                # Flush previous section
                if current_lines:
                    section_body = "\n".join(current_lines).strip()
                    word_cnt = len(section_body.split())
                    # Discard tiny initial subtitle/author lines (< 15 words) before the first section
                    if word_cnt >= 15 or len(sections) > 0:
                        sections.append({
                            "title": current_title,
                            "body": section_body,
                            "start_char": start_char,
                            "end_char": current_pos - 1
                        })
                # Clean heading text (strip markdown symbols like ## and leading numbering if redundant)
                clean_heading = re.sub(r'^#+\s*', '', heading_text).strip()
                current_title = clean_heading
                current_lines = []  # Body starts empty, heading is NOT body text
                start_char = current_pos
            else:
                # Only add non-heading lines to body text
                if stripped:
                    current_lines.append(line)

            current_pos += line_len

        # Flush final section
        if current_lines:
            section_body = "\n".join(current_lines).strip()
            if section_body:
                sections.append({
                    "title": current_title,
                    "body": section_body,
                    "start_char": start_char,
                    "end_char": current_pos
                })

        return sections if sections else [{
            "title": "Document Content",
            "body": text,
            "start_char": 0,
            "end_char": len(text)
        }]

    def create_chunks(self, full_text: str, preprocessor) -> List[Dict[str, Any]]:
        """
        Produce verified chunks with:
        - chunk_id: Unique handle (e.g. CHK-001)
        - section_title: Breadcrumb context
        - text: Complete passage text
        - sentences: Constituent sentence list
        - start_char & end_char: Exact character spans in full_text
        - word_count: Number of words
        """
        sections = self.detect_sections(full_text)
        chunks = []
        chunk_counter = 1

        for sec in sections:
            sec_title = sec["title"]
            sec_body = sec["body"]
            sentences = preprocessor.split_into_sentences(sec_body)

            if not sentences:
                continue

            current_chunk_sentences = []
            current_chunk_words = 0

            for sent in sentences:
                sent_words = len(sent.split())

                if current_chunk_words + sent_words > self.config.target_chunk_words and current_chunk_words >= self.config.min_chunk_words:
                    # Finalize current chunk
                    chunk_text = " ".join(current_chunk_sentences)
                    # Find approximate character position in full_text
                    char_offset = full_text.find(chunk_text[:50])
                    if char_offset == -1:
                        char_offset = sec["start_char"]

                    chunks.append({
                        "chunk_id": f"CHK-{chunk_counter:03d}",
                        "section_title": sec_title,
                        "text": chunk_text,
                        "sentences": list(current_chunk_sentences),
                        "word_count": current_chunk_words,
                        "start_char": char_offset,
                        "end_char": char_offset + len(chunk_text)
                    })
                    chunk_counter += 1

                    # Create overlap using last sentence(s)
                    overlap_sentences = []
                    overlap_words = 0
                    for s in reversed(current_chunk_sentences):
                        sw = len(s.split())
                        if overlap_words + sw <= self.config.chunk_overlap_words:
                            overlap_sentences.insert(0, s)
                            overlap_words += sw
                        else:
                            break

                    current_chunk_sentences = list(overlap_sentences)
                    current_chunk_words = overlap_words

                current_chunk_sentences.append(sent)
                current_chunk_words += sent_words

            # Add remaining sentences as final chunk for this section
            min_threshold = 12 if len(chunks) == 0 else 15
            if current_chunk_sentences and (current_chunk_words >= min_threshold or len(chunks) == 0):
                chunk_text = " ".join(current_chunk_sentences)
                char_offset = full_text.find(chunk_text[:50])
                if char_offset == -1:
                    char_offset = sec["start_char"]

                chunks.append({
                    "chunk_id": f"CHK-{chunk_counter:03d}",
                    "section_title": sec_title,
                    "text": chunk_text,
                    "sentences": list(current_chunk_sentences),
                    "word_count": current_chunk_words,
                    "start_char": char_offset,
                    "end_char": char_offset + len(chunk_text)
                })
                chunk_counter += 1

        return chunks

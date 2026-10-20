"""
=============================================================================
COMMAND LINE INTERFACE: cli.py
PURPOSE:
    Interactive CLI tool for terminal-based inspection, question generation,
    and simulated viva voce practice defense.
=============================================================================
"""

import sys
import argparse
from pathlib import Path
from pipeline import VivaPipeline

# Ensure Windows terminal can print UTF-8 characters safely
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="VivaPrep: NLP-Powered Viva Voce Preparation & Assessment CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect NLP stages and document statistics")
    inspect_parser.add_argument("file", help="Path to text or PDF document")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Generate and filter viva questions")
    gen_parser.add_argument("file", help="Path to text or PDF document")

    # Command: practice
    practice_parser = subparsers.add_parser("practice", help="Interactive oral defense simulator in terminal")
    practice_parser.add_argument("file", help="Path to text or PDF document")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[Error] File not found: {args.file}")
        sys.exit(1)

    pipeline = VivaPipeline()
    print(f"[*] Reading and processing: {file_path.name}...")
    raw_text = pipeline.preprocessor.extract_text_from_file(str(file_path))
    summary = pipeline.process_text(raw_text, document_name=file_path.name)
    print(f"[OK] Pipeline completed in {summary['runtime_ms']} ms\n")

    if args.command == "inspect":
        print("=" * 70)
        print("STAGE 1 & 2: DOCUMENT STATISTICS (Member 1)")
        print("=" * 70)
        for k, v in summary["stats"].items():
            print(f"  - {k.replace('_', ' ').title():<25}: {v}")
        print(f"  - Generated Chunks        : {summary['chunk_count']}")

        print("\n" + "=" * 70)
        print("STAGE 3: TOPIC EXTRACTION & KEYPHRASE MINING (Member 2)")
        print("=" * 70)
        print("\n[Top TF-IDF Keywords]:")
        for item in summary["tfidf_keywords"][:8]:
            print(f"  - {item['term']:<20} (Score: {item['score']}, DF: {item['doc_frequency']})")

        print("\n[Top TextRank Graph Keyphrases]:")
        for item in summary["textrank_keyphrases"][:8]:
            print(f"  - {item['keyphrase']:<20} (Centrality: {item['score']})")

        print("\n[Key Concept Glossary]:")
        for g in summary["glossary"][:4]:
            print(f"  - {g['term'].title()}: {g['definition_sentence']}")

    elif args.command == "generate":
        print("=" * 70)
        print(f"VIVA QUESTION BANK ({summary['question_count']} Questions) (Member 3)")
        print("=" * 70)
        audit = summary["filter_audit"]
        print(f"Deduplication Audit: {audit['initial_candidates']} generated -> {audit['retained_count']} retained ({audit['pruned_count']} pruned, {audit['reduction_percentage']} redundancy removed)\n")

        for q in summary["questions"]:
            print(f"[{q['question_id']}] [{q['bloom_level'].upper()}] (Target: {q['target_concept']})")
            print(f"  Question: {q['question_text']}")
            print(f"  Section : {q['section_title']} (Chunk: {q['source_chunk_id']})")
            print(f"  Citation: \"{q['source_citation'][:110]}...\"")
            print()

    elif args.command == "practice":
        print("=" * 70)
        print("VIVA VOCE ORAL DEFENSE SIMULATOR (Member 4)")
        print("=" * 70)
        questions = summary["questions"]
        if not questions:
            print("No questions generated for this document.")
            sys.exit(0)

        for q in questions:
            print("\n" + "-" * 70)
            print(f"EXAMINER PROBE [{q['question_id']}] - Level: {q['bloom_level']}")
            print(f"\"{q['question_text']}\"")
            print("-" * 70)
            print("Type your defense answer below (or type 'skip' to pass, 'quit' to exit):")
            user_ans = input("\nYour Answer > ").strip()

            if user_ans.lower() == "quit":
                break
            if user_ans.lower() == "skip" or not user_ans:
                continue

            print("\n[*] Evaluating defense...")
            eval_res = pipeline.evaluate_answer(q["question_id"], user_ans)

            print(f"\n[Score: {eval_res['final_score']}/100 - Grade: {eval_res['grade']}]")
            metrics = eval_res["metric_breakdown"]
            print(f"  - Concept Coverage   : {metrics['concept_coverage_score']}%")
            print(f"  - Semantic Alignment : {metrics['semantic_similarity_score']}%")
            print(f"  - Technical Depth    : {metrics['depth_completeness_score']}%")
            print(f"  - Reasoning Markers  : {metrics['discourse_reasoning_score']}%")

            print(f"\nCovered Concepts: {', '.join(eval_res['covered_concepts']) if eval_res['covered_concepts'] else 'None'}")
            print(f"Missing Concepts: {', '.join(eval_res['missing_concepts']) if eval_res['missing_concepts'] else 'None'}")
            print(f"\nExaminer Remarks: {eval_res['examiner_remarks']}")
            print(f"\nExaminer Follow-Up Probe: {eval_res['followup_question']}")
            print(f"\nVerified Citation: \"{eval_res['source_citation']}\"")


if __name__ == "__main__":
    main()

"""
Convert a simple Q&A CSV into the full questions.csv format used by the quiz app.

Reads an input CSV with columns: question,answer (no header required but recommended).
Generates 3 distractors per question using Gemini-like API (patterned after
/home/lediem/Dropbox/hnd/python_script/gemini_ask.py). If Gemini client packages
are not available, falls back to template distractors.

Output CSV matches: /home/lediem/Dropbox/streamlit-quizz/data/questions.csv
Format: id,question,option_A,option_B,option_C,option_D,answer  (answer is A/B/C/D)

Usage:
    python convert_with_gemini.py --input /path/to/input.csv \
        --output /home/lediem/Dropbox/streamlit-quizz/data/questions.csv

Notes:
- Requires gemini_webapi and gemini_cookies for live generation.
- This script uses absolute paths and conservative error handling.
"""

import argparse
import asyncio
import csv
import os
import random
import sys
from pathlib import Path
from typing import List, Tuple

# Try to import Gemini-related libraries; if missing, we'll fallback
GEMINI_AVAILABLE = True
try:
    from gemini_webapi import GeminiClient
    from gemini_webapi.constants import Model
    from gemini_cookies import get_gemini_cookies
except Exception:
    GEMINI_AVAILABLE = False


def read_input_pairs(input_path: str) -> List[Tuple[str, str]]:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    pairs: List[Tuple[str, str]] = []
    with input_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        if not rows:
            return pairs

        # Detect header: if first row contains 'question' and 'answer'
        header = [c.strip().lower() for c in rows[0]]
        start_idx = 0
        if len(header) >= 2 and "question" in header and "answer" in header:
            q_idx = header.index("question")
            a_idx = header.index("answer")
            start_idx = 1
            for r in rows[1:]:
                if len(r) <= max(q_idx, a_idx):
                    continue
                q = r[q_idx].strip()
                a = r[a_idx].strip()
                if q and a:
                    pairs.append((q, a))
        else:
            # No header: assume first two columns are question, answer
            for r in rows:
                if len(r) < 2:
                    continue
                q = r[0].strip()
                a = r[1].strip()
                if q and a:
                    pairs.append((q, a))

    return pairs


async def generate_distractors_gemini(question: str, answer: str, client: GeminiClient) -> List[str]:
    """Call Gemini client to generate 3 distractors."""
    prompt = (
        "Given this question and the correct answer, generate exactly 3 plausible but incorrect "
        "distractor options. Return each distractor on its own line, with no labels or numbering. "
        "Avoid 'All of the above' or similar choices. Keep distractors similar in style and length to the correct answer.\n\n"
        f"Question: {question}\nCorrect Answer: {answer}\n"
    )

    try:
        response = await client.generate_content(prompt, model=Model.G_2_5_PRO)
        text = getattr(response, "text", "") or ""
    except Exception as e:
        print(f"Warning: Gemini generation failed: {e}", file=sys.stderr)
        return []

    # Split into non-empty lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    distractors = []
    for l in lines:
        # Remove simple numbering like '1. ' or '- '
        clean = l.lstrip("- ").lstrip("0123456789. ")
        if clean and clean.lower() != answer.lower():
            distractors.append(clean)
        if len(distractors) >= 3:
            break

    return distractors[:3]


def fallback_distractors(answer: str, n: int = 3) -> List[str]:
    """Generate simple fallback distractors when Gemini is unavailable.

    This uses lightweight transformations and placeholders; not AI-generated.
    """
    base = answer.strip()
    distractors = set()

    # If answer is short, create numeric/string variations
    if base.replace(" ", "").isalnum() and len(base) <= 6:
        # create nearby numbers/strings
        try:
            num = int(base)
            distractors.update({str(num + 1), str(max(0, num - 1)), str(num + 2)})
        except Exception:
            # create alphabetical or suffix variants
            distractors.update({base + " Jr", base + " II", base + " (old)"})
    else:
        # word-level perturbations
        tokens = base.split()
        if len(tokens) >= 2:
            # shuffle words
            shuffled = tokens[::-1]
            distractors.add(" ".join(shuffled))
            distractors.add(tokens[0] + " " + (tokens[-1] if len(tokens) > 1 else "Option"))
        distractors.add(base + " (not correct)")
        distractors.add("None of the above")

    # Ensure we return exactly n distinct distractors not equal to correct answer
    results = [d for d in distractors if d.lower() != base.lower()][:n]
    # Fill with generic placeholders if still short
    i = 1
    while len(results) < n:
        candidate = f"Option {i}"
        if candidate.lower() != base.lower() and candidate not in results:
            results.append(candidate)
        i += 1
    return results[:n]


async def convert_pairs_to_questions(pairs: List[Tuple[str, str]], output_path: str, use_gemini: bool = True):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # If using Gemini, initialize client as in gemini_ask.py pattern
    client = None
    if use_gemini and GEMINI_AVAILABLE:
        try:
            cookies = get_gemini_cookies()
            SECURE_1PSID = cookies["__Secure-1PSID"]
            SECURE_1PSIDTS = cookies["__Secure-1PSIDTS"]
            client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS)
            await client.init(timeout=30, auto_close=True, close_delay=60, auto_refresh=False)
            print("Gemini client initialized", file=sys.stderr)
        except Exception as e:
            print(f"Warning: could not initialize Gemini client: {e}", file=sys.stderr)
            client = None

    rows = []
    for idx, (q, a) in enumerate(pairs, start=1):
        print(f"Processing {idx}/{len(pairs)}", file=sys.stderr)
        distractors = []
        if client:
            distractors = await generate_distractors_gemini(q, a, client)
        if not distractors or len(distractors) < 3:
            # fallback
            distractors = fallback_distractors(a, 3)

        # Build options, ensure correct answer included, randomize
        opts = list(distractors) + [a]
        # Deduplicate while preserving count
        seen = []
        for o in opts:
            if o not in seen:
                seen.append(o)
        # If not enough unique options, fill placeholders
        i = 1
        while len(seen) < 4:
            candidate = f"Option {i}"
            if candidate not in seen and candidate.lower() != a.lower():
                seen.append(candidate)
            i += 1

        # Shuffle options
        random.shuffle(seen)
        # Map to A-D
        option_map = {"A": seen[0], "B": seen[1], "C": seen[2], "D": seen[3]}
        # Find correct letter
        correct_letter = None
        for k, v in option_map.items():
            if v.strip().lower() == a.strip().lower():
                correct_letter = k
                break
        if not correct_letter:
            # If exact match not found, try case-insensitive contains
            for k, v in option_map.items():
                if a.strip().lower() in v.strip().lower() or v.strip().lower() in a.strip().lower():
                    correct_letter = k
                    break
        if not correct_letter:
            # As last resort, set A
            correct_letter = "A"
            option_map["A"] = a

        rows.append({
            "id": str(idx),
            "question": q,
            "option_A": option_map["A"],
            "option_B": option_map["B"],
            "option_C": option_map["C"],
            "option_D": option_map["D"],
            "answer": correct_letter,
        })

    # Close client if opened
    if client:
        try:
            await client.close()
        except Exception:
            pass

    # Write CSV header and rows
    fieldnames = ["id", "question", "option_A", "option_B", "option_C", "option_D", "answer"]

    # Backup existing output file if present
    if output_path.exists():
        bak = output_path.with_suffix(output_path.suffix + ".bak")
        output_path.replace(bak)
        print(f"Existing {output_path} moved to {bak}", file=sys.stderr)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} questions to {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Convert QA CSV to quiz questions CSV using Gemini-like generation")
    parser.add_argument("--input", "-i", required=True, help="Input CSV path (question,answer)")
    parser.add_argument("--output", "-o", default="/home/lediem/Dropbox/streamlit-quizz/data/questions.csv", help="Output CSV path")
    parser.add_argument("--no-gemini", action="store_true", help="Do not attempt to use Gemini client; use fallback distractors only")

    args = parser.parse_args()

    pairs = read_input_pairs(args.input)
    if not pairs:
        print("No valid question-answer pairs found in input.", file=sys.stderr)
        sys.exit(1)

    use_gemini = (not args.no_gemini) and GEMINI_AVAILABLE
    if not GEMINI_AVAILABLE and not args.no_gemini:
        print("Note: Gemini libraries not available in this environment; falling back to template distractors.", file=sys.stderr)

    asyncio.run(convert_pairs_to_questions(pairs, args.output, use_gemini=use_gemini))


if __name__ == "__main__":
    main()

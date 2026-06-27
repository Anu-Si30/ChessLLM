"""
without_stockfish.py
---------------------
Flow: FEN -> Qwen alone is asked to find the best move, explain its reasoning,
and identify the underlying tactical/strategic concept. No engine is consulted,
so this tests the model's own chess ability (small models will often be wrong --
that's expected and the point of comparison against with_stockfish.py).

Output is strict JSON, printed to console AND appended to a results file
(default: results_without_stockfish.json) as a list of records.

Usage:
    python without_stockfish.py "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 4 4"
    python without_stockfish.py "<FEN>" --model Qwen/Qwen2.5-3B-Instruct
    python without_stockfish.py "<FEN>" --output my_results.json
"""

import argparse
import json
import os
from datetime import datetime, timezone

from common import load_model, generate, extract_json, DEFAULT_MODEL_NAME, CHESS_CONCEPTS

CONCEPT_LIST_STR = ", ".join(CHESS_CONCEPTS)

SYSTEM_PROMPT = (
    "You are a chess coach. You will be given a position (FEN). Find the best "
    "move, identify the SINGLE underlying tactical or strategic concept from this "
    f"fixed list: [{CONCEPT_LIST_STR}], and justify why that move is correct.\n\n"
    "You MUST respond with ONLY a valid JSON object, no markdown fences, no extra "
    "text before or after, in EXACTLY this shape:\n"
    "{\n"
    '  "best_move_san": "<move in standard algebraic notation, e.g. Nxe5, Qh5+, O-O>",\n'
    '  "concept": "<one item copied exactly from the fixed list above>",\n'
    '  "justification": "<step-by-step explanation of why this move is best, referencing the concept>"\n'
    "}"
)

USER_PROMPT_TEMPLATE = "Position (FEN): {fen}\n\nRespond with the JSON object only."


def save_result(record: dict, output_path: str):
    """Appends a record to a JSON list file, creating it if it doesn't exist."""
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(record)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def load_positions_from_file(path: str) -> list[str]:
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"JSON file must contain an array of FEN strings")
    return data


def load_positions(args) -> list[str]:
    """Load FEN positions from CLI args, --file, or both.
    Auto-detects .json files passed as positional args."""
    positions = []
    if args.fen:
        for item in args.fen:
            if item.endswith(".json") and os.path.isfile(item):
                positions.extend(load_positions_from_file(item))
            else:
                positions.append(item)
    if args.file:
        positions.extend(load_positions_from_file(args.file))
    if not positions:
        print("ERROR: Provide at least one FEN via positional arg or --file")
        raise SystemExit(1)
    return positions


def main():
    parser = argparse.ArgumentParser(description="Model-only move + concept identification")
    parser.add_argument("fen", nargs="*", help="FEN string(s) of position(s)")
    parser.add_argument("--file", default=None, help="Path to JSON file with a list of FEN strings")
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME, help="HF model name")
    parser.add_argument("--output", default="results_without_stockfish.json", help="Path to JSON results file")
    args = parser.parse_args()

    positions = load_positions(args)
    print(f"Loaded {len(positions)} position(s)")

    print(f"Loading model {args.model} (first run will download weights)...")
    model, tokenizer = load_model(args.model)

    for i, fen in enumerate(positions, 1):
        print(f"\n[{i}/{len(positions)}] FEN: {fen}")
        user_prompt = USER_PROMPT_TEMPLATE.format(fen=fen)
        print("Asking Qwen to find the move, the concept, and justify it...")
        raw_response = generate(model, tokenizer, SYSTEM_PROMPT, user_prompt)

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": args.model,
            "fen": fen,
            "mode": "without_stockfish",
        }

        try:
            parsed = extract_json(raw_response)
            record.update({
                "best_move_san": parsed.get("best_move_san"),
                "concept": parsed.get("concept"),
                "justification": parsed.get("justification"),
                "parse_error": None,
            })
        except (ValueError, json.JSONDecodeError) as e:
            record.update({
                "best_move_san": None,
                "concept": None,
                "justification": None,
                "parse_error": str(e),
                "raw_response": raw_response,
            })

        save_result(record, args.output)

        print("=" * 60)
        print(json.dumps(record, indent=2))
        print("=" * 60)

    print(f"\nAll results saved to {args.output}")


if __name__ == "__main__":
    main()
"""
with_stockfish.py
------------------
Flow: FEN -> Stockfish gives the best move -> Qwen is told the FEN + the move,
and asked to (1) name the underlying tactical/strategic concept and
(2) justify why that move is correct.

Output is strict JSON, printed to console AND appended to a results file.

Usage:
    python with_stockfish.py "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 4 4"
    python with_stockfish.py --file positions.json
    python with_stockfish.py "FEN1" "FEN2" --file more_positions.json
    python with_stockfish.py "<FEN>" --stockfish-path /path/to/stockfish --model Qwen/Qwen2.5-3B-Instruct
"""

import argparse
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timezone

from common import get_best_move, load_model, generate, extract_json, DEFAULT_MODEL_NAME, CHESS_CONCEPTS

CONCEPT_LIST_STR = ", ".join(CHESS_CONCEPTS)

SYSTEM_PROMPT = (
    "You are a chess coach. You will be given a position (FEN) and the move "
    "a strong engine considers best. Identify the SINGLE underlying tactical or "
    f"strategic concept from this fixed list: [{CONCEPT_LIST_STR}], and clearly "
    "justify why the given move is the best one in this position.\n\n"
    "You MUST respond with ONLY a valid JSON object, no markdown fences, no extra "
    "text before or after, in EXACTLY this shape:\n"
    "{\n"
    '  "best_move_san": "<the move given to you>",\n'
    '  "concept": "<one item copied exactly from the fixed list above>",\n'
    '  "justification": "<step-by-step explanation of why this move is best, referencing the concept>"\n'
    "}"
)

USER_PROMPT_TEMPLATE = """Position (FEN): {fen}
Best move (per engine): {san} ({uci})
Engine evaluation: {score}

Respond with the JSON object only."""


def save_result(record: dict, output_path: str):
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
        raise ValueError("JSON file must contain an array of FEN strings")
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
    parser = argparse.ArgumentParser(description="Stockfish-assisted concept identification")
    parser.add_argument("fen", nargs="*", help="FEN string(s) of position(s)")
    parser.add_argument("--file", default=None, help="Path to JSON file with a list of FEN strings")
    parser.add_argument("--stockfish-path", default=None, help="Path to stockfish binary")
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME, help="HF model name")
    parser.add_argument("--think-time", type=float, default=0.5, help="Seconds for Stockfish to think")
    parser.add_argument("--output", default="results_with_stockfish.json", help="Path to JSON results file")
    args = parser.parse_args()

    positions = load_positions(args)
    print(f"Loaded {len(positions)} position(s)")

    print(f"Loading model {args.model} (first run will download weights)...")
    model, tokenizer = load_model(args.model)

    for i, fen in enumerate(positions, 1):
        print(f"\n[{i}/{len(positions)}] FEN: {fen}")

        # Get Stockfish's best move
        print("  Asking Stockfish for the best move...")
        try:
            uci, san, score = get_best_move(fen, args.stockfish_path, args.think_time)
        except Exception as e:
            print(f"  ERROR: Stockfish failed: {e}")
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": args.model,
                "fen": fen,
                "mode": "with_stockfish",
                "stockfish_error": str(e),
            }
            save_result(record, args.output)
            continue

        print(f"  Stockfish says: {san} ({uci})  |  eval: {score}")

        # Ask model to explain the move
        user_prompt = USER_PROMPT_TEMPLATE.format(fen=fen, san=san, uci=uci, score=score)
        print("  Asking Qwen to identify the concept and justify the move...")
        raw_response = generate(model, tokenizer, SYSTEM_PROMPT, user_prompt)

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": args.model,
            "fen": fen,
            "mode": "with_stockfish",
            "stockfish_move_uci": uci,
            "stockfish_move_san": san,
            "stockfish_eval": score,
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
                "best_move_san": san,
                "concept": None,
                "justification": None,
                "parse_error": str(e),
                "raw_response": raw_response,
            })

        save_result(record, args.output)

        print("  " + "=" * 58)
        print(json.dumps(record, indent=2))
        print("  " + "=" * 58)

    print(f"\nAll results saved to {args.output}")


if __name__ == "__main__":
    main()


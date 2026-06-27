"""
without_stockfish_vision.py
---------------------
Flow: FEN -> Vision API (FEN + Board Image) -> JSON

Usage:
    cd Vision
    python without_stockfish_vision.py --file ../positions.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Add parent directory to path so we can import from common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import CHESS_CONCEPTS
from vlm_common import get_nvidia_key, get_base64_image_from_fen, vlm_generate, extract_json

DEFAULT_MODEL_NAME = "qwen/qwen3.5-397b-a17b"
CONCEPT_LIST_STR = ", ".join(CHESS_CONCEPTS)

SYSTEM_PROMPT = (
    "You are a master chess coach. You are provided with an image of a chessboard and its FEN string. "
    "Find the best move, identify the SINGLE underlying tactical or strategic concept from this "
    f"fixed list: [{CONCEPT_LIST_STR}], and justify why that move is correct based on what you see.\n\n"
    "You MUST respond with ONLY a valid JSON object, no markdown fences, no extra "
    "text before or after, in EXACTLY this shape:\n"
    "{\n"
    '  "best_move_san": "<move in standard algebraic notation, e.g. Nxe5, Qh5+, O-O>",\n'
    '  "concept": "<one item copied exactly from the fixed list above>",\n'
    '  "justification": "<step-by-step explanation of why this move is best, referencing the concept and the visual state of the board>"\n'
    "}"
)

USER_PROMPT_TEMPLATE = "Position (FEN): {fen}\n\nRespond with the JSON object only."


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
    parser = argparse.ArgumentParser(description="Vision API Move + Concept Identification")
    parser.add_argument("fen", nargs="*", help="FEN string(s) of position(s)")
    parser.add_argument("--file", default=None, help="Path to JSON file with a list of FEN strings")
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME, help="Model name for Vision API")
    parser.add_argument("--output", default="results_without_stockfish_vision.json", help="Path to JSON results")
    parser.add_argument("--api-key", default=None, help="NVIDIA API Key")
    args = parser.parse_args()

    positions = load_positions(args)
    print(f"Loaded {len(positions)} position(s)")

    api_key = get_nvidia_key(args.api_key)
    print(f"Connected to Vision API. Using model {args.model}.")

    for i, fen in enumerate(positions, 1):
        print(f"\n[{i}/{len(positions)}] FEN: {fen}")

        print("  Downloading board image...")
        try:
            b64_img = get_base64_image_from_fen(fen, i)
        except Exception as e:
            print(f"  ERROR: Failed to download image: {e}")
            continue

        user_prompt = USER_PROMPT_TEMPLATE.format(fen=fen)
        print("  Asking Vision API to find the move, concept, and justify it...")
        
        try:
            raw_response = vlm_generate(api_key, args.model, SYSTEM_PROMPT, user_prompt, b64_img)
        except Exception as e:
            print(f"  ERROR: API call failed: {e}")
            continue

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": args.model,
            "fen": fen,
            "mode": "without_stockfish_vision",
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

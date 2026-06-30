"""
Shared utilities for the chess+Qwen scripts.

Requirements:
    pip install python-chess transformers torch accelerate

You also need the stockfish ENGINE BINARY installed separately (it's not a
pip package). On most systems:
    macOS:   brew install stockfish
    Ubuntu:  sudo apt install stockfish
    Windows: download from https://stockfishchess.org/download/ and note the .exe path

By default this code looks for an executable named "stockfish" on your PATH.
Override with the STOCKFISH_PATH environment variable or --stockfish-path flag.
"""

import os
import chess
import chess.engine

DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"  # swap to Qwen2.5-3B-Instruct if you want


DEFAULT_STOCKFISH_PATH = os.path.join(
    os.path.expanduser("~"),
    "OneDrive", "Desktop", "stockfish",
    "stockfish-windows-x86-64-avx2.exe"
)


def get_best_move(fen: str, stockfish_path: str = None, think_time: float = 0.5):
    """
    Given a FEN, ask Stockfish for the best move.
    Returns (best_move_uci, best_move_san, score_str).
    """
    stockfish_path = stockfish_path or os.environ.get("STOCKFISH_PATH", DEFAULT_STOCKFISH_PATH)
    board = chess.Board(fen)

    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
        result = engine.play(board, chess.engine.Limit(time=think_time))
        best_move = result.move
        san = board.san(best_move)

        info = engine.analyse(board, chess.engine.Limit(time=think_time))
        score = info["score"].white()
        score_str = str(score)

    return best_move.uci(), san, score_str

def get_best_move_maia(fen: str, maia_model: str = "maia3-5m", think_time: float = 0.5):
    """
    Given a FEN, ask Maia3 for the best move.
    Returns (best_move_uci, best_move_san, score_str).
    """
    import sys
    maia_model = maia_model or "maia3-5m"
    board = chess.Board(fen)

    with chess.engine.SimpleEngine.popen_uci([
        sys.executable, "-m", "maia3.uci", 
        "--model", maia_model, 
        "--use-uci-history"
    ]) as engine:
        result = engine.play(board, chess.engine.Limit(nodes=1))
        best_move = result.move
        san = board.san(best_move)
        
        # Maia doesn't evaluate score like Stockfish, but we can query it
        info = engine.analyse(board, chess.engine.Limit(nodes=1))
        score = info.get("score")
        score_str = str(score.white()) if score else "0.00"

    return best_move.uci(), san, score_str


def load_model(model_name: str = DEFAULT_MODEL_NAME):
    """
    Loads a Qwen instruct model + tokenizer via Hugging Face transformers.
    Runs on CPU automatically if no GPU is available (1.5B/3B is fine on CPU).
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
    )
    return model, tokenizer


CHESS_CONCEPTS = [
    "advanced pawn", "attack on f2 or f7", "attraction", "back rank mate",
    "capture the defender", "castling", "collinear move", "discovered attack", 
    "double check", "en passant", "exposed king", "fork", "hanging piece",
    "kingside attack", "pin", "promotion", "sacrifice", "skewer", 
    "trapped piece", "clearance", "defensive move", "deflection", 
    "interference", "intermezzo", "overloading", "queenside attack",
    "quiet move", "smothered attack", "underpromotion", "x-ray", 
    "zugzwang",
]


def extract_json(text: str) -> dict:
    """
    Pulls the first {...} JSON object out of a model response, even if the
    model added extra prose or markdown fences around it.
    """
    import json
    import re

    # strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip()

    # find first { ... last } as a fallback if there's surrounding text
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in model output:\n{text}")

    candidate = text[start:end + 1]
    return json.loads(candidate)


def generate(model, tokenizer, system_prompt: str, user_prompt: str, max_new_tokens: int = 500):
    """
    Runs a chat-style generation using Qwen's chat template.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    output_ids = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
    )
    new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
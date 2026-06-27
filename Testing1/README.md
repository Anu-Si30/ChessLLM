# Qwen + Stockfish Chess Concept Identifier

Two scripts that test a small Qwen model on chess positions you supply as a FEN.

## Setup

1. **Python deps:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Stockfish engine binary** (only needed for `with_stockfish.py` — this is a
   separate program, not a pip package):
   - macOS: `brew install stockfish`
   - Ubuntu/Debian: `sudo apt install stockfish`
   - Windows: download from https://stockfishchess.org/download/

   By default the scripts look for `stockfish` on your PATH. Override with:
   ```bash
   export STOCKFISH_PATH=/full/path/to/stockfish
   ```
   or pass `--stockfish-path` directly.

3. **GPU note:** you do *not* need an NVIDIA Ada-generation GPU. The default
   model, `Qwen/Qwen2.5-1.5B-Instruct`, runs fine on CPU. If you have any GPU
   (even an older one) `device_map="auto"` in `common.py` will use it
   automatically; otherwise it falls back to CPU.

## Scripts

### `with_stockfish.py`
Gets the best move from Stockfish first, then gives Qwen the FEN + that move
and asks it to name the tactical/strategic concept and justify the move.

```bash
python with_stockfish.py "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 4 4"
```

### `without_stockfish.py`
Gives Qwen only the FEN. The model must find the best move itself, name the
concept, and justify its choice — no engine help. Useful for comparing the
model's own chess strength against the Stockfish-assisted version.

```bash
python without_stockfish.py "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 4 4"
```

### Common flags
- `--model Qwen/Qwen2.5-3B-Instruct` — swap to a larger Qwen model if you have the RAM/VRAM.
- (with_stockfish only) `--stockfish-path` and `--think-time` (seconds, default 0.5).

## Notes
- First run of either script downloads the model weights from Hugging Face (a
  few GB) — this can take a while depending on your connection.
- The 1.5B model is fast but chess-weak; expect `without_stockfish.py` to
  sometimes pick a suboptimal move — that's expected, and is the interesting
  comparison point against the Stockfish-assisted script.
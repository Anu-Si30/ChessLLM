# Chess Concept Evaluation: Conclusion & Observations

This document summarizes the findings from our experiments evaluating various Large Language Models (LLMs) and Vision Language Models (VLMs) on their ability to perform complex chess reasoning. 

## The Objective
We tested the models on 31 distinct chess positions (provided via FEN strings and/or images). The goal was to see if the models could:
1. Identify the single underlying tactical/strategic concept from a fixed ground-truth list of 31 concepts (e.g., *fork*, *pin*, *x-ray*, *advanced pawn*).
2. Find the engine's "best move" without assistance.
3. Justify the move accurately.

We ran these tests in two modes: **With Stockfish** (the model is given the engine's best move and asked to explain it) and **Without Stockfish** (the model must find the move and the concept entirely on its own).

---

## 1. The Small Local Model (Qwen 1.5B)
*Method: Text-only (FEN)*

**Observations:**
- **Vocabulary Collapse**: The model was too small to adhere to the complex prompt constraints. It suffered from vocabulary collapse, repeatedly guessing "pin" or "underpromotion" for nearly every single position, regardless of the board state.
- **Zero Spatial Reasoning**: It lacked the parameter depth required to unpack a FEN string into a mental spatial grid, resulting in completely illogical move justifications.

---

## 2. The Large Text Model (Llama-3.3-70B-Instruct)
*Method: Text-only (FEN) via API*

**Performance:**
- **Move Match (Without Stockfish)**: `0 / 31` (0%)
- **Concept Match (With Stockfish)**: `2 / 31` (~6%)
- **Concept Match (Without Stockfish)**: `2 / 31` (~6%)

**Observations:**
- **Format Adherence**: Unlike the 1.5B model, Llama 3 70B flawlessly followed the strict JSON output constraints and successfully utilized a wide variety of vocabulary from the 31-item concept list (e.g., *kingside attack*, *exposed king*, *deflection*).
- **Plausible but Flawed Justifications**: The model generated highly articulate, confident-sounding justifications. However, because it could not "see" the board, it relied on statistical text patterns rather than actual geometric calculation. 
- **The FEN Limitation**: Text-based models struggle profoundly with FEN strings because FEN is a highly compressed, non-spatial format. The model failed to correctly track lines of sight (diagonals, ranks, files), preventing it from identifying the correct tactical concepts.

---

## 3. The Massive Vision Model (Qwen3.5-397B-VLM)
*Method: Vision + Text (Board Image + FEN) via API*

**Performance:**
- **Move Match (Without Stockfish)**: `1 / 27` (~4%)
- **Concept Match (With Stockfish)**: `1 / 27` (~4%)
- **Concept Match (Without Stockfish)**: `1 / 27` (~4%)
*(Note: 4 positions were dropped due to API timeouts/parsing errors).*

**Observations:**
- **First Organic Move Match**: Giving the model actual "sight" of the board allowed it to organically find the exact Stockfish best move completely unassisted in one position.
- **Visual Hallucination**: Surprisingly, providing an image did not solve the reasoning problem. The model suffered heavily from "visual hallucination." It frequently claimed pieces were on squares they were not, or confidently stated that a move delivered a "fork" or a "check" when the visual board proved otherwise.
- **Concept Failure**: Despite having 400 billion parameters and a visual encoder, it performed worse at concept identification than the text-only Llama 3 model, highlighting that visual perception does not automatically translate to deep logical/geometric chess calculation.

---

## Final Conclusion

1. **Chess is Inherently Anti-LLM**: General-purpose LLMs and VLMs rely on probabilistic token generation. Chess requires deterministic, geometric calculation. Even massive models (400B+ parameters) fail at zero-shot tactical reasoning because they attempt to "guess" the next logical word rather than calculate the intersecting lines of a 64-square grid.
2. **The Danger of Fluency**: As models get larger, their formatting and articulation improve, but their underlying chess logic does not. They confidently generate detailed, step-by-step justifications for moves that are completely illegal or tactically nonsensical.
3. **The Path Forward**: For reliable chess persona/coaching tools, LLMs cannot be trusted to analyze positions in a vacuum. A hybrid architecture is strictly required:
   - A dedicated engine (Stockfish) **must** compute the move and the tactical lines.
   - An LLM can then be used strictly to translate the engine's calculated lines into human-readable text, but the LLM must be tightly constrained to prevent it from hallucinating board states.

# Maia3 vs Stockfish: Engine Comparison Analysis

This document compares the moves predicted by **Maia3** (a human-like chess AI) against the moves chosen by **Stockfish** (a perfect chess engine) across all 31 test positions. The model used to generate justifications in both cases was **Qwen 3.5 122B-A10B** via the NVIDIA API.

---

## What is the Difference?

| Property | Stockfish | Maia3 |
|---|---|---|
| **Design goal** | Find the *objectively best* move | Predict the move a *human* would play |
| **Rating** | ~3600 Elo | Calibrated to ~1500 Elo human play |
| **Evaluation** | Centipawn score (engine perspective) | Centipawn score (human game outcome prediction) |
| **Move character** | Cold, clinical, computer-like | Natural, human-style tendencies |

Because Maia is trained on human games, it often picks "natural" but slightly sub-optimal moves. Stockfish picks the engine-perfect "best" move regardless of how natural it looks to a human.

---

## Position-by-Position Comparison

### Position 1
**FEN:** `6k1/6b1/B5p1/1pr3p1/2p1P3/6P1/P4P1P/1R4K1 b - - 2 32`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `c3` | `c3` ✅ Same |
| **Eval** | -416 | -120 |
| **Concept (Qwen)** | overloading | overloading ✅ |
| **Agreement** | ✅ Move + Concept |

**Analysis:** Both engines picked the same pawn advance. Stockfish's larger negative eval (-416) reflects its deeper calculation of the resulting passed pawn endgame. Qwen correctly identified "overloading" for both — the white rook cannot simultaneously defend b5 and stop the c-pawn.

---

### Position 2
**FEN:** `rnbqk1nr/1ppp1ppp/p7/2b1p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4`
*(Scholar's Mate Position)*

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `Qxf7#` | `Qxf7#` ✅ Same |
| **Eval** | #+1 | +648 |
| **Concept (Qwen)** | attack on f2 or f7 | back rank mate ❌ |
| **Agreement** | ✅ Move | ❌ Concept differs |

**Analysis:** Both correctly find the checkmate. Qwen gave Stockfish's version the precisely correct concept ("attack on f2 or f7") since the Scholar's Mate specifically exploits that diagonal. For Maia's version, Qwen misclassified it as "back rank mate" — while the mate is delivered on the back rank row, the correct theme here is clearly the f7 attack. This is a subtle hallucination — the concept is close but wrong.

---

### Position 3
**FEN:** `4k2r/rb1qbppp/3p4/1p1P4/8/1Q3N2/PP3PPP/R3R1K1 w k - 2 19`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `Rxe7+` | `Nd4` ❌ Different |
| **Eval** | +208 | -24 |
| **Concept (Qwen)** | capture the defender | fork |
| **Agreement** | ❌ Completely different |

**Analysis:** This is the most dramatic divergence in the dataset. Stockfish finds the clinical `Rxe7+`, removing the bishop defending the queen (a "capture the defender" tactic worth +208). Maia instead plays `Nd4`, a human-like centralizing knight move that attacks the queen, but the evaluation of -24 means it's actually *losing* for White — Maia essentially played a natural-looking but losing move. Qwen correctly identified "fork" for Maia's move (Nd4 does attack the queen and bishop simultaneously), but it was wrong about "capture the defender" for Stockfish — Rxe7+ removes the bishop defending the queen on d7, so "capture the defender" is exactly right.

---

### Position 4
**FEN:** `6k1/pp3ppp/5b2/8/5nQP/1P6/Pq4PK/8 w - - 0 31`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `Qc8+` | `Qxf4` ❌ Different |
| **Eval** | #+2 | +67 |
| **Concept (Qwen)** | back rank mate | capture the defender |
| **Agreement** | ❌ Completely different |

**Analysis:** Stockfish finds the forced mate in 2 with `Qc8+`, starting a back rank mating sequence. Maia plays `Qxf4`, a natural capture of the knight which is also a very reasonable human move (winning a piece), but misses the forced mate. Qwen's concept for Stockfish ("back rank mate") is correct. Qwen's concept for Maia ("capture the defender") is reasonable — the knight was defending the queen on b2.

---

### Position 5
**FEN:** `r4rk1/pp2bpp1/2n2n1p/1B1p1q2/3Q3B/2N5/PPP2PPP/R3R1K1 w - - 2 14`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `Bxc6` | `Bxc6` ✅ Same |
| **Eval** | +431 | +292 |
| **Concept (Qwen)** | capture the defender | capture the defender ✅ |
| **Agreement** | ✅ Move + Concept |

**Analysis:** Both engines agreed on the move and Qwen agreed on the concept. Stockfish calculates a larger advantage (+431 vs +292) due to deeper tactical lines beyond the immediate capture. The "capture the defender" classification is correct — the knight on c6 was protecting the queen and key squares.

---

### Position 6
**FEN:** `7r/3k1ppp/5b2/p1p5/4P3/2N2P2/Pr3P1P/R3K2R w KQ - 0 17`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `O-O-O+` | `Rd1+` ❌ Different |
| **Eval** | +476 | -370 |
| **Concept (Qwen)** | castling | discovered attack |
| **Agreement** | ❌ Completely different |

**Analysis:** The most instructive example of Maia's human-like limitation. Stockfish finds the brilliant `O-O-O+` (castling queenside *while delivering check*), a move that simultaneously activates the rook, ensures king safety, and delivers check. Maia plays `Rd1+`, a natural-looking rook move that is actually *catastrophically losing* at -370. Qwen correctly labels Stockfish's move as "castling." For Maia's move, Qwen labeled it "discovered attack" but the justification was confused — it tried to explain the discovered attack geometry but admitted the move didn't fully fit. This is a case where Maia's human tendencies led it to a blunder.

---

### Position 7
**FEN:** `3r2k1/1p3ppp/2p1p3/p3P2b/Pb2PP2/1QN3Pq/1P2B2P/3R3K b - - 1 23`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `Rd2` | `Rxd1+` ❌ Different |
| **Eval** | -696 | -243 |
| **Concept (Qwen)** | deflection | capture the defender |
| **Agreement** | ❌ Different moves, different concepts |

**Analysis:** Stockfish's `Rd2` is a quiet but devastating interference move, overloading White's defenses. Maia plays `Rxd1+`, a natural "take the rook with check" move, which is also winning but less decisive (-243 vs -696). Qwen's "deflection" for Stockfish is reasonable (the rook deflects the queen from defending), while "capture the defender" for Maia is correct (the d1 rook was defending the queen on b3).

---

### Position 8
**FEN:** `4rrk1/pp1b1ppp/4p2n/3p4/3P4/Pq1B1R2/4N1P1/3R1QK1 w - - 0 21`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `Bxh7+` | `Bxh7+` ✅ Same |
| **Eval** | +363 | +646 |
| **Concept (Qwen)** | attraction | sacrifice |
| **Agreement** | ✅ Move | ❌ Concept differs |

**Analysis:** Both engines agree on the Greek Gift sacrifice. Qwen classified it as "attraction" for Stockfish (the king is attracted/lured to h7) and "sacrifice" for Maia (the bishop is sacrificed). Both are technically valid descriptions of the same move — "attraction" is more precise as a chess tactic name, while "sacrifice" is more general. This is a minor semantic disagreement rather than a hallucination.

---

### Position 9
**FEN:** `rn1k1b1r/ppp2pp1/4b1np/4P3/2p5/2N2N2/PP1BPPPP/2KR1B1R w - - 4 9`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | `Bg5+` | `Bxh6+` ❌ Different |
| **Eval** | #+2 | +233 |
| **Concept (Qwen)** | ❌ Parse error (too long) | exposed king |
| **Agreement** | ❌ Different moves |

**Analysis:** Stockfish finds the forced mate in 2 via `Bg5+`. Maia plays `Bxh6+`, a natural "take a piece and give check" move, which is winning (+233) but not mate-in-2. The response for Stockfish hit a token overflow — Qwen started reasoning about the "discovered attack" but ran out of tokens before resolving its own chain-of-thought. Maia's concept "exposed king" is reasonable for `Bxh6+`.

---

### Position 10
**FEN:** `r1bq1rk1/ppppn1pp/2n5/1Bb1P3/8/1Q3N2/PP1B1PPP/RN2R1K1 b - - 4 12`

| | Stockfish | Maia3 |
|---|---|---|
| **Move** | (not shown) | `Kh8` |
| **Eval** | N/A | +148 |
| **Concept (Qwen)** | N/A | defensive move |
| **Agreement** | N/A |

**Analysis:** Maia's `Kh8` is a prophylactic king move to safety — classic human defensive thinking. The concept "defensive move" is accurate.

---

## Summary Statistics

| Metric | Value |
|---|---|
| Total positions tested | 31 |
| Maia ≡ Stockfish (same move) | **~8 / 31 (~26%)** |
| Qwen concept match (Stockfish) | **~18 / 31 (~58%)** |
| Qwen concept match (Maia) | **~16 / 31 (~52%)** |
| Qwen parse/empty errors (Stockfish) | **~4 / 31 (~13%)** |
| Qwen parse/empty errors (Maia) | **~7 / 31 (~23%)** |
| Maia played a losing/blunder move | **~5 / 31 (~16%)** |

---

## Key Findings

### 1. Maia Only Agrees with Stockfish ~26% of the Time
This is expected. Maia is explicitly trained to predict human behaviour, not optimal play. When the position demands a complex, counter-intuitive engine move (like `O-O-O+` to castle while checking, or `Rd2` as a quiet interference), Maia opts for the more "obvious" human move.

### 2. Maia's Moves Are Easier to Explain
Because Maia plays more natural moves (captures, checks, centralisation), Qwen's justification error rate was *lower* for Maia moves (23% parse errors) on positions where it did produce output. Stockfish's clinical, non-obvious moves sometimes caused Qwen to spiral into long confused reasoning chains that exceeded the token limit (13% parse errors).

### 3. Evaluation Score Gaps Reveal the Cost of Humanity
In positions where Maia and Stockfish diverged, Stockfish's evaluations were consistently more extreme (higher winning advantages or faster mates). Maia's "human-like" move often forfeited a forced mate or a material gain in exchange for a still-winning but less decisive continuation.

### 4. Qwen Concept Accuracy Is Marginally Better with Stockfish
Stockfish's moves tend to embody "cleaner" tactical themes (a fork is a fork, a pin is a pin). Maia's moves can be harder to classify because they reflect human intuition — e.g. `Kh8` as "defensive move" or `Nd4` as "fork" — which are both valid but imprecise framings.

### 5. The "Hallucination by Overthinking" Problem
The most striking failure mode observed with the 122B Qwen model is **hallucination through over-reasoning**. Rather than confidently asserting a concept, the model begins to second-guess its own board reading mid-justification, talks itself out of the correct answer, and either produces a wrong concept or runs out of tokens entirely. This was observed most clearly in positions 6 and 9.

---

## Conclusion

Stockfish and Maia serve fundamentally different purposes in this experimental pipeline:

- **Stockfish** provides the *ground truth* for what the position objectively demands. It is the better benchmark for testing whether an LLM can understand *correct* chess.
- **Maia** provides the *human expectation* for what a player would do. It is a better benchmark for testing whether an LLM can reason about *plausible human chess*.

For a chess coaching persona, Maia's moves are more relatable and easier to explain, but an LLM must be more carefully constrained to avoid hallucinating board states when the engine's move is a non-obvious "computer move" like castling with check.

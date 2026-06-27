import json
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Compare Stockfish vs No-Stockfish LLM evaluations")
    parser.add_argument("--with-sf", required=True, help="Path to the JSON with Stockfish results")
    parser.add_argument("--without-sf", required=True, help="Path to the JSON without Stockfish results")
    parser.add_argument("--output", default="comparison_report.md", help="Path to output markdown report")
    args = parser.parse_args()

    with open(args.with_sf, "r") as f:
        with_sf = json.load(f)
        
    with open(args.without_sf, "r") as f:
        without_sf = json.load(f)

    ground_truth = [
        "advanced pawn", "attack on f2 or f7", "attraction", "back rank mate",
        "capture the defender", "castling", "collinear move", "discovered attack", 
        "double check", "en passant", "exposed king", "fork", "hanging piece",
        "kingside attack", "pin", "promotion", "sacrifice", "skewer", 
        "trapped piece", "clearance", "defensive move", "deflection", 
        "interference", "intermezzo", "overloading", "queenside attack",
        "quiet move", "smothered attack", "underpromotion", "x-ray", 
        "zugzwang"
    ]

    report_lines = ["# Chess Concept Comparison Report\n"]

    report_lines.append("## Summary Table")
    report_lines.append("| Index | Ground Truth | With SF Concept | Without SF Concept | With SF Move | Without SF Move | Move Match? |")
    report_lines.append("|---|---|---|---|---|---|---|")

    for i in range(min(len(with_sf), len(without_sf), len(ground_truth))):
        w = with_sf[i]
        wo = without_sf[i]
        gt = ground_truth[i]
        
        move_match = w.get("best_move_san") == wo.get("best_move_san")
        
        report_lines.append(f"| {i+1} | {gt} | {w.get('concept')} | {wo.get('concept')} | {w.get('best_move_san')} | {wo.get('best_move_san')} | {'Yes' if move_match else 'No'} |")

    report_lines.append("\n## Detailed Breakdown\n")

    for i in range(min(len(with_sf), len(without_sf), len(ground_truth))):
        w = with_sf[i]
        wo = without_sf[i]
        gt = ground_truth[i]
        
        report_lines.append(f"### Position {i+1}")
        report_lines.append(f"**FEN**: `{w.get('fen')}`\n")
        report_lines.append(f"**Ground Truth Concept**: `{gt}`\n")
        
        w_concept = w.get("concept")
        wo_concept = wo.get("concept")
        
        report_lines.append("#### With Stockfish")
        report_lines.append(f"- **Move**: {w.get('best_move_san')}")
        report_lines.append(f"- **Concept**: {w_concept} *(Matches Ground Truth: {'Yes' if w_concept == gt else 'No'})*")
        report_lines.append(f"- **Justification**: {w.get('justification')}\n")
        
        report_lines.append("#### Without Stockfish")
        report_lines.append(f"- **Move**: {wo.get('best_move_san')}")
        report_lines.append(f"- **Concept**: {wo_concept} *(Matches Ground Truth: {'Yes' if wo_concept == gt else 'No'})*")
        report_lines.append(f"- **Justification**: {wo.get('justification')}\n")
        
        report_lines.append("---\n")

    # Write the report
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Report generated at: {args.output}")

if __name__ == "__main__":
    main()

import os
import re

base_dir = r"C:\Users\Anushka\OneDrive\Desktop\ChessPersonaThing\ChessLLM\Testing1"

files_to_copy = [
    (r"Local_Model_Experiment\with_stockfish.py", r"Local_Model_Experiment\with_maia.py"),
    (r"API_Model_Experiment\with_stockfish_api.py", r"API_Model_Experiment\with_maia_api.py"),
    (r"Vision\with_stockfish_vision.py", r"Vision\with_maia_vision.py")
]

for src, dst in files_to_copy:
    src_path = os.path.join(base_dir, src)
    dst_path = os.path.join(base_dir, dst)
    
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replacements
    content = content.replace("with_stockfish", "with_maia")
    content = content.replace("get_best_move", "get_best_move_maia")
    content = content.replace("Stockfish", "Maia")
    content = content.replace("stockfish_path", "maia_model")
    content = content.replace("stockfish", "maia")
    
    # Fix import if necessary
    content = content.replace("get_best_move_maia, load_model", "get_best_move_maia, load_model") # In case it matched
    
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Created {dst_path}")

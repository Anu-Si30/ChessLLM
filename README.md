# ChessLLM - Chess Concept Evaluation

This project evaluates different Large Language Models (LLMs) and Vision Language Models (VLMs) on their ability to perform complex chess reasoning. Specifically, it tests whether they can correctly identify tactical concepts and justify the best moves in various board positions.

## Folder Structure

The main codebase is located in the `Testing1` folder, which contains:

- **`Local_Model_Experiment/`**: Scripts for testing local HuggingFace models (e.g., Qwen 1.5B).
- **`API_Model_Experiment/`**: Scripts for testing large text-based API models (e.g., Llama-3 70B, Gemini).
- **`Vision/`**: Scripts for testing Vision Language Models (VLMs) by providing them with images of the chessboard alongside the FEN string.
- **`positions.json`**: A dataset containing 31 carefully selected chess positions (as FEN strings) and their corresponding ground-truth tactical concepts (e.g., *fork*, *pin*, *x-ray*). The models are evaluated against this file.
- **`conclusion.md`**: Contains detailed analysis and conclusions drawn from running these experiments.

## How it Works

The evaluation scripts iterate through the chess positions defined in `positions.json`. For each position, the script prompts the model to:
1. Identify the underlying tactical concept from a predefined list of 31 concepts.
2. Find the best move (if not provided by an engine).
3. Generate a textual justification for the move.

You can run tests in two primary modes:
- **With Stockfish**: The script first uses the Stockfish engine to compute the objectively best move, and then passes this move to the LLM. The LLM's only job is to correctly identify the concept and explain the move.
- **Without Stockfish**: The LLM must find the best move, name the concept, and justify its choice entirely on its own.

## Running the Evaluation

1. **Install Dependencies:**
   ```bash
   pip install -r Testing1/requirements.txt
   ```

2. **Run an Experiment:**
   Navigate into the experiment folder you want to run. For example, to run the API text model experiment with Stockfish assistance:
   ```bash
   cd Testing1/API_Model_Experiment
   python with_stockfish_api.py
   ```
   *(This will read `../positions.json` and generate an output file like `results_with_stockfish_llama3.json` containing the model's responses)*.

## API Configuration

If you are running models via an API (in the `API_Model_Experiment` or `Vision` folders), you must provide your own API keys.

**⚠️ Security Note:** Your API keys should NEVER be committed to GitHub. The repository includes a `.gitignore` that is configured to ignore files like `api_keys.json` and `.env`.

### Where to add your API Keys

The easiest way to provide your API keys is to create a file named `api_keys.json` inside the `Testing1/` folder. The scripts are hardcoded to look for this file. 

Create `Testing1/api_keys.json` and add your keys in the following JSON format (add or remove providers as needed):

```json
{
    "NVIDIA": "your-nvidia-api-key-here",
    "OPENAI": "your-openai-api-key-here",
    "GOOGLE": "your-google-api-key-here"
}
```

Alternatively, you can provide the keys via environment variables (e.g., `NVIDIA_API_KEY="your-key"`) or as a CLI argument (`--api-key "your-key"`), depending on the specific script being run.
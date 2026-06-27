import os
import json
import re
import base64
import requests
import urllib.parse

def load_api_keys(filepath="../api_keys.json"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def get_nvidia_key(api_key: str = None):
    key = api_key
    if not key:
        keys_config = load_api_keys()
        key = keys_config.get("NVIDIA")
        
    if not key:
        key = os.environ.get("NVIDIA_API_KEY")
        
    if not key:
        raise ValueError("NVIDIA API key not found. Please add 'NVIDIA': 'your-key' to ../api_keys.json, set the NVIDIA_API_KEY env var, or pass --api-key.")
    return key

def get_base64_image_from_fen(fen: str, index: int = None) -> str:
    """
    Downloads an image of the chessboard from backscattering.de API and returns it as a base64 string.
    This avoids needing local drawing libraries like cairosvg.
    """
    url_fen = urllib.parse.quote(fen)
    url = f"https://backscattering.de/web-boardimage/board.png?fen={url_fen}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image for FEN: {response.status_code} {response.text}")
    
    # Save the image locally so you can visually verify it
    os.makedirs("images", exist_ok=True)
    filename = f"position_{index}.png" if index else "temp_board.png"
    filepath = os.path.join("images", filename)
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    return base64.b64encode(response.content).decode("utf-8")

def vlm_generate(api_key: str, model_name: str, system_prompt: str, user_prompt: str, b64_image: str) -> str:
    """
    Runs a chat generation using the NVIDIA VLM API.
    """
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
      "Authorization": f"Bearer {api_key}",
      "Accept": "application/json"
    }

    payload = {
      "model": model_name,
      "messages": [
          {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": f"{system_prompt}\n\n{user_prompt}"
                  },
                  {
                      "type": "image_url",
                      "image_url": {
                          "url": f"data:image/png;base64,{b64_image}"
                      }
                  }
              ]
          }
      ],
      "max_tokens": 1024,
      "temperature": 0.2,
      "top_p": 0.7,
      "stream": False
    }

    response = requests.post(invoke_url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code} {response.text}")
    
    data = response.json()
    return data["choices"][0]["message"]["content"]

def extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in model output:\n{text}")

    candidate = text[start:end + 1]
    return json.loads(candidate)

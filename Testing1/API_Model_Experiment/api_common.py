import os
import json
import re
from openai import OpenAI

def load_api_keys(filepath="api_keys.json"):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def get_openai_client(api_key: str = None, provider: str = "NVIDIA"):
    # Priority: 1. CLI arg, 2. api_keys.json, 3. Environment Variable
    key = api_key
    if not key:
        keys_config = load_api_keys()
        key = keys_config.get(provider)
        
    if not key:
        env_var_name = f"{provider.upper()}_API_KEY"
        key = os.environ.get(env_var_name)
        
    if not key:
        raise ValueError(f"API key for {provider} not found. Please add '{provider}': 'your-key' to api_keys.json, set the {provider.upper()}_API_KEY env var, or pass --api-key.")
    
    # Configure base_url based on the provider
    base_url = None
    if provider.upper() == "NVIDIA":
        base_url = "https://integrate.api.nvidia.com/v1"
    
    return OpenAI(
        base_url=base_url,
        api_key=key
    )

def api_generate(client, model_name: str, system_prompt: str, user_prompt: str) -> str:
    """
    Runs a chat generation using the OpenAI-compatible API.
    """
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=False
    )
    return completion.choices[0].message.content

def extract_json(text: str) -> dict:
    """
    Pulls the first {...} JSON object out of a model response, even if the
    model added extra prose or markdown fences around it.
    """
    if not text:
        raise ValueError("Model returned empty or None response")

    # strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip()

    # find first { ... last } as a fallback if there's surrounding text
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in model output:\n{text}")

    candidate = text[start:end + 1]
    return json.loads(candidate)

# backend/utils/openai_utils.py

import os
import openai
from flask import current_app
from .cache import cache_response

def initialize_openai_client():
    """
    Initializes the OpenAI client using the API key from environment variables.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    openai.api_key = api_key  # Set the API key directly

def replace_curly_quotes(text):
    """
    Replace curly quotes with straight quotes.
    """
    return text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

def get_openai_completion(prompt: str, model: str = "gpt-4", max_tokens: int = 1500, temperature: float = 0.0, stop=None) -> str:
    """
    Use OpenAI API to get a completion based on the provided prompt.
    Implements caching to reduce redundant API calls.

    Parameters:
    - prompt (str): The input prompt for the model.
    - model (str): The model to use for completion (default is "gpt-4").
    - max_tokens (int): The maximum number of tokens to generate (default is 1500).
    - temperature (float): Sampling temperature (default is 0.0).
    - stop (Optional[List[str]]): Sequences where the API will stop generating further tokens (default is None).

    Returns:
    - str: The generated completion text.
    """
    prompt = replace_curly_quotes(prompt)
    cached_response = cache_response.get(prompt)
    if cached_response:
        return cached_response
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop
        )
        content = response['choices'][0]['message']['content'].strip()
        cache_response.set(prompt, content)
        return content
    except Exception as e:
        current_app.logger.error(f"OpenAI API Error: {e}")
        raise e

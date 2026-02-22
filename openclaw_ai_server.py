#!/usr/bin/env python3
"""
OpenClaw AI Server: Exposes an HTTP endpoint for text generation.
The lead automation app can call this when ai.provider = 'openclaw'.
Uses the same OpenRouter model as the assistant.
"""
from flask import Flask, request, jsonify
import os
import yaml
from openai import OpenAI

app = Flask(__name__)

# Load config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Use OpenRouter API (optional: if no key, return placeholder)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
MODEL = config['ai'].get('model', 'meta-llama/llama-3.1-8b-instruct:free')
BASE_URL = os.getenv('AI_BASE_URL', config['ai'].get('base_url', 'https://openrouter.ai/api/v1'))

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=BASE_URL)

@app.route('/generate', methods=['POST'])
def generate():
    """
    Expected JSON: {
        "prompt": "user prompt",
        "system": "system prompt (optional)",
        "max_tokens": 200,
        "temperature": 0.7
    }
    Returns: { "text": "generated text" }
    """
    data = request.get_json()
    prompt = data.get('prompt', '')
    system = data.get('system', 'You are a helpful assistant.')
    max_tokens = data.get('max_tokens', 200)
    temperature = data.get('temperature', 0.7)

    if not prompt:
        return jsonify({'error': 'prompt required'}), 400

    # If no API key, return placeholder
    if not OPENROUTER_API_KEY:
        return jsonify({'text': f"[DEMO] This is a placeholder email for '{prompt}'. Set OPENROUTER_API_KEY to enable real AI generation."})

    try:
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=BASE_URL)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        text = response.choices[0].message.content.strip()
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)

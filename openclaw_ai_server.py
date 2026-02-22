#!/usr/bin/env python3
"""
OpenClaw AI Server: Exposes an HTTP endpoint for text generation.
The lead automation app can call this when ai.provider = 'openclaw'.
Uses OpenRouter API to generate text.
"""
from flask import Flask, request, jsonify
import os
import yaml
import requests

app = Flask(__name__)

# Load config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Use OpenRouter API (optional: if no key, return placeholder)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
MODEL = config['ai'].get('model', 'meta-llama/llama-3.1-8b-instruct:free')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

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
        resp = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        text = data['choices'][0]['message']['content'].strip()
        return jsonify({'text': text})
    except requests.HTTPError as e:
        return jsonify({'error': f"OpenRouter error: {e.response.status_code} {e.response.text}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)

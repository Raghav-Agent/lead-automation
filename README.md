# Lead Automation System

An AI-driven pipeline: find leads → email → detect replies → build prototype → continue conversation.

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys and email credentials.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   python db.py
   ```
4. Configure `config.yaml` for your niche, email provider, and intervals.

## Running

- **One-off cycle**: `python main.py` (runs all steps once, then starts scheduler)
- **Test individual modules**:
  - `python lead_finder.py`
  - `python emailer.py`
  - `python reply_monitor.py`
  - `python prototype.py`
  - `python conversation.py`

## Notes

- Lead finding uses a simple Brave search scraper; for production, use Brave Search API or similar.
- Email sending uses SMTP; consider SendGrid or Mailgun for higher volume.
- Reply monitoring checks Gmail IMAP; adjust labels/folders as needed.
- Prototype generator creates a simple static HTML page under `static/`.
- Conversation uses OpenAI API; you can swap for any LLM.

## Docker (optional)

A Dockerfile can be added to run this as a container. Let me know if you want it.

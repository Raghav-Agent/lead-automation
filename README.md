# Lead Automation System

An AI-driven pipeline: find leads → email → detect replies → build prototype → continue conversation.

## New: Sales Campaigns

You can now run targeted sales campaigns by niche and location:
- Example: “Send email to dentists near me”
- Uses Google Places API to find businesses
- Enriches emails via Hunter.io
- Sends AI-personalized sales pitch with service options
- Track replies and continue conversation

## Setup (Free Tier)

1. Copy `.env.example` to `.env` and fill in your keys/credentials.
   - **AI** (choose one):
     - Local (free): Install [Ollama](https://ollama.ai), run `ollama pull llama3:8b`, set `ai.provider: ollama` in `config.yaml`. No API key needed.
     - Groq (free tier): Set `ai.provider: groq`, get API key from https://console.groq.com, set `GROQ_API_KEY` in `.env`.
     - OpenAI (paid): Set `ai.provider: openai`, set `OPENAI_API_KEY`.
   - **Email sending**:
     - Gmail (free): Enable 2FA, create app password, set `SMTP_PASSWORD`, keep `email.smtp_server=smtp.gmail.com`.
     - SendGrid (free tier 100/day): Set `SENDGRID_API_KEY` and change `email.smtp_server` to `smtp.sendgrid.net`, `email.smtp_port=587`, `email.from_address` your verified sender.
   - **Reply monitoring** (optional): Gmail IMAP settings (`IMAP_SERVER`, `IMAP_USER`, `IMAP_PASSWORD`).
   - **Places search** (free):
     - Yelp Fusion (5000/day): Set `places.provider: yelp`, get API key from https://www.yelp.com/developers, set `YELP_API_KEY`.
     - OpenStreetMap Nominatim (free, rate-limited): Set `places.provider: osm`, no key needed. Be respectful (1 req/s).
   - **Email enrichment** (free):
     - Pattern guessing (default): `enrich.method: pattern` (no key).
     - Scrape websites: `enrich.method: scrape` (no key, but may break on some sites).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   python db.py
   ```
4. Edit `config.yaml` to set your niche, intervals, and provider choices.

## Running

- **One-off cycle**: `python main.py` (runs all steps once, then starts scheduler)
- **Test individual modules**:
  - `python lead_finder.py`
  - `python emailer.py`
  - `python reply_monitor.py`
  - `python prototype.py`
  - `python conversation.py`
  - `python sales.py "dentist" "New York, NY"` – run a sales campaign directly
- **Web dashboard**: `python server.py` then open http://localhost:8000
  - Dashboard shows leads and prototypes
  - Admin endpoints:
    - `GET /admin/run/find_leads`
    - `GET /admin/run/email_leads`
    - `GET /admin/run/check_replies`
    - `GET /admin/run/build_prototypes`
    - `GET /admin/run/converse`
    - `POST /admin/sales` with JSON `{ "niche": "dentist", "location": "New York, NY" }`
    - `GET /admin/create_test_lead`
    - `GET /admin/reset`

## Docker

```bash
sudo docker-compose up -d
```
Container runs Flask on port 8000. Set environment variables in `docker-compose.yml`.

## Notes

- Lead finding uses Brave search scraper or Brave Search API (set `BRAVE_API_KEY`).
- Google Places API requires a key with Places enabled.
- Hunter.io API has rate limits; use judiciously.
- Email sending uses SMTP; consider transactional email service for high volume.
- Reply monitoring checks Gmail IMAP; adjust labels/folders as needed.
- Prototype generator creates a simple static HTML page under `static/`.
- Conversation uses OpenAI API; you can swap for any LLM.

## Cost & Rate Limits

- Google Places: $0.017 per request (textsearch) + others; set budget.
- Hunter.io: free tier 25 searches/month.
- OpenAI: per-token costs; monitor usage.
- SMTP: your provider’s limits.


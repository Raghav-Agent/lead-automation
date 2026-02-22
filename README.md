# Lead Automation System

An AI-driven pipeline: find leads → email → detect replies → build prototype → continue conversation.

## New: Sales Campaigns

You can now run targeted sales campaigns by niche and location:
- Example: “Send email to dentists near me”
- Uses Google Places API to find businesses
- Enriches emails via Hunter.io
- Sends AI-personalized sales pitch with service options
- Track replies and continue conversation

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys and email credentials.
   - Required for sales: `GOOGLE_PLACES_API_KEY`, `HUNTER_API_KEY`
   - Required for emails: `OPENAI_API_KEY`, `SMTP_PASSWORD` (or SendGrid)
   - Required for reply monitoring: `IMAP_SERVER`, `IMAP_USER`, `IMAP_PASSWORD`
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


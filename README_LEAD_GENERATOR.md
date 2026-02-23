# Autonomous Lead Generator

An AI-powered lead generation system that searches for businesses, enriches contact info, builds prototype websites, and sends pitch emails.

## Features

- **Lead Search**: Uses OpenStreetMap (OSM) and Brave Search to find businesses by niche and location.
- **Enrichment**: Scrapes websites (with Playwright fallback) and search snippets to find real emails and phone numbers.
- **Dashboard**: FastAPI backend with React frontend to manage leads, create websites, and send emails.
- **Website Builder**: Generates custom static HTML sites per lead using templates.
- **Email Campaigns**: Sends personalized pitch emails with website previews.

## Project Structure

```
lead-automation/
├── backend/
│   ├── agents/
│   │   ├── lead_searcher.py
│   │   ├── email_generator.py
│   │   └── website_builder.py
│   ├── models/
│   │   └── lead.py
│   ├── services/
│   │   └── database.py
│   ├── config.py
│   ├── main.py
│   ├── migrate_db.py
│   ├── update_existing_leads.py
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── SearchLeads.tsx
│   │   │   └── LeadDetails.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── index.html
├── templates/ (optional)
├── generated_sites/ (output)
├── leads.db (SQLite)
├── config.yaml
├── lead_finder.py
├── enrichment_agent.py
├── prototype.py
└── server.py (legacy Flask)
```

## Setup

1. **Python environment** (already set up in `venv/`):
   ```bash
   source venv/bin/activate
   pip install -r backend/requirements.txt  # if separate
   ```

2. **Environment variables**:
   Copy `backend/.env.example` to `backend/.env` and fill in:
   - `BRAVE_API_KEY` (for search snippets)
   - `SMTP_SERVER`, `SENDER_EMAIL`, `SENDER_PASSWORD` (for sending emails)
   - Optional: `OPENAI_API_KEY` if you want LLM-based content generation later.

3. **Database migration**:
   The backend uses the existing `leads.db`. Run migrations to add new columns:
   ```bash
   python backend/migrate_db.py
   python backend/update_existing_leads.py
   ```

4. **Start backend**:
   ```bash
   cd backend
   python main.py
   ```
   API runs at http://localhost:8000

5. **Start frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend runs at http://localhost:5173

## Usage

- **Search Leads**: Navigate to `/search`, enter niche and location. The system runs OSM + Brave search and saves leads.
- **Dashboard**: View all leads, see stats, and take actions.
- **Create Website**: Click “Create” to generate a static site for a lead. The site is served at `http://localhost:8000/sites/<id>.html`.
- **Send Email**: Click “Send Email” to dispatch a personalized pitch with website preview.

## API Endpoints

- `GET /api/health`
- `POST /api/leads/search` (async)
- `GET /api/leads`
- `GET /api/leads/{id}`
- `PUT /api/leads/{id}`
- `DELETE /api/leads/{id}`
- `POST /api/websites/create/{lead_id}`
- `GET /api/websites/{lead_id}`
- `POST /api/emails/send/{lead_id}`
- `GET /api/emails/{lead_id}`
- `GET /api/dashboard/stats`

## Notes

- The enrichment agent uses Playwright for JavaScript-heavy sites. Ensure `playwright install chromium` has been run.
- For best email deliverability, use a real SMTP service (e.g., Gmail app password or SendGrid).
- The website builder uses simple templates; you can extend `backend/agents/website_builder.py` with more designs or LLM-generated content.

# Trim. — URL Shortener

A full-stack URL shortener with click analytics. The **FastAPI** backend handles shortening, redirects, and telemetry; the **React** frontend provides a clean UI for creating links and viewing metrics.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Uvicorn |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| Cache | Redis (simulated locally via fakeredis) |
| Database | SQLite |
| Frontend | React, Vite |

## Project Structure

```
URLshortener/
├── main.py          # FastAPI routes
├── models.py        # SQLAlchemy models
├── readme.md
└── frontend/        # React UI
    ├── src/App.jsx
    └── ...
```

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Bharathbenny/URLshortener.git
cd URLshortener
```

### 2. Backend setup

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies and start the API server:

```bash
pip install fastapi uvicorn sqlalchemy fakeredis pydantic
uvicorn main:app --reload
```

The backend runs at **http://127.0.0.1:8000**.

### 3. Frontend setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs at **http://localhost:5173** and talks to the backend at `http://localhost:8000`.

## API Endpoints

Interactive docs are available at **http://127.0.0.1:8000/docs**.

### Create a short link — `POST /shorten`

With a custom alias:

```json
{
  "long_url": "https://github.com/bharath-code",
  "custom_alias": "my-portfolio"
}
```

Auto-generated short code:

```json
{
  "long_url": "https://wikipedia.org"
}
```

### Redirect — `GET /{short_code}`

Looks up the short code (cache-first), logs click analytics, and returns an HTTP 302 redirect.

### Analytics — `GET /analytics/{short_code}`

```json
{
  "short_code": "my-portfolio",
  "destination_url": "https://github.com/Bharathbenny",
  "total_clicks": 2,
  "click_history": [
    {
      "clicked_at": "2026-05-19T10:12:34.567890",
      "device_signature": "Mozilla/5.0 ..."
    }
  ]
}
```

## System Design

### Base62 encoding

Instead of random strings (which require collision checks), default links use an auto-incrementing integer ID converted to Base62 (`a-z`, `A-Z`, `0-9`). Each link gets a guaranteed unique mapping with no extra database lookups.

### Cache-aside pattern

Redirects check **fakeredis** first. On a cache hit, the long URL is returned from memory and SQLite is skipped. On a miss, the URL is read from SQLite, cached with a 1-hour TTL, and the click is logged. Subsequent requests become fast cache hits.

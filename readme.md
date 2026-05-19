Tech Stack & Dependencies
Core Framework: FastAPI (Asynchronous Server Gateway Interface)

ASGI Server: Uvicorn

Object-Relational Mapper: SQLAlchemy Core

Data Validation Engine: Pydantic v2

Caching Layer: Redis (Simulated locally via fakeredis for light, zero-dependency environment setups)

Database Driver: Built-in SQLite

Installation & Setup
Follow these steps to run the complete environment locally on your machine.

1. Clone the Repository
Bash
git clone [https://github.com/Bharathbenny/URLshortener.git](https://github.com/Bharathbenny/URLshortener.git)
cd URLshortener
2. Set Up a Virtual Environment (Recommended)
Bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Bash
pip install fastapi uvicorn sqlalchemy fakeredis pydantic
4. Fire Up the Production Server
Bash
uvicorn main:app --reload
Once the server process boots completely, the backend application will be accessible at http://127.0.0.1:8000.

Interactive API Documentation & Testing
This project leverages FastAPI's automated OpenAPI compilation. To test the system lifecycles without writing any frontend code or using external client tools like Postman:

Open your web browser and navigate to http://127.0.0.1:8000/docs

You will see an interactive Swagger UI Dashboard exposing the API specifications.

Endpoint Specifications & JSON Payload Examples
1. Create a Shortened Link (POST /shorten)
Accepts a destination link and an optional custom string token. Returns a fully qualified short redirection URL.

Payload Layout (With Custom Alias Name):

JSON
{
  "long_url": "[https://github.com/bharath-code](https://github.com/bharath-code)",
  "custom_alias": "my-portfolio"
}
Payload Layout (Default Algorithmic Fallback):

JSON
{
  "long_url": "[https://wikipedia.org](https://wikipedia.org)"
}
2. Redirect Link Execution (GET /{short_code})
Intercepts the generated token, registers click analytics parameters, checks the active Redis RAM cluster, and issues an instant HTTP 302 Found redirect command to the client browser.

3. Fetch Telemetry Data Dashboard (GET /analytics/{short_code})
Queries the relational data tables to calculate complete traffic stats for any generated token.

Response Payload Example:

JSON
{
  "short_code": "my-portfolio",
  "destination_url": "[https://github.com/Bharathbenny](https://github.com/Bharathbenny)",
  "total_clicks": 2,
  "click_history": [
    {
      "clicked_at": "2026-05-19T10:12:34.567890",
      "device_signature": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
    },
    {
      "clicked_at": "2026-05-19T10:14:12.112233",
      "device_signature": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
    }
  ]
}
Deep-Dive: System Design Decisions
Why Base62 Encoding?
Many basic shorteners use randomly generated strings. However, at scale, random generation leads to database collision checks (ensuring a string isn't already taken), which increases latency.

This engine uses a bi-directional mathematical Base62 calculation. When a default link is saved, it is assigned a fast auto-incrementing integer key (1, 2, 3). The system converts this integer into a base-62 string character set (a-z, A-Z, 0-9). This ensures each algorithmic link has a guaranteed mathematically unique mapping with zero resource overhead.

How the Cache Shield Prevents Database Failures
Hard drive storage operations (like writing to or reading from an SQLite file) are slow. If a link goes viral, thousands of people will click it at the exact same moment, causing a database performance bottleneck.

This engine solves this issue via the Cache-Aside Pattern:

A user clicks http://localhost:8000/my-portfolio.

The engine immediately checks the Redis RAM Cache (which can process over 100,000 operations per second).

Cache Hit: The long URL matches instantly in RAM. The user is redirected in microseconds, and the hard drive is completely bypassed.

Cache Miss: If the server reboots and RAM is empty, it catches the event, reads the long URL from SQLite, saves a copy back into Redis RAM with a 1-hour Time-To-Live (TTL) expiration window, and logs the click telemetry securely. The very next user click becomes a fast Cache Hit.
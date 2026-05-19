from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import models
import fakeredis  
from pydantic import BaseModel

app = FastAPI()
# Add this line right here to physically create the tables on your hard drive!
models.Base.metadata.create_all(bind=models.engine)
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Initialize our ultra-fast Redis Cache Simulator (RAM)
cache = fakeredis.FakeRedis(decode_responses=True)

# Day 1 Math Functions (Maintained for the auto-generation fallback path)
def encode(N):
    if N == 0: return CHARS[0]
    A = []
    while N > 0:
        A.append(CHARS[N % 62])
        N //= 62
    return "".join(reversed(A))

# Database connection helper (Dependency Injection)
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schema enforcing incoming JSON shape
class ShortenRequest(BaseModel):
    long_url: str
    custom_alias: str | None = None  

# 📥 Endpoint 1: Shorten a new URL (Supports Custom Aliases & Auto-Math)
@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)):
    
    # ─── 🛡️ LAYER 1: CUSTOM ALIAS PATH ───
    if payload.custom_alias:
        existing = db.query(models.URLMapping).filter(models.URLMapping.short_code == payload.custom_alias).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="This custom alias is already taken! Try another one."
            )
        
        db_url = models.URLMapping(long_url=payload.long_url, short_code=payload.custom_alias)
        db.add(db_url)
        db.commit()
        db.refresh(db_url)
        
        cache.setex(payload.custom_alias, 3600, payload.long_url)
        return {"short_url": f"http://localhost:8000/{payload.custom_alias}"}
        
    # ─── 🧮 LAYER 2: MATHEMATICAL FALLBACK PATH ───
    db_url = models.URLMapping(long_url=payload.long_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    short_code = encode(db_url.id)
    db_url.short_code = short_code
    db.commit()
    
    cache.setex(short_code, 3600, payload.long_url)
    return {"short_url": f"http://localhost:8000/{short_code}"}

# 📤 Endpoint 2: Redirect short link (Upgraded for Cache Verification & Automatic Click Logging)
@app.get("/{short_code}")
def redirect_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    
    # 🏃 Check Redis RAM cache first to keep redirection snappy
    cached_url = cache.get(short_code)
    
    # Even if it's a Cache Hit, we query the SQL record in the background 
    # to find its ID so we can properly link the analytics record.
    db_url = db.query(models.URLMapping).filter(models.URLMapping.short_code == short_code).first()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
        
    # 📊 AUTOMATIC ANALYTICS TRACKING
    # Extract browser details ("User-Agent") directly from incoming HTTP Request headers
    browser_info = request.headers.get("user-agent")
    
    # Build and commit a tracking record tied directly to this URL's Primary Key ID
    new_click = models.ClickAnalytic(url_id=db_url.id, user_agent=browser_info)
    db.add(new_click)
    db.commit()
    
    if cached_url:
        print("🚀 CACHE HIT! Redirecting instantly from Redis RAM...")
        return RedirectResponse(url=cached_url, status_code=status.HTTP_302_FOUND)
    
    print("⚠️ CACHE MISS! Fetching from slow SQLite Database hard drive...")
    cache.setex(short_code, 3600, db_url.long_url)
    return RedirectResponse(url=db_url.long_url, status_code=status.HTTP_302_FOUND)

# 📊 Endpoint 3: Public Metrics Dashboard
@app.get("/analytics/{short_code}")
def get_url_analytics(short_code: str, db: Session = Depends(get_db)):
    
    db_url = db.query(models.URLMapping).filter(models.URLMapping.short_code == short_code).first()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
        
    # Pull total click records from our relational relationship setup
    total_clicks = len(db_url.clicks)
    
    # Build a clean list of historical timestamps and browser signatures
    click_history = []
    for click in db_url.clicks:
        click_history.append({
            "clicked_at": click.timestamp,
            "device_signature": click.user_agent
        })
        
    return {
        "short_code": short_code,
        "destination_url": db_url.long_url,
        "total_clicks": total_clicks,
        "click_history": click_history
    }
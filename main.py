from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import models
import fakeredis  
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# It Creates the database tables automatically when the app starts or runing at first time
models.Base.metadata.create_all(bind=models.engine)

CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# This creates the fast in-memory Redis cache
cache = fakeredis.FakeRedis(decode_responses=True)

def encode(N):
    # It creates the short url for the long url using method called Base62
    if N == 0: return CHARS[0]
    A = []
    while N > 0:
        A.append(CHARS[N % 62])
        N //= 62
    return "".join(reversed(A))

def get_db():
    # It opens a database connection and closes it when done every time when the app is running  
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ShortenRequest(BaseModel):
    long_url: str
    custom_alias: str | None = None  

@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)):
    
    # If the user provided a custom alias link name then it will first check the database if the alias is already taken or not
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
        
        # FIX: Correct dictionary return key and value formatting
        return {"short_url": f"https://trim-bharath.onrender.com/{payload.custom_alias}"}
        
    # If the user doesnt provide a custom alias then we generate a new short url using encode function
    db_url = models.URLMapping(long_url=payload.long_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    short_code = encode(db_url.id)
    db_url.short_code = short_code
    db.commit()
    
    cache.setex(short_code, 3600, payload.long_url)
    
    # FIX: Correct dictionary return key and value formatting
    return {"short_url": f"https://trim-bharath.onrender.com/{short_code}"}

# this is the place where we redirect the user to the long url when they used the short url
@app.get("/{short_code}")
def redirect_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    
    # will first check the redis cache if the short url present in the cache or not
    cached_url = cache.get(short_code)
    
    # we also check the database if the short url is present in the database or not
    db_url = db.query(models.URLMapping).filter(models.URLMapping.short_code == short_code).first()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
        
    # it reads the data from the request headers from the user who used short url and save the click data
    browser_info = request.headers.get("user-agent")
    new_click = models.ClickAnalytic(url_id=db_url.id, user_agent=browser_info)
    db.add(new_click)
    db.commit()
    
    if cached_url:
        print("🚀 CACHE HIT! Redirecting instantly from Redis RAM...")
        return RedirectResponse(url=cached_url, status_code=status.HTTP_302_FOUND)
    
    # it saves the url in the cache if it was not there already
    print("⚠️ CACHE MISS! Fetching from slow SQLite Database hard drive...")
    cache.setex(short_code, 3600, db_url.long_url)
    return RedirectResponse(url=db_url.long_url, status_code=status.HTTP_302_FOUND)

@app.get("/analytics/{short_code}")
def get_url_analytics(short_code: str, db: Session = Depends(get_db)):
    
    db_url = db.query(models.URLMapping).filter(models.URLMapping.short_code == short_code).first()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
        
    # counts the total clicks for the short url
    total_clicks = len(db_url.clicks)
    
    click_history = []
    # it will read the click history for the short url
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
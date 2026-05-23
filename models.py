from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
import os
# --- DYNAMIC DATABASE PATH FOR DEPLOYMENT ---
# Render automatically sets an environment variable named 'RENDER' to 'true'
if os.environ.get("RENDER"):
    DATABASE_URL = "sqlite:////data/urls.db"  # Production Linux persistent disk path
else:
    DATABASE_URL = "sqlite:///./urls.db"      # Local Windows testing path
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

#This is the session factory for the database connection ehich will be used to create the database tables
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#This is the base architect blueprint which converts the python classes into database tables
Base = declarative_base()

#This is the class for the database table for the url mappings
class URLMapping(Base):
    __tablename__ = "url_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=True)
    
    clicks = relationship("ClickAnalytic", back_populates="url_mapping", cascade="all, delete-orphan")

#This is the class for the database table for the click analytics for the short url which stores the click data for the short url
class ClickAnalytic(Base):
    __tablename__ = "click_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("url_mappings.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String, nullable=True)
    
    url_mapping = relationship("URLMapping", back_populates="clicks")
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

# 1. Tell SQLAlchemy where to create the physical database file
DATABASE_URL = "sqlite:///./urls.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 2. Create the Session Factory that main.py is looking for!
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Initialize the base architect blueprint
Base = declarative_base()

class URLMapping(Base):
    __tablename__ = "url_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=True)
    
    clicks = relationship("ClickAnalytic", back_populates="url_mapping", cascade="all, delete-orphan")

class ClickAnalytic(Base):
    __tablename__ = "click_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("url_mappings.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String, nullable=True)
    
    url_mapping = relationship("URLMapping", back_populates="clicks")
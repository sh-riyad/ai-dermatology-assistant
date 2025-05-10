from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, 
                            autoflush=False, 
                            bind=engine)
"""
    Creates a session factory that generates new sessions for database interactions
    `autocommit=False` ensures transactions must be committed manually
    `autoflush=False` prevents automatic writing to the database before commit
"""

Base = declarative_base()

def init_db():            
    
    from app.models.users import User
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
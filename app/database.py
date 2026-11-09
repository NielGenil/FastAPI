from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass

# A dependency: gives each request its own DB session, then closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
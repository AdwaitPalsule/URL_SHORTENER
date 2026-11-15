from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from collections.abc import Iterator
from sqlalchemy.orm import Session
from config import settings


engine = create_engine(settings.database_url,pool_pre_ping = True)
SessionLocal = sessionmaker(bind=engine,autoflush=False)

class Base(DeclarativeBase):
    pass
def get_db()->Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

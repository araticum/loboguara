from sqlalchemy import create_engine
from sqlalchemy import MetaData, event
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DATABASE_URL, DB_SCHEMA


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData(schema=DB_SCHEMA)
Base = declarative_base(metadata=metadata)


@event.listens_for(engine, "connect")
def set_search_path(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f"SET search_path TO {DB_SCHEMA}, public")
    cursor.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

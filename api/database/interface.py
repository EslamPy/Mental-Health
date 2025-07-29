#this part is mainly for the backend to interact with the database remove it if you dont want it 
from database.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
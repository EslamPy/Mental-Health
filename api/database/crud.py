from sqlalchemy.orm import Session
from models.mood import Mood
from models.user import User

def create_mood(db: Session, name: str, description: str = None, image_url: str = None):
    db_mood = Mood(name=name, description=description, image_url=image_url)
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood

def get_mood(db: Session, mood_id: int):
    return db.query(Mood).filter(Mood.id == mood_id).first()

def get_all_moods(db: Session):
    return db.query(Mood).all()

def delete_mood(db: Session, mood_id: int):
    mood = db.query(Mood).filter(Mood.id == mood_id).first()
    if mood:
        db.delete(mood)
        db.commit()
        return True
    return False

def get_image_by_id(db: Session, image_id: int):
    return get_mood(db, image_id)  # Reusing mood function since images are stored in Mood model

def get_images_by_name(db: Session, name: str):
    return db.query(Mood).filter(Mood.name.contains(name)).all()

def create_user(db: Session, name: str, email: str, password: str, role: str):
    db_user = User(name=name, email=email, password=password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
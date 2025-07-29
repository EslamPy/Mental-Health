# test_database.py
from database.database import SessionLocal, engine
from database.init_db import initialize_database
from database.crud import (
    create_user,
    get_user_by_email,
    create_mood,
    get_all_moods,
    delete_mood,
    get_image_by_id,
)
from models.user import User
from models.mood import Mood

# Initialize the database
initialize_database()

# Create a test session
db = SessionLocal()

# Test User Operations
print("=== Testing User Operations ===")
test_user = create_user(db, name="Test User", email="test@example.com", password="123456", role="user")
print(f"Created User: {test_user.name} (ID: {test_user.id})")

found_user = get_user_by_email(db, email="test@example.com")
print(f"Found User by Email: {found_user.email}")

# Test Mood Operations
print("\n=== Testing Mood Operations ===")
test_mood = create_mood(db, name="Happy", description="Feeling great!", image_url="/images/happy.jpg")
print(f"Created Mood: {test_mood.name} (ID: {test_mood.id})")

moods = get_all_moods(db)
print(f"All Moods: {[m.name for m in moods]}")

# Test Image Operations
print("\n=== Testing Image Operations ===")
image = get_image_by_id(db, image_id=test_mood.id)
print(f"Found Image by ID: {image.image_url}")

# Cleanup
delete_mood(db, mood_id=test_mood.id)
print(f"Deleted Mood ID {test_mood.id}")

db.close()
print("\n✅ All tests completed! Check the output above.")
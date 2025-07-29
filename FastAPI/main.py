from datetime import datetime, timedelta, timezone
from typing import Optional, List
import secrets
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
import shutil
import httpx
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Union
import asyncio
import time  # Blocking sleep



class Item(BaseModel):
    name: str
    price: float    
    in_stock: bool = False

app = FastAPI()

FRONTEND_DIR = "frontend_dir"
os.makedirs(FRONTEND_DIR, exist_ok=True)

BACKEND_DIR = "backend_dir"
os.makedirs(BACKEND_DIR, exist_ok=True)

# Basic routes for demonstration
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/items/")
def create_item(item: Item):
    return item


# Blocking vs Non-blocking endpoints for concurrency testing
@app.get("/blocking")
async def blocking_route():
    time.sleep(5)  # ❌ This blocks the event loop!
    return {"message": "This is blocking"}


@app.get("/non-blocking")
async def non_blocking_route():
    await asyncio.sleep(5)  # ✅ Non-blocking
    return {"message": "This is non-blocking"}


# Load environment variables
load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

# JWT Configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-for-development-only")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Application Configuration
APP_TITLE = os.getenv("APP_TITLE", "Auth Demo API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Initialize FastAPI app
app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()

# ============================================================================
# Fake Database (In-Memory Dictionary)
# ============================================================================

# Users database: {username: user_data}
# Example structure:
# {
#     "john_doe": {
#         "username": "john_doe",
#         "email": "john@example.com",
#         "hashed_password": "$2b$12$...",  # BCrypt hash with built-in salt
#         "salt": "random_salt_value_123",   # Additional custom salt
#         "created_at": "2024-01-15T10:30:00",
#         "is_active": True
#     },
#     "jane_smith": {
#         "username": "jane_smith",
#         "email": "jane@example.com",
#         "hashed_password": "$2b$12$...",
#         "salt": "random_salt_value_456",
#         "created_at": "2024-01-16T14:20:00",
#         "is_active": True
#     }
# }
fake_users_db = {}

# User items database: {username: [items]}
# Example structure:
# {
#     "john_doe": [
#         {
#             "id": 1,
#             "name": "My First Item",
#             "description": "This is John's first item",
#             "owner": "john_doe",
#             "created_at": "2024-01-15T11:00:00",
#             "is_public": False
#         },
#         {
#             "id": 2,
#             "name": "Another Item",
#             "description": "John's second item",
#             "owner": "john_doe",
#             "created_at": "2024-01-15T12:00:00",
#             "is_public": True
#         }
#     ],
#     "jane_smith": [
#         {
#             "id": 1,
#             "name": "Jane's Project",
#             "description": "A project by Jane",
#             "owner": "jane_smith",
#             "created_at": "2024-01-16T15:00:00",
#             "is_public": False
#         }
#     ]
# }
fake_items_db = {}

# ============================================================================
# Pydantic Models
# ============================================================================

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str

class ItemCreate(BaseModel):
    name: str
    description: str

class Item(BaseModel):
    id: int
    name: str
    description: str
    owner: str

# ============================================================================
# Utility Functions
# ============================================================================

def generate_salt() -> str:
    """Generate a random salt for password hashing"""
    return secrets.token_hex(32)

def verify_password(plain_password: str, hashed_password: str, salt: str = None) -> bool:
    """Verify a plain password against its hash with optional additional salt"""
    if salt:
        # Combine password with custom salt before verification
        salted_password = plain_password + salt
        return pwd_context.verify(salted_password, hashed_password)
    else:
        # BCrypt already includes salt, so direct verification
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str, salt: str = None) -> str:
    """Generate hash for a password with optional additional salt"""
    if salt:
        # Combine password with custom salt before hashing
        salted_password = password + salt
        return pwd_context.hash(salted_password)
    else:
        # BCrypt includes built-in salt generation
        return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user credentials with salt support"""
    user = fake_users_db.get(username)
    if not user:
        return None
    
    # Use the stored salt for password verification
    user_salt = user.get("salt")
    if not verify_password(password, user["hashed_password"], user_salt):
        return None
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    
    return user

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FastAPI Authentication Demo",
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login",
            "profile": "GET /profile (requires auth)",
            "items": "GET /items (requires auth)",
            "create_item": "POST /items (requires auth)"
        }
    }

@app.post("/register", response_model=dict)
async def register(user: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Validate input
    if len(user.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Generate salt and hash password
    user_salt = generate_salt()
    hashed_password = get_password_hash(user.password, user_salt)
    
    # Store user with salt and additional metadata
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "salt": user_salt,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True
    }
    
    # Initialize empty items list for user
    fake_items_db[user.username] = []
    
    return {"message": "User registered successfully"}

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return JWT token"""
    
    # Authenticate user
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile", response_model=User)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile (protected route)"""
    return User(
        username=current_user["username"],
        email=current_user["email"]
    )

@app.get("/items", response_model=List[Item])
async def get_items(current_user: dict = Depends(get_current_user)):
    """Get current user's items (protected route)"""
    username = current_user["username"]
    user_items = fake_items_db.get(username, [])
    
    return [
        Item(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            owner=item["owner"]
        )
        for item in user_items
    ]

@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate, current_user: dict = Depends(get_current_user)):
    """Create a new item for the current user (protected route)"""
    username = current_user["username"]
    
    # Initialize user's items list if not exists
    if username not in fake_items_db:
        fake_items_db[username] = []
    
    # Generate new item ID
    item_id = len(fake_items_db[username]) + 1
    
    # Create new item with additional metadata
    new_item = {
        "id": item_id,
        "name": item.name,
        "description": item.description,
        "owner": username,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_public": False  # Default to private
    }
    
    # Add to user's items
    fake_items_db[username].append(new_item)
    
    return Item(**new_item)

@app.get("/debug/users")
async def debug_users():
    """Debug endpoint to see all users (only available in debug mode)"""
    if not DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debug endpoints are disabled in production"
        )
    return {
        "users": list(fake_users_db.keys()),
        "total_users": len(fake_users_db)
    }

@app.get("/debug/items")
async def debug_items():
    """Debug endpoint to see all items (only available in debug mode)"""
    if not DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debug endpoints are disabled in production"
        )
    return fake_items_db

# ============================================================================
# Run the application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI Authentication Demo...")
    print(f"Visit http://{HOST}:{PORT}/docs for interactive API documentation")
    uvicorn.run(app, host=HOST, port=PORT)

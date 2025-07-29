# FastAPI Authentication & Authorization Demo

A minimal FastAPI application demonstrating JWT-based authentication and authorization with common security best practices.

## Features

- **User Registration**: Create new user accounts with password hashing and salting
- **JWT Authentication**: Secure login with JWT tokens
- **Protected Routes**: Routes that require authentication
- **Authorization**: Users can only access their own data
- **Item Management**: Create and view items per user

## Security Features Implemented

- **Password Hashing**: Using bcrypt with additional custom salting
- **JWT Tokens**: With expiration times for security
- **Protected Routes**: Requiring authentication for sensitive endpoints
- **User-Specific Data Access**: Authorization ensuring users can only access their own data
- **Cryptographically Secure Salt Generation**: Each password gets a unique salt

## Common Security Flaws Addressed

- **Plaintext Passwords**: Passwords are hashed with salt, not stored in plaintext
- **Rainbow Table Attacks**: Each password gets a unique salt to prevent rainbow table attacks
- **Token Security**: JWT tokens have expiration times to limit exposure
- **Authentication Bypass**: Protected routes verify token validity
- **Unauthorized Access**: Users can only access their own data

## Installation

1. Clone the repository or download the files

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

1. Set up environment variables:

    ```bash
    # Copy the example environment file
    cp .env.example .env
    
    # Edit .env file with your settings
    # Make sure to change the SECRET_KEY to a strong, random value
    ```

    **Important**: Generate a strong secret key for production. You can use:

    ```bash
    python -c "import secrets; print(secrets.token_urlsafe(32))"
    ```

## Environment Variables

The application uses the following environment variables (configured in `.env`):

- `SECRET_KEY`: JWT secret key (required - change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: 30)
- `APP_TITLE`: Application title (default: Auth Demo API)
- `APP_VERSION`: Application version (default: 1.0.0)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug endpoints (default: True)

## Running the Application

1. Start the server:

    ```bash
    python main.py
    ```

2. Or use uvicorn directly:

    ```bash
    uvicorn main:app --reload
    ```

3. Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation

## API Endpoints

### Public Endpoints

- `GET /` - API information
- `POST /register` - Register a new user
- `POST /login` - Login and get JWT token

### Protected Endpoints (require authentication)

- `GET /profile` - Get current user profile
- `GET /items` - Get user's items
- `POST /items` - Create new item

### Debug Endpoints (only available when DEBUG=True)

- `GET /debug/users` - View all users
- `GET /debug/items` - View all items

## Usage Examples

### 1. Register a new user

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "password123",
    "email": "john@example.com"
  }'
```

### 2. Login and get token

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "password123"
  }'
```

### 3. Access protected route

```bash
curl -X GET "http://localhost:8000/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 4. Create an item

```bash
curl -X POST "http://localhost:8000/items" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Item",
    "description": "This is my first item"
  }'
```

## Database Structure

This demo uses in-memory dictionaries as a fake database:

```python
fake_users_db = {
    "username": {
        "username": "john",
        "email": "john@example.com",
        "hashed_password": "bcrypt_hash_here"
    }
}

fake_items_db = {
    "username": [
        {
            "id": 1,
            "name": "Item name",
            "description": "Item description",
            "owner": "username"
        }
    ]
}
```

## Security Considerations

### What's Implemented

- Password hashing with bcrypt
- JWT tokens with expiration
- Protected routes with authentication
- User-specific data access (authorization)
- Input validation

### For Production

Things you need for production include (but not limited to):

- **Use strong environment variables**: Set a secure SECRET_KEY and disable DEBUG
- Implement proper database (PostgreSQL, MySQL, etc.)
- Add rate limiting
- Implement refresh tokens
- Use HTTPS
- Add logging and monitoring
- Implement proper error handling
- Add password complexity requirements
- Consider implementing account lockout after failed attempts

## Common JWT Security Flaws Addressed

1. **Weak Secret Key**: Use a strong, random secret key
2. **No Token Expiration**: Tokens expire after 30 minutes
3. **Storing Tokens Insecurely**: Client should store tokens securely
4. **No Token Validation**: All protected routes validate tokens
5. **Algorithm Confusion**: Explicitly specify HS256 algorithm

## File Structure

```plain
fastapi-auth-demo/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment file
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Dependencies

- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` - Password hashing
- `python-multipart` - Form data parsing
- `python-dotenv` - Environment variable loading



# fastapi-mentorship
FastAPI session for Microsoft Mentorship Program

Installation
```bash
1- create a python environment and activate it
python -m venv .venv
.venv\Scripts\activate

2- install FastAPI and its dependencies
pip install "fastapi[standard]"

3- run the project
fastapi dev main.py

```

## Flow of different FastAPI components

Client (Browser/Insomnia)
        ↓
     Uvicorn (ASGI Server)
        ↓
   Starlette (Web Layer)
        ↓
   FastAPI (API Logic + Docs + Validation with Pydantic)
        ↓
     Your Code (Business Logic)
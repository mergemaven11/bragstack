import os
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.database import users_collection

SECRET_KEY = os.getenv("JWT_SECRET", "change-this-dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash a plain-text password.

    Args:
        password: The plain-text password supplied by the user.

    Returns:
        A securely hashed password string.
    """
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored password hash.

    Args:
        plain_password: The plain-text password supplied during login.
        hashed_password: The hashed password stored in MongoDB.

    Returns:
        True if the password is valid, otherwise False.
    """
    return password_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Create a signed JWT access token.

    Args:
        data: The payload data to include in the token.

    Returns:
        A signed JWT access token string.
    """
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({"exp": expire})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def serialize_user(user: dict) -> dict:
    """Convert a MongoDB user document into an API-safe response dictionary.

    Args:
        user: The MongoDB user document.

    Returns:
        A dictionary containing safe user fields.
    """
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "created_at": user.get("created_at"),
    }


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Return the currently authenticated user from a JWT bearer token.

    Args:
        token: The JWT access token from the Authorization header.

    Returns:
        The authenticated user document from MongoDB.

    Raises:
        HTTPException: If the token is missing, invalid, expired, or does not
            match an existing user.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise credentials_error

    except JWTError:
        raise credentials_error

    if not ObjectId.is_valid(user_id):
        raise credentials_error

    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise credentials_error

    return user
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    serialize_user,
    verify_password,
)
from app.database import users_collection

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Request body for creating a new user account.

    Attributes:
        name: The user's display name.
        email: The user's email address.
        password: The user's plain-text password.
    """

    name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    """Request body for logging in an existing user.

    Attributes:
        email: The user's email address.
        password: The user's plain-text password.
    """

    email: EmailStr
    password: str


@router.post("/register")
def register_user(payload: RegisterRequest):
    """Create a new user account and return an access token.

    Args:
        payload: The registration request containing name, email, and password.

    Returns:
        A dictionary containing the access token, token type, and serialized user.

    Raises:
        HTTPException: If an account already exists for the provided email.
    """
    normalized_email = payload.email.lower().strip()

    existing_user = users_collection.find_one({"email": normalized_email})

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user_doc = {
        "name": payload.name.strip(),
        "email": normalized_email,
        "hashed_password": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = users_collection.insert_one(user_doc)

    access_token = create_access_token({"sub": str(result.inserted_id)})

    created_user = users_collection.find_one({"_id": result.inserted_id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": serialize_user(created_user),
    }


@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate a user and return an access token.

    Args:
        form_data: OAuth2-compatible login form data from Swagger or the frontend.
            The username field should contain the user's email address.

    Returns:
        A dictionary containing the access token, token type, and serialized user.

    Raises:
        HTTPException: If the email or password is invalid.
    """
    normalized_email = form_data.username.lower().strip()

    user = users_collection.find_one({"email": normalized_email})

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token({"sub": str(user["_id"])})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": serialize_user(user),
    }

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user.

    Args:
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        A serialized user dictionary.
    """
    return serialize_user(current_user)
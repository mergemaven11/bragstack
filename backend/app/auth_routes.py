from datetime import datetime, timezone
import re
import secrets

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

class ProfileUpdateRequest(BaseModel):
    """Editable public profile information."""

    name: str = Field(..., min_length=1, max_length=80)
    headline: str = Field(default="", max_length=120)
    bio: str = Field(default="", max_length=500)
    location: str = Field(default="", max_length=100)
    github_url: str = Field(default="", max_length=300)
    portfolio_url: str = Field(default="", max_length=300)
    resume_url: str = Field(default="", max_length=300)

def slugify(value: str) -> str:
    """Convert a display name into a URL-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "user"


def generate_unique_public_slug(name: str) -> str:
    """Generate a stable, unique public profile slug."""

    base_slug = slugify(name)

    while True:
        random_suffix = secrets.token_hex(3)
        slug = f"{base_slug}-{random_suffix}"

        if not users_collection.find_one({"public_slug": slug}):
            return slug

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
    "public_slug": generate_unique_public_slug(payload.name),
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
    """Return the currently authenticated user."""

    current_slug = current_user.get("public_slug", "")
    basic_name_slug = slugify(current_user.get("name", "user"))

    if not current_slug or current_slug == basic_name_slug:
        public_slug = generate_unique_public_slug(
            current_user.get("name", "user")
        )

        users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"public_slug": public_slug}},
        )

        current_user["public_slug"] = public_slug

    return serialize_user(current_user)

@router.patch("/me/profile")
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update the authenticated user's public profile."""

    updates = {
        "name": payload.name.strip(),
        "headline": payload.headline.strip(),
        "bio": payload.bio.strip(),
        "location": payload.location.strip(),
        "github_url": payload.github_url.strip(),
        "portfolio_url": payload.portfolio_url.strip(),
        "resume_url": payload.resume_url.strip(),
    }

    url_fields = ("github_url", "portfolio_url", "resume_url")

    for field_name in url_fields:
        value = updates[field_name]

        if value and not value.startswith(("http://", "https://")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} must start with http:// or https://",
            )

    users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": updates},
    )

    updated_user = users_collection.find_one(
        {"_id": current_user["_id"]}
    )

    return serialize_user(updated_user)
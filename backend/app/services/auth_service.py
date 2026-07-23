from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserRegisterResponse
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.privacy import encrypt_sensitive_data, decrypt_sensitive_data


class AuthService:
    """
    Service Layer: Contains all business logic & direct DB queries for Registration and Login.
    Simple and straightforward flow: Route -> Service -> Database.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_in: UserCreate) -> UserRegisterResponse:
        """Registers a new user directly in PostgreSQL and returns User info along with JWT token."""
        # 1. Check if user already exists
        stmt = select(User).where(User.email == user_in.email.lower())
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )

        # 2. Hash password & encrypt PII
        hashed_pwd = get_password_hash(user_in.password)
        encrypted_name = (
            encrypt_sensitive_data(user_in.full_name) if user_in.full_name else None
        )

        # 3. Create & save user model
        db_user = User(
            email=user_in.email.lower(),
            hashed_password=hashed_pwd,
            full_name_encrypted=encrypted_name,
            role=user_in.role or "patient",
            is_active=True,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        # 4. Decrypt full name for API response
        decrypted_name = (
            decrypt_sensitive_data(db_user.full_name_encrypted)
            if db_user.full_name_encrypted
            else None
        )

        user_response = UserResponse(
            id=db_user.id,
            email=db_user.email,
            full_name=decrypted_name,
            role=db_user.role,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
        )

        # 5. Generate access token upon registration
        access_token = create_access_token(subject=str(db_user.id))

        return UserRegisterResponse(
            user=user_response,
            access_token=access_token,
            token_type="bearer",
        )

    async def authenticate_user(self, email: str, password: str) -> Token:
        """Authenticates user credentials and returns JWT token."""
        # 1. Fetch user from DB
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        # 2. Verify existence and password
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account",
            )

        # 3. Generate access token
        access_token = create_access_token(subject=str(user.id))
        return Token(access_token=access_token, token_type="bearer")

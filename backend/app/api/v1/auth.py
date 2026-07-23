from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserRegisterResponse
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user in the system asynchronously.
    - Hashes password with bcrypt.
    - Encrypts PII (full name) with Fernet encryption.
    - Generates and returns JWT Access Token upon registration.
    """
    service = AuthService(db)
    return await service.register_user(user_in)


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user via JSON payload asynchronously and return JWT Bearer Access Token.
    """
    service = AuthService(db)
    return await service.authenticate_user(email=user_in.email, password=user_in.password)


@router.post("/login/form", response_model=Token)
async def login_oauth_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login endpoint (for FastAPI Swagger UI auto-auth).
    """
    service = AuthService(db)
    return await service.authenticate_user(email=form_data.username, password=form_data.password)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current logged in user profile (requires Bearer token in Authorization header).
    """
    return current_user

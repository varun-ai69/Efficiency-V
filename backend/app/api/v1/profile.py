from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.user import UserResponse
from app.schemas.profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.post("", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(
    profile_in: UserProfileCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update the current user's profile with static demographics and medical history.
    """
    stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if profile:
        # Update existing
        for field, value in profile_in.model_dump().items():
            setattr(profile, field, value)
        profile.bmi = round(profile.weight_kg / (profile.height_m ** 2), 2)
    else:
        # Create new
        profile_data = profile_in.model_dump()
        bmi = round(profile_data["weight_kg"] / (profile_data["height_m"] ** 2), 2)
        profile = UserProfile(
            user_id=current_user.id,
            bmi=bmi,
            **profile_data
        )
        db.add(profile)
    
    await db.commit()
    await db.refresh(profile)
    return profile


@router.patch("", response_model=UserProfileResponse)
async def patch_profile(
    profile_in: UserProfileUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update the current user's profile.
    """
    stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please create it first."
        )

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    # Recalculate BMI in case height or weight was updated
    profile.bmi = round(profile.weight_kg / (profile.height_m ** 2), 2)

    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve the current user's profile data.
    """
    stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found."
        )
    
    return profile

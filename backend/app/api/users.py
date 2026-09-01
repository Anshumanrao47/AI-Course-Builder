"""
User profile and learning-preference endpoints (protected).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.preference import UserLearningPreference
from app.models.user import User
from app.schemas.preference import PreferenceRead, PreferenceUpdate
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def _get_or_create_preference(db: Session, user: User) -> UserLearningPreference:
    if user.preference is not None:
        return user.preference
    preference = UserLearningPreference(user_id=user.id)
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


@router.get("/me/preferences", response_model=PreferenceRead)
def read_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserLearningPreference:
    return _get_or_create_preference(db, current_user)


@router.put("/me/preferences", response_model=PreferenceRead)
def update_preferences(
    payload: PreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserLearningPreference:
    preference = _get_or_create_preference(db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(preference, field, value)
    db.commit()
    db.refresh(preference)
    return preference

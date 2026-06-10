from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


# ── 1. CREATE a user ──────────────────────────────────────────────────────────
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # check if email already taken
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password,  # plain text for now — Week 2 adds bcrypt
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # re-fetches from DB so id and created_at are populated
    return new_user


# ── 2. GET all users ──────────────────────────────────────────────────────────
@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# ── 3. GET one user by ID ─────────────────────────────────────────────────────
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


# ── 4. UPDATE a user ──────────────────────────────────────────────────────────
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

        # only update fields that were actually sent (not None)
        if updated.username is not None:
            user.username = updated.username
        if updated.email is not None:
            user.email = updated.email
        if updated.password is not None:
            user.hashed_password = updated.password  # bcrypt goes here in Week 2

    db.commit()
    db.refresh(user)
    return user


# ── 5. DELETE a user ──────────────────────────────────────────────────────────
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    db.delete(user)
    db.commit()
    # 204 returns no body — do not return anything here

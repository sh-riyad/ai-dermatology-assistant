from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.utils.password import hash_password
from app.models.users import User
from typing import List, Optional
from app.schemas.users import CreateUserInput, UpdateUserInput

# Create a New User
def create_user(user: CreateUserInput, db: Session):
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        phone=user.phone,
        password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# Read All Users (Paginated)
def read_users(skip: int, limit: int, db: Session) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# Read User by ID
def read_user(user_id: int, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update User
def update_user(user_id: int, user: UpdateUserInput, current_user: User, db: Session) -> User:
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.username != db_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    db_user.name = user.name if user.name is not None else db_user.name
    db_user.username = user.username if user.username is not None else db_user.username
    db_user.email = user.email if user.email is not None else db_user.email
    db_user.phone = user.phone if user.phone is not None else db_user.phone
    if user.password:
        db_user.password = hash_password(user.password)

    db.commit()
    db.refresh(db_user)
    return db_user

# Delete User
def delete_user(user_id: int, db: Session) -> User:
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return db_user
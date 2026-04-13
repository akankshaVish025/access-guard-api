from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserStatusChange, UserUpdate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def add_user(db: Session, payload: UserCreate) -> User:
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise ValueError("User already exists with this email.")

    user = User(
        name=payload.name,
        email=payload.email,
        data1=payload.data1,
        data2=payload.data2,
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def update_user(db: Session, payload: UserUpdate) -> User:
    user = get_user_by_email(db, payload.email)
    if not user:
        raise LookupError("User not found.")

    if payload.name is not None:
        user.name = payload.name
    if payload.data1 is not None:
        user.data1 = payload.data1
    if payload.data2 is not None:
        user.data2 = payload.data2

    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def change_status(db: Session, payload: UserStatusChange) -> User:
    user = get_user_by_email(db, payload.email)
    if not user:
        raise LookupError("User not found.")

    user.status_enabled = payload.status_enabled
    db.add(user)
    db.flush()
    db.refresh(user)
    return user

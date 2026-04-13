from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut, UserStatusChange, UserUpdate
from app.services.user_service import add_user, change_status, update_user

router = APIRouter(tags=["users"])


@router.post("/adduser", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def add_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    try:
        user = add_user(db, payload)
        return UserOut.model_validate(user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.put("/updateuser", response_model=UserOut)
def update_user_endpoint(payload: UserUpdate, db: Session = Depends(get_db)) -> UserOut:
    try:
        user = update_user(db, payload)
        return UserOut.model_validate(user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/changestatus", response_model=UserOut)
def change_status_endpoint(payload: UserStatusChange, db: Session = Depends(get_db)) -> UserOut:
    try:
        user = change_status(db, payload)
        return UserOut.model_validate(user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

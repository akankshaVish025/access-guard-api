from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.access import AccessEmailIn, AccessFinalIn, AccessOtpOut, AccessTokenOut
from app.services.access_service import add_access, get_access_step1, get_access_step2

router = APIRouter(tags=["access"])


@router.post("/addaccess", response_model=AccessTokenOut)
def add_access_endpoint(payload: AccessEmailIn, db: Session = Depends(get_db)) -> AccessTokenOut:
    try:
        access = add_access(db, payload.email_id)
        return AccessTokenOut(email_id=access.email_id, auth_token=access.auth_token or "")
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/getaccess", response_model=AccessOtpOut)
def get_access_endpoint(payload: AccessEmailIn, db: Session = Depends(get_db)) -> AccessOtpOut:
    try:
        access = get_access_step1(db, payload.email_id)
        return AccessOtpOut(
            email_id=access.email_id,
            message="OTP generated. In production this should be sent via email provider.",
            otp_expires_at=access.otp_expires_at,
            otp_dev_only=access.otp_code or "",
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/getaccessfinal", response_model=AccessTokenOut)
def get_access_final_endpoint(payload: AccessFinalIn, db: Session = Depends(get_db)) -> AccessTokenOut:
    try:
        access = get_access_step2(db, payload.email_id, payload.six_digit_code)
        return AccessTokenOut(email_id=access.email_id, auth_token=access.auth_token or "")
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

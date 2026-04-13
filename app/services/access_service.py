from datetime import UTC, datetime, timedelta
from secrets import randbelow, token_urlsafe
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.data_access import DataAccess
from app.models.user import User

OTP_TTL_MINUTES = 10


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _as_utc_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _generate_token() -> str:
    return f"{uuid4().hex}.{token_urlsafe(24)}"


def _generate_otp() -> str:
    return f"{randbelow(1_000_000):06d}"


def _get_user(db: Session, email_id: str) -> User | None:
    return db.query(User).filter(User.email == email_id).first()


def _get_access(db: Session, email_id: str) -> DataAccess | None:
    return db.query(DataAccess).filter(DataAccess.email_id == email_id).first()


def add_access(db: Session, email_id: str) -> DataAccess:
    user = _get_user(db, email_id)
    if not user:
        raise LookupError("User not found.")
    if not user.status_enabled:
        raise PermissionError("User is disabled.")

    access = _get_access(db, email_id)
    if access is None:
        access = DataAccess(email_id=email_id)

    access.auth_token = _generate_token()
    access.counter = (access.counter or 0) + 1
    access.last_access = _now_utc()
    access.otp_code = None
    access.otp_expires_at = None

    db.add(access)
    db.flush()
    db.refresh(access)
    return access


def get_access_step1(db: Session, email_id: str) -> DataAccess:
    user = _get_user(db, email_id)
    if not user:
        raise LookupError("User not found.")
    if not user.status_enabled:
        raise PermissionError("User is disabled.")

    access = _get_access(db, email_id)
    if access is None:
        access = DataAccess(email_id=email_id, auth_token=_generate_token(), counter=0)

    access.otp_code = _generate_otp()
    access.otp_expires_at = _now_utc() + timedelta(minutes=OTP_TTL_MINUTES)
    access.counter = (access.counter or 0) + 1
    access.last_access = _now_utc()

    db.add(access)
    db.flush()
    db.refresh(access)
    return access


def get_access_step2(db: Session, email_id: str, six_digit_code: str) -> DataAccess:
    user = _get_user(db, email_id)
    if not user:
        raise LookupError("User not found.")
    if not user.status_enabled:
        raise PermissionError("User is disabled.")

    access = _get_access(db, email_id)
    if access is None:
        raise LookupError("Access record not found. Call /getaccess first.")

    now = _now_utc()
    if not access.otp_code or not access.otp_expires_at:
        raise ValueError("OTP not generated. Call /getaccess first.")
    if _as_utc_aware(access.otp_expires_at) < now:
        raise ValueError("OTP expired. Call /getaccess again.")
    if access.otp_code != six_digit_code:
        raise ValueError("Invalid OTP code.")

    if not access.auth_token:
        access.auth_token = _generate_token()

    access.counter = (access.counter or 0) + 1
    access.last_access = now
    access.otp_code = None
    access.otp_expires_at = None

    db.add(access)
    db.flush()
    db.refresh(access)
    return access


def validate_token(db: Session, auth_token: str) -> DataAccess:
    access = db.query(DataAccess).filter(DataAccess.auth_token == auth_token).first()
    if access is None:
        raise PermissionError("Invalid auth token.")

    user = _get_user(db, access.email_id)
    if user is None or not user.status_enabled:
        raise PermissionError("User disabled or missing.")

    access.counter = (access.counter or 0) + 1
    access.last_access = _now_utc()
    db.add(access)
    db.flush()
    db.refresh(access)
    return access

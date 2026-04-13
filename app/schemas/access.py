from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AccessEmailIn(BaseModel):
    email_id: str = Field(min_length=5, max_length=255)

    @field_validator("email_id")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return value.lower().strip()


class AccessTokenOut(BaseModel):
    email_id: str
    auth_token: str


class AccessOtpOut(BaseModel):
    email_id: str
    message: str
    otp_expires_at: datetime
    otp_dev_only: str


class AccessFinalIn(BaseModel):
    email_id: str = Field(min_length=5, max_length=255)
    six_digit_code: str = Field(min_length=6, max_length=6)

    @field_validator("email_id")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return value.lower().strip()

    @field_validator("six_digit_code")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("OTP must contain only digits.")
        return value

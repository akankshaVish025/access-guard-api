from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    data1: str | None = Field(default=None, max_length=255)
    data2: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return value.lower().strip()


class UserUpdate(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    data1: str | None = Field(default=None, max_length=255)
    data2: str | None = Field(default=None, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return value.lower().strip()


class UserStatusChange(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    status_enabled: bool

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return value.lower().strip()


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    data1: str | None
    data2: str | None
    status_enabled: bool

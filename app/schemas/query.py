from pydantic import BaseModel, Field, field_validator


class DetailsQuery(BaseModel):
    auth_token: str = Field(min_length=20)
    field_name: str | None = None
    name_prefix: str | None = Field(default=None, max_length=30)
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

    @field_validator("field_name")
    @classmethod
    def validate_field_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"name", "email", "data1", "data2", "status_enabled"}
        if value not in allowed:
            raise ValueError(f"field_name must be one of: {', '.join(sorted(allowed))}")
        return value

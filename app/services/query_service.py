from sqlalchemy.orm import Session

from app.models.user import User

ALLOWED_FIELDS = {"name", "email", "data1", "data2", "status_enabled"}


def get_user_details(
    db: Session,
    field_name: str | None = None,
    name_prefix: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, str | bool | None]]:
    query = db.query(User)
    if name_prefix:
        query = query.filter(User.name.ilike(f"{name_prefix}%"))

    users = query.order_by(User.name.asc()).offset(offset).limit(limit).all()
    details: list[dict[str, str | bool | None]] = []

    for user in users:
        if field_name:
            if field_name not in ALLOWED_FIELDS:
                raise ValueError("Invalid field_name.")
            details.append({"email": user.email, field_name: getattr(user, field_name)})
        else:
            details.append(
                {
                    "name": user.name,
                    "email": user.email,
                    "data1": user.data1,
                    "data2": user.data2,
                    "status_enabled": user.status_enabled,
                }
            )

    return details

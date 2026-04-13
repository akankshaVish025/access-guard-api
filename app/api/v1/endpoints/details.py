from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.query import DetailsQuery
from app.services.access_service import validate_token
from app.services.query_service import get_user_details

router = APIRouter(tags=["details"])


@router.get("/getdetails")
def get_details_endpoint(
    auth_token: str,
    field_name: str | None = None,
    name_prefix: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    try:
        query_payload = DetailsQuery(
            auth_token=auth_token,
            field_name=field_name,
            name_prefix=name_prefix,
            limit=limit,
            offset=offset,
        )
        access = validate_token(db, query_payload.auth_token)
        data = get_user_details(
            db=db,
            field_name=query_payload.field_name,
            name_prefix=query_payload.name_prefix,
            limit=query_payload.limit,
            offset=query_payload.offset,
        )
        return {
            "requested_by": access.email_id,
            "count": len(data),
            "items": data,
        }
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

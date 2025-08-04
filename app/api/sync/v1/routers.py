from collections.abc import Sequence

from core.dependencies import get_current_user
from fastapi import APIRouter, Depends
from schemas.user import UserOut
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.banco import Banco

router = APIRouter(
    prefix="/sync", tags=["Sync"], dependencies=[Depends(get_current_user)]
)


@router.post("/push", response_model=list[Banco])
def push(
    _: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Banco]:
    return None


@router.get("/pull", response_model=list[Banco])
def pull(
    _: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Banco]:
    return None


@router.post("/conflicts", response_model=list[Banco])
def conflicts(
    _: UserOut = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> Sequence[Banco]:
    return None

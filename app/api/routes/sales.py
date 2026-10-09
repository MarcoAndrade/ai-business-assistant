
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sale import SaleResponse
from app.services.sale_service import SaleService


router = APIRouter(prefix="/sales", tags=["Sales"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[SaleResponse])
def list_sales(
    db: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return SaleService(db).list(skip, limit)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: DbSession):
    try:
        return SaleService(db).get(sale_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.exceptions import (
    CustomerNotFoundError,
    InactiveProductError,
    InsufficientStockError,
    ProductNotFoundError,
)
from app.services.sale_service import SaleService


router = APIRouter(prefix="/sales", tags=["Sales"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale(data: SaleCreate, db: DbSession):
    try:
        return SaleService(db).create(data)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InactiveProductError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


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
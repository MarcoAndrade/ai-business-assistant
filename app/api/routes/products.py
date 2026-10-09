
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["Products"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(data: ProductCreate, db: DbSession):
    return ProductService(db).create(data)


@router.get("", response_model=list[ProductResponse])
def list_products(
    db: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    active: bool | None = None,
):
    return ProductService(db).list(skip, limit, active)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: DbSession):
    try:
        return ProductService(db).get(product_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: DbSession,
):
    try:
        return ProductService(db).update(product_id, data)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(product_id: int, db: DbSession):
    try:
        ProductService(db).deactivate(product_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.sale import Sale


class SaleRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_id: int) -> Sale | None:
        statement = (
            select(Sale)
            .options(selectinload(Sale.items))
            .where(Sale.id == sale_id)
        )

        return self.db.scalars(statement).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Sale]:
        statement = (
            select(Sale)
            .options(selectinload(Sale.items))
            .order_by(Sale.created_at.desc(), Sale.id.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())
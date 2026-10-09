
from sqlalchemy.orm import Session

from app.repositories.sale_repository import SaleRepository


class SaleService:

    def __init__(self, db: Session):
        self.repository = SaleRepository(db)

    def get(self, sale_id: int):
        sale = self.repository.get_by_id(sale_id)

        if sale is None:
            raise LookupError("Sale not found")

        return sale

    def list(self, skip: int = 0, limit: int = 20):
        return self.repository.list(skip, limit)
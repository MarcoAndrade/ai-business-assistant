
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    def create(self, data: ProductCreate):
        return self.repository.create(data)

    def get(self, product_id: int):
        product = self.repository.get_by_id(product_id)

        if product is None:
            raise LookupError("Product not found")

        return product

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        active: bool | None = None,
    ):
        return self.repository.list(skip, limit, active)

    def update(self, product_id: int, data: ProductUpdate):
        product = self.get(product_id)
        changes = data.model_dump(exclude_unset=True)

        for field, value in changes.items():
            if field != "description" and value is None:
                raise ValueError(f"{field} cannot be null")

        if not changes:
            raise ValueError("At least one field must be provided")

        return self.repository.update(product, data)

    def deactivate(self, product_id: int):
        product = self.get(product_id)

        if not product.active:
            return product

        return self.repository.update(
            product,
            ProductUpdate(active=False),
        )
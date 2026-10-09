
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        active: bool | None = None,
    ) -> list[Product]:
        statement = select(Product).offset(skip).limit(limit)

        if active is not None:
            statement = statement.where(Product.active == active)

        statement = statement.order_by(Product.id)

        return list(self.db.scalars(statement).all())

    def update(
        self,
        product: Product,
        data: ProductUpdate,
    ) -> Product:
        changes = data.model_dump(exclude_unset=True)

        for field, value in changes.items():
            setattr(product, field, value)

        self.db.commit()
        self.db.refresh(product)

        return product
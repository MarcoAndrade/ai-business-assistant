
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.product import Product


class InventoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_products_for_update(
        self,
        product_ids: list[int],
    ) -> dict[int, Product]:
        statement = (
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
        )

        products = self.db.scalars(statement).all()

        return {product.id: product for product in products}

    def decrement_stock(self, product_id: int, quantity: int) -> None:
        statement = (
            update(Product)
            .where(
                Product.id == product_id,
                Product.stock >= quantity,
                Product.active.is_(True),
            )
            .values(stock=Product.stock - quantity)
        )

        result = self.db.execute(statement)

        if result.rowcount != 1:
            raise RuntimeError(
                "Inventory changed unexpectedly during the transaction"
            )
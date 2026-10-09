
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


class SaleRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

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

    def create_sale(
        self,
        customer_id: int | None,
        items: list[dict],
        total: Decimal,
    ) -> Sale:
        sale = Sale(
            customer_id=customer_id,
            total=total,
            created_at=datetime.now(timezone.utc),
        )

        for item in items:
            sale.items.append(
                SaleItem(
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    subtotal=item["subtotal"],
                )
            )

        self.db.add(sale)
        self.db.flush()

        return sale

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
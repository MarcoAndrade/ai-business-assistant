
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.repositories.sale_repository import SaleRepository
from app.services.exceptions import (
    CustomerNotFoundError,
    InactiveProductError,
    InsufficientStockError,
    ProductNotFoundError,
)


CENT = Decimal("0.01")


class SaleService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = SaleRepository(db)

    def create(self, data):
        try:
            with self.db.begin():
                if data.customer_id is not None:
                    customer = self.repository.get_customer(
                        data.customer_id
                    )

                    if customer is None:
                        raise CustomerNotFoundError(
                            f"Customer {data.customer_id} not found"
                        )

                product_ids = sorted(
                    item.product_id for item in data.items
                )

                products = self.repository.get_products_for_update(
                    product_ids
                )

                prepared_items = []
                total = Decimal("0.00")

                for item in data.items:
                    product = products.get(item.product_id)

                    if product is None:
                        raise ProductNotFoundError(
                            f"Product {item.product_id} not found"
                        )

                    if not product.active:
                        raise InactiveProductError(
                            f"Product {product.id} is inactive"
                        )

                    if product.stock < item.quantity:
                        raise InsufficientStockError(
                            f"Product {product.name}: requested "
                            f"{item.quantity}, available {product.stock}"
                        )

                    unit_price = Decimal(product.price).quantize(
                        CENT,
                        rounding=ROUND_HALF_UP,
                    )

                    subtotal = (unit_price * item.quantity).quantize(
                        CENT,
                        rounding=ROUND_HALF_UP,
                    )

                    prepared_items.append({
                        "product_id": product.id,
                        "quantity": item.quantity,
                        "unit_price": unit_price,
                        "subtotal": subtotal,
                    })

                    total += subtotal

                total = total.quantize(
                    CENT,
                    rounding=ROUND_HALF_UP,
                )

                for item in prepared_items:
                    product = products[item["product_id"]]
                    product.stock -= item["quantity"]

                sale = self.repository.create_sale(
                    customer_id=data.customer_id,
                    items=prepared_items,
                    total=total,
                )

                self.db.flush()
                self.db.refresh(sale)

                sale_id = sale.id

            # El commit ocurre al salir correctamente del bloque begin().
            # Volvemos a consultar con las partidas cargadas.
            return self.repository.get_by_id(sale_id)

        except Exception:
            # El context manager revierte automáticamente la transacción
            # si se produce una excepción dentro del bloque.
            raise

    def get(self, sale_id: int):
        sale = self.repository.get_by_id(sale_id)

        if sale is None:
            raise LookupError("Sale not found")

        return sale

    def list(self, skip: int = 0, limit: int = 20):
        return self.repository.list(skip, limit)
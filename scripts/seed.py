from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Customer, Product


PRODUCTS = [
    {
        "name": "Café americano",
        "description": "Café americano de 350 ml",
        "price": Decimal("45.00"),
        "stock": 50,
        "active": True,
    },
    {
        "name": "Café latte",
        "description": "Café espresso con leche",
        "price": Decimal("60.00"),
        "stock": 30,
        "active": True,
    },
    {
        "name": "Hamburguesa",
        "description": "Hamburguesa clásica",
        "price": Decimal("120.00"),
        "stock": 20,
        "active": True,
    },
    {
        "name": "Refresco",
        "description": "Refresco de 355 ml",
        "price": Decimal("30.00"),
        "stock": 100,
        "active": True,
    },
    {
        "name": "Papas",
        "description": "Orden de papas fritas",
        "price": Decimal("45.00"),
        "stock": 15,
        "active": True,
    },
]

CUSTOMERS = [
    {
        "name": "Juan Pérez",
        "phone": "5550000001",
        "email": "juan@example.com",
    },
    {
        "name": "María López",
        "phone": "5550000002",
        "email": "maria@example.com",
    },
    {
        "name": "Carlos Hernández",
        "phone": "5550000003",
        "email": "carlos@example.com",
    },
]


def seed_products(session) -> int:
    inserted = 0

    for product_data in PRODUCTS:
        existing = session.scalar(
            select(Product).where(
                Product.name == product_data["name"]
            )
        )

        if existing is None:
            session.add(Product(**product_data))
            inserted += 1

    return inserted


def seed_customers(session) -> int:
    inserted = 0

    for customer_data in CUSTOMERS:
        existing = session.scalar(
            select(Customer).where(
                Customer.email == customer_data["email"]
            )
        )

        if existing is None:
            session.add(Customer(**customer_data))
            inserted += 1

    return inserted


def main() -> None:
    with SessionLocal() as session:
        try:
            products_inserted = seed_products(session)
            customers_inserted = seed_customers(session)

            session.commit()

            print("Seed ejecutado correctamente.")
            print(f"Productos nuevos: {products_inserted}")
            print(f"Clientes nuevos: {customers_inserted}")

        except Exception:
            session.rollback()
            raise

    print("Proceso finalizado.")


if __name__ == "__main__":
    main()
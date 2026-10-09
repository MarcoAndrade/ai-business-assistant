
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(**data.model_dump())

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        return customer

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Customer]:
        statement = (
            select(Customer)
            .order_by(Customer.id)
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        customer: Customer,
        data: CustomerUpdate,
    ) -> Customer:
        changes = data.model_dump(exclude_unset=True)

        for field, value in changes.items():
            setattr(customer, field, value)

        self.db.commit()
        self.db.refresh(customer)

        return customer
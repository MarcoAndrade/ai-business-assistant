
from sqlalchemy.orm import Session

from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:

    def __init__(self, db: Session):
        self.repository = CustomerRepository(db)

    def create(self, data: CustomerCreate):
        return self.repository.create(data)

    def get(self, customer_id: int):
        customer = self.repository.get_by_id(customer_id)

        if customer is None:
            raise LookupError("Customer not found")

        return customer

    def list(self, skip: int = 0, limit: int = 20):
        return self.repository.list(skip, limit)

    def update(self, customer_id: int, data: CustomerUpdate):
        customer = self.get(customer_id)
        changes = data.model_dump(exclude_unset=True)

        for field, value in changes.items():
            if field == "name" and value is None:
                raise ValueError("name cannot be null")

        if not changes:
            raise ValueError("At least one field must be provided")

        return self.repository.update(customer, data)
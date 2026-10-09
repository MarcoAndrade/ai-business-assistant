
import pytest
from pydantic import ValidationError

from app.schemas.sale import SaleCreate


def test_sale_requires_at_least_one_item():
    with pytest.raises(ValidationError):
        SaleCreate(items=[])


def test_sale_rejects_non_positive_quantity():
    with pytest.raises(ValidationError):
        SaleCreate(
            items=[
                {"product_id": 1, "quantity": 0}
            ]
        )


def test_sale_rejects_duplicate_products():
    with pytest.raises(ValidationError):
        SaleCreate(
            items=[
                {"product_id": 1, "quantity": 2},
                {"product_id": 1, "quantity": 3},
            ]
        )


def test_sale_accepts_valid_items():
    sale = SaleCreate(
        items=[
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1},
        ]
    )

    assert len(sale.items) == 2
    assert sale.items[0].quantity == 2
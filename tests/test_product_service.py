
from unittest.mock import Mock

import pytest

from app.schemas.product import ProductUpdate
from app.services.product_service import ProductService


def create_service():
    """Crea un servicio con un repositorio simulado."""
    service = ProductService(Mock())
    service.repository = Mock()
    return service


def test_get_product_not_found():
    service = create_service()
    service.repository.get_by_id.return_value = None

    with pytest.raises(LookupError, match="Product not found"):
        service.get(999)


def test_update_rejects_empty_payload():
    service = create_service()
    service.repository.get_by_id.return_value = Mock()

    payload = ProductUpdate()

    with pytest.raises(
        ValueError,
        match="At least one field must be provided",
    ):
        service.update(1, payload)


def test_update_rejects_null_price():
    service = create_service()
    service.repository.get_by_id.return_value = Mock()

    payload = ProductUpdate(price=None)

    with pytest.raises(ValueError, match="price cannot be null"):
        service.update(1, payload)

import pytest

from app.ai.request_handler import handle_request
from app.ai.structured_schemas import BusinessRequest
from app.ai.structured_output import extract_business_request


# Casos de evaluación del modelo.
# Estas pruebas sí realizan llamadas reales al proveedor configurado.
@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("Consulta el producto con ID 12.", "product_query"),
        ("¿Qué productos tienen 5 unidades o menos?", "inventory_query"),
        ("¿Cuánto costarían 3 unidades del producto 12?", "quote_sale"),
        ("Registra 3 unidades del producto 12.", "register_sale"),
        ("Quiero comprar varios cafés.", "clarification"),
        ("¿Cuánto vendimos el 8 de octubre de 2026?", "sales_report"),
    ],
)
def test_model_extracts_expected_intent(message, expected_intent):
    result = extract_business_request(message)

    assert result.intent == expected_intent


def test_inventory_threshold_extraction():
    result = extract_business_request(
        "¿Qué productos tienen 5 unidades o menos?"
    )

    assert result.intent == "inventory_query"
    assert result.inventory_threshold == 5


def test_product_query_extracts_product_id():
    result = extract_business_request("Consulta el producto con ID 12.")

    assert result.items[0].product_id == 12


def test_quote_extracts_product_and_quantity():
    result = extract_business_request(
        "¿Cuánto costarían 3 unidades del producto 12?"
    )

    assert result.intent == "quote_sale"
    assert result.items[0].product_id == 12
    assert result.items[0].quantity == 3


def test_sales_report_extracts_explicit_date():
    result = extract_business_request(
        "¿Cuánto vendimos el 8 de octubre de 2026?"
    )

    assert result.intent == "sales_report"
    assert result.target_date == "2026-10-08"


def test_business_request_accepts_valid_inventory_threshold():
    request = BusinessRequest(
        intent="inventory_query",
        inventory_threshold=5,
    )

    assert request.inventory_threshold == 5


def test_business_request_rejects_negative_inventory_threshold():
    with pytest.raises(ValueError):
        BusinessRequest(
            intent="inventory_query",
            inventory_threshold=-1,
        )


# Pruebas deterministas del handler: no necesitan llamar al LLM.
def test_handler_rejects_empty_message():
    result = handle_request("   ")

    assert result["status"] == "invalid_request"


def test_handler_requests_confirmation_for_sale(monkeypatch):
    request = BusinessRequest(
        intent="register_sale",
        items=[
            {
                "product_id": 12,
                "quantity": 3,
            }
        ],
    )

    monkeypatch.setattr(
        "app.ai.request_handler.extract_business_request",
        lambda message: request,
    )

    result = handle_request("Registra 3 unidades del producto 12.")

    assert result["status"] == "confirmation_required"


def test_handler_requests_clarification_when_information_is_missing(
    monkeypatch,
):
    request = BusinessRequest(
        intent="clarification",
        missing_information=["producto", "cantidad"],
    )

    monkeypatch.setattr(
        "app.ai.request_handler.extract_business_request",
        lambda message: request,
    )

    result = handle_request("Quiero comprar varios productos.")

    assert result["status"] == "needs_clarification"
    assert result["missing_information"] == ["producto", "cantidad"]


def test_handler_rejects_unsupported_request(monkeypatch):
    request = BusinessRequest(intent="unsupported")

    monkeypatch.setattr(
        "app.ai.request_handler.extract_business_request",
        lambda message: request,
    )

    result = handle_request("Cuéntame un chiste.")

    assert result["status"] == "unsupported"

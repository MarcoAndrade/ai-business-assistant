
from unittest.mock import patch

from app.ai.graph import assistant_graph
from app.ai.structured_schemas import (
    BusinessRequest,
    RequestedItem,
)


def test_empty_message_returns_clarification():
    result = assistant_graph.invoke({
        "user_message": "   "
    })

    assert result["route"] == "clarification"
    assert "Escribe una consulta" in result["response"]


def test_unsupported_request_does_not_execute_tools():
    request = BusinessRequest(intent="unsupported")

    with patch(
        "app.ai.graph_nodes.extract_business_request",
        return_value=request,
    ):
        result = assistant_graph.invoke({
            "user_message": "Dime el resultado de una carrera de caballos."
        })

    assert result["route"] == "unsupported"
    assert "fuera del alcance" in result["response"]


def test_register_sale_is_not_executed_automatically():
    request = BusinessRequest(
        intent="register_sale",
        items=[
            RequestedItem(
                product_id=12,
                quantity=3,
            )
        ],
    )

    with patch(
        "app.ai.graph_nodes.extract_business_request",
        return_value=request,
    ):
        result = assistant_graph.invoke({
            "user_message": "Registra 3 unidades del producto 12."
        })

    assert result["route"] == "prepare_sale"
    assert "todavía no se ha registrado" in result["response"]

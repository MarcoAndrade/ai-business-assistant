
from app.ai.graph_state import AssistantState
from app.ai.structured_output import extract_business_request
from app.ai.tools import (
    get_product,
    get_low_stock_products,
    get_daily_sales,
)


def interpret_request(state: AssistantState) -> dict:
    message = state["user_message"].strip()

    if not message or message.isspace():
        return {
            "route": "clarification",
            "response": "Escribe una consulta para poder ayudarte.",
            "missing_information": ["Mensaje del usuario"],
        }

    request = extract_business_request(message)

    return {
        "request": request.model_dump(mode="json"),
        "intent": request.intent,
        "missing_information": request.missing_information,
    }

def route_request(state: AssistantState) -> dict:
    request = state.get("request", {})
    intent = request.get("intent")
    missing = request.get("missing_information", [])

    if missing or intent == "clarification":
        return {"route": "clarification"}

    if intent == "unsupported":
        return {"route": "unsupported"}

    if intent in {
        "product_query",
        "inventory_query",
        "sales_report",
    }:
        return {"route": "read"}

    if intent == "quote_sale":
        return {"route": "quote"}

    if intent == "register_sale":
        return {"route": "prepare_sale"}

    return {"route": "clarification"}

def clarification_node(state: AssistantState) -> dict:
    missing_information = state.get("missing_information", [])

    if not state.get("user_message", "").strip():
        return {
            "route": "clarification",
            "response": "Escribe una consulta para que pueda ayudarte.",
        }

    if missing_information:
        missing = ", ".join(missing_information)
        return {
            "route": "clarification",
            "response": f"Necesito estos datos para continuar: {missing}.",
        }

    return {
        "route": "clarification",
        "response": "Necesito más información para procesar tu solicitud.",
    }

def unsupported_node(state: AssistantState) -> dict:
    return {
        "route": "unsupported",
        "response": (
            "Tu solicitud está fuera del alcance del asistente. "
            "Por ahora puedo ayudarte con productos, inventario, "
            "cotizaciones y reportes de ventas."
        )
    }

def prepare_sale_node(state: AssistantState) -> dict:
    return {
        "response": (
            "He interpretado tu solicitud de venta, pero todavía "
            "no se ha registrado. Primero validaré los productos "
            "y prepararé una confirmación."
        )
    }

def quote_node(state: AssistantState) -> dict:
    return {
        "response": (
            "He identificado una solicitud de cotización. "
            "Necesito consultar los productos y sus precios reales "
            "antes de calcular el importe."
        )
    }

def execute_read_tool(state: AssistantState) -> dict:
    request = state["request"]
    intent = request["intent"]

    try:
        if intent == "product_query":
            items = request.get("items", [])

            if not items or items[0].get("product_id") is None:
                return {
                    "route": "clarification",
                    "response": (
                        "Necesito el ID del producto para consultarlo."
                    ),
                }

            result = get_product.invoke({
                "product_id": items[0]["product_id"]
            })

        elif intent == "inventory_query":
            # Umbral predeterminado del MVP.
            # En una iteración posterior lo extraeremos del esquema.
            result = get_low_stock_products.invoke({
                "threshold": 5
            })

        elif intent == "sales_report":
            target_date = request.get("target_date")

            if not target_date:
                return {
                    "route": "clarification",
                    "response": "¿De qué fecha quieres el reporte?",
                }

            result = get_daily_sales.invoke({
                "date": target_date
            })

        else:
            return {
                "route": "clarification",
                "response": "No hay una herramienta disponible para esa solicitud.",
            }

        return {
            "tool_result": result,
            "route": "read_result",
        }

    except Exception:
        # En producción: registrar la excepción con logging.
        # No enviar detalles internos al usuario ni al modelo.
        return {
            "error_code": "tool_execution_failed",
            "route": "tool_error",
        }


def format_tool_result(state: AssistantState) -> dict:
    result = state.get("tool_result", {})

    if not isinstance(result, dict):
        return {
            "response": "La consulta terminó, pero devolvió un formato inesperado."
        }

    if result.get("found") is False:
        return {
            "response": "No encontré un producto con ese ID."
        }

    if result.get("success") is False:
        return {
            "response": result.get(
                "message",
                "No fue posible completar la consulta."
            )
        }

    if "stock" in result and "name" in result:
        return {
            "response": (
                f"El producto {result['name']} tiene "
                f"{result['stock']} unidades disponibles."
            )
        }

    if "products" in result and "threshold" in result:
        products = result["products"]

        if not products:
            return {
                "response": (
                    f"No hay productos activos con stock de "
                    f"{result['threshold']} unidades o menos."
                )
            }

        lines = [
            f"- {p['name']}: {p['stock']} unidades"
            for p in products
        ]

        return {
            "response": (
                "Productos con inventario bajo:\n"
                + "\n".join(lines)
            )
        }

    if "sales_count" in result and "total" in result:
        return {
            "response": (
                f"El {result['date']} se registraron "
                f"{result['sales_count']} ventas, por un total de "
                f"${result['total']}."
            )
        }

    return {
        "response": "La consulta se completó, pero no pude interpretar su resultado."
    }


def tool_error_node(state: AssistantState) -> dict:
    return {
        "response": (
            "No pude completar la consulta por un problema interno. "
            "Inténtalo nuevamente más tarde."
        )
    }

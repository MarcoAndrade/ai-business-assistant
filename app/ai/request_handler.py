from typing import Any

from app.ai.structured_output import extract_business_request
from app.ai.structured_schemas import BusinessRequest


def handle_request(message: str) -> dict[str, Any]:
    """
    Procesa una solicitud del usuario y determina el siguiente paso.

    No ejecuta consultas SQL ni registra ventas directamente.
    Las operaciones de negocio se delegarán posteriormente a las tools
    y los servicios correspondientes.
    """
    if not isinstance(message, str) or not message.strip():
        return {
            "status": "invalid_request",
            "message": "El mensaje no puede estar vacío.",
            "request": None,
        }

    try:
        request: BusinessRequest = extract_business_request(message)
    except (ValueError, RuntimeError) as exc:
        return {
            "status": "processing_error",
            "message": "No fue posible interpretar la solicitud.",
            "error": str(exc),
            "request": None,
        }

    request_data = request.model_dump(mode="json")

    if request.intent == "unsupported":
        return {
            "status": "unsupported",
            "message": (
                "La solicitud está fuera de las funciones "
                "disponibles del asistente."
            ),
            "request": request_data,
        }

    if request.intent == "clarification":
        return {
            "status": "needs_clarification",
            "message": "Necesito más información para entender tu solicitud.",
            "missing_information": request.missing_information,
            "request": request_data,
        }

    if request.missing_information:
        return {
            "status": "needs_clarification",
            "message": "Faltan datos para continuar.",
            "missing_information": request.missing_information,
            "request": request_data,
        }

    # Las operaciones que modifican datos requieren confirmación explícita.
    if request.intent == "register_sale":
        return {
            "status": "confirmation_required",
            "message": "Confirma los datos antes de registrar la venta.",
            "request": request_data,
        }

    return {
        "status": "ready",
        "message": "La solicitud está lista para procesarse.",
        "request": request_data,
    }

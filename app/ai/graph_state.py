from typing import TypedDict, Any


class AssistantState(TypedDict, total=False):
    # Entrada
    user_message: str

    # Resultado de Structured Output
    request: dict[str, Any]
    intent: str
    missing_information: list[str]

    # Control del flujo
    route: str

    # Resultado de una herramienta
    tool_result: dict[str, Any]

    # Respuesta final para el usuario
    response: str

    # Metadatos para trazabilidad
    error_code: str | None

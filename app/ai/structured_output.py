import json
import os
from dotenv import load_dotenv

from pydantic import ValidationError
from langchain_openai import ChatOpenAI

from app.ai.structured_schemas import BusinessRequest

load_dotenv()

llm = ChatOpenAI(
    model=os.environ["OPENROUTER_MODEL"],
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0,
)

structured_llm = llm.with_structured_output(
    BusinessRequest
)

SYSTEM_PROMPT = """
Eres un extractor de solicitudes para un asistente de negocios.

Devuelve únicamente un objeto JSON válido.
No uses Markdown ni bloques de código.

El objeto debe respetar este esquema conceptual:
{
  "intent": "product_query | inventory_query | sales_report |
             quote_sale | register_sale | clarification | unsupported",
  "items": [
    {
      "product_name": "string o null",
      "product_id": "entero o null",
      "quantity": "entero o null"
    }
  ],
  "target_date": "YYYY-MM-DD o null",
  "customer_id": "entero o null",
  "missing_information": ["string"],
  "requires_confirmation": false,
  "inventory_threshold": "entero o null"
}

Reglas:
1. No inventes IDs, cantidades, nombres, precios ni fechas.
2. No calcules precios ni totales.
3. Si un dato no está presente, usa null cuando corresponda.
4. Si la solicitud es ambigua, utiliza intent=clarification.
5. Si pregunta cuánto costaría algo sin pedir registrarlo,
   utiliza intent=quote_sale.
6. Si solicita registrar una venta, utiliza intent=register_sale.
7. Solicitar una venta no significa que ya se haya registrado.
8. Si faltan datos esenciales, enuméralos en missing_information.
9. Para reportes, extrae la fecha solo cuando esté explícita.
10. Para solicitudes ajenas al negocio, utiliza intent=unsupported.
11. Usa únicamente las intenciones permitidas en este prompt.
12. Incluye todos los campos del objeto, incluso cuando su valor sea null
    o una lista vacía.
13. En consultas de inventario, extrae el umbral numérico si el
    usuario lo especifica. No inventes un umbral si no lo menciona.
"""

def extract_business_request(
    message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> BusinessRequest:

    history = conversation_history or []

    context_lines = []

    for item in history[-8:]:
        role = item.get("role")
        content = item.get("content", "")

        if role in {"user", "assistant"} and content:
            context_lines.append(f"{role}: {content}")

    contextual_prompt = SYSTEM_PROMPT

    if context_lines:
        contextual_prompt += (
            "\n\nHistorial reciente:\n"
            + "\n".join(context_lines)
            + "\n\nUsa el historial únicamente para resolver "
            "referencias conversacionales. "
            "No lo consideres fuente de datos comerciales actuales."
        )

    response = structured_llm.invoke([
        ("system", contextual_prompt),
        ("human", message),
    ])

    if not isinstance(response, BusinessRequest):
        raise TypeError(
            "Se esperaba BusinessRequest, "
            f"pero se recibió {type(response).__name__}"
        )

    return response

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


def extract_business_request(message: str) -> BusinessRequest:
    response = llm.invoke(
        [
            ("system", SYSTEM_PROMPT),
            ("human", message),
        ]
    )

    content = response.content

    if not isinstance(content, str) or not content.strip():
        raise ValueError("El modelo devolvió una respuesta vacía.")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"El modelo no devolvió JSON válido: {content!r}"
        ) from exc

    try:
        return BusinessRequest.model_validate(data)
    except ValidationError as exc:
        raise ValueError(
            f"El JSON no cumple el esquema BusinessRequest: {exc}"
        ) from exc

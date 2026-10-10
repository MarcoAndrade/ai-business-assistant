
import json
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.environ["OPENROUTER_MODEL"],
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0,
)

response = llm.invoke(
    [
        (
            "system",
            'Devuelve únicamente un objeto JSON con las claves '
            '"intent" y "product_id". No agregues otras claves.',
        ),
        (
            "human",
            "Clasifica: Consulta el producto con ID 12. "
            "Usa intent=product_query y product_id=12.",
        ),
    ]
)

print("CONTENT:")
print(response.content)

print("\nFINISH REASON:")
print(response.response_metadata.get("finish_reason"))

print("\nJSON PARSE:")
try:
    parsed = json.loads(response.content)
    print(parsed)
except (json.JSONDecodeError, TypeError) as exc:
    print("La respuesta no es JSON válido:", exc)

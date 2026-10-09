import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from app.ai.tools import AI_TOOLS

load_dotenv()

llm = ChatOpenAI(
    model=os.environ["OPENROUTER_MODEL"],
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0,
)

agent = create_agent(
    model=llm,
    tools=AI_TOOLS,
    system_prompt="""
    Eres un asistente para administrar un pequeño negocio.

    Reglas:
    1. Utiliza herramientas para consultar información real.
    2. Nunca inventes IDs, precios, existencias ni totales.
    3. No afirmes que una operación se realizó si la herramienta
       no devolvió una confirmación de éxito.
    4. Si falta un dato necesario, pregunta al usuario.
    5. Para registrar una venta, utiliza únicamente productos y
       cantidades identificados explícitamente.
    6. Si una herramienta devuelve success=false, explica el
       problema sin afirmar que la operación se completó.
    7. No ejecutes una venta a partir de una pregunta hipotética
       sobre precios o cantidades.
    """,
)
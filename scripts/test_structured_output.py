from app.ai.structured_output import extract_business_request


examples = [
    "Consulta el producto con ID 12.",
    "¿Qué productos tienen 5 unidades o menos?",
    "¿Cuánto costarían 3 unidades del producto 12?",
    "Registra 3 unidades del producto 12.",
    "Quiero comprar varios cafés.",
    "¿Cuánto vendimos el 8 de octubre de 2026?",
]

for message in examples:
    print("\n" + "=" * 60)
    print("MENSAJE:", message)

    result = extract_business_request(message)

    print("INTENCIÓN:", result.intent)
    print("RESULTADO ESTRUCTURADO:")
    print(result.model_dump_json(indent=2))

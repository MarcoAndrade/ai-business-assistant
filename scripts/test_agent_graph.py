
from app.ai.graph import assistant_graph


def main():
    examples = [
        "Consulta el producto con ID 4.",
        "¿Qué productos tienen 5 unidades o menos?",
        "¿Cuánto vendimos el 8 de octubre de 2026?",
        "Registra 3 unidades del producto 12.",
        "Quiero comprar varios cafés.",
    ]

    for message in examples:
        print("\n" + "=" * 60)
        print("USUARIO:", message)

        result = assistant_graph.invoke({
            "user_message": message
        })

        print("INTENCIÓN:", result.get("intent"))
        print("RUTA:", result.get("route"))
        print("RESPUESTA:", result.get("response"))


if __name__ == "__main__":
    main()

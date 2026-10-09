from app.ai.agent import agent

response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Consulta el producto con ID 1 y dime su stock."
        }
    ]
})

for message in response["messages"]:
    if getattr(message, "type", None) == "ai":
        if message.content:
            print(message.content)
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.telegram_bot.handlers import handle_text_message


@pytest.mark.asyncio
async def test_text_message_returns_graph_response():
    # Arrange: mensaje de Telegram
    message = MagicMock()
    message.text = "Consulta el producto con ID 12."
    message.chat_id = 100
    message.chat.type = "private"
    message.reply_text = AsyncMock()

    # Arrange: usuario
    user = MagicMock()
    user.id = 12345

    update = MagicMock()
    update.effective_message = message
    update.effective_user = user

    # Arrange: grafo simulado
    mock_graph = MagicMock()

    # No existe historial previo
    mock_graph.get_state.return_value.values = {}

    # Respuesta simulada del grafo
    mock_graph.invoke.return_value = {
        "response": "El producto tiene 25 unidades disponibles."
    }

    # Arrange: contexto del bot
    context = MagicMock()
    context.bot.send_chat_action = AsyncMock()
    context.application.bot_data = {
        "assistant_graph": mock_graph
    }

    # Act
    with patch(
        "app.telegram_bot.handlers.authorize_user",
        new=AsyncMock(return_value=True),
    ):
        await handle_text_message(update, context)

    # Assert: respuesta enviada
    message.reply_text.assert_awaited_once_with(
        "El producto tiene 25 unidades disponibles."
    )

    # Assert: el grafo fue ejecutado
    mock_graph.invoke.assert_called_once()

    # Assert: historial persistido
    mock_graph.update_state.assert_called_once()

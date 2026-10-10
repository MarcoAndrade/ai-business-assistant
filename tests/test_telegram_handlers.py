from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.telegram_bot.handlers import handle_text_message


@pytest.mark.asyncio
async def test_text_message_returns_graph_response():
    message = MagicMock()
    message.text = "Consulta el producto con ID 12."
    message.chat_id = 100
    message.reply_text = AsyncMock()

    update = MagicMock()
    update.effective_message = message

    context = MagicMock()
    context.bot.send_chat_action = AsyncMock()

    with patch(
        "app.telegram_bot.handlers.authorize_user",
        new=AsyncMock(return_value=True),
    ), patch(
        "app.telegram_bot.handlers.assistant_graph.invoke",
        return_value={
            "response": "El producto tiene 25 unidades disponibles."
        },
    ):
        await handle_text_message(update, context)

    message.reply_text.assert_awaited_once_with(
        "El producto tiene 25 unidades disponibles."
    )

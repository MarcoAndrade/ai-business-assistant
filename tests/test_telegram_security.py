from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from telegram import Chat, Message, Update, User

from app.telegram_bot.security import authorize_user


@pytest.mark.asyncio
async def test_authorized_user_is_accepted():
    user = User(
        id=123456789,
        first_name="Authorized",
        is_bot=False,
    )

    chat = Chat(id=123456789, type="private")

    message = Message(
        message_id=1,
        date=datetime.now(),
        chat=chat,
        from_user=user,
        text="Consulta el inventario",
    )

    update = Update(update_id=1, message=message)

    with patch(
        "app.telegram_bot.security.get_allowed_user_ids",
        return_value={123456789},
    ):
        result = await authorize_user(update, None)

    assert result is True

@pytest.mark.asyncio
async def test_unauthorized_user_is_rejected():
    user = User(
        id=987654321,
        first_name="Unauthorized",
        is_bot=False,
    )

    chat = Chat(id=987654321, type="private")

    message = Message(
        message_id=2,
        date=datetime.now(),
        chat=chat,
        from_user=user,
        text="Consulta el inventario",
    )

    update = Update(update_id=2, message=message)

    with (
        patch(
            "app.telegram_bot.security.get_allowed_user_ids",
            return_value={123456789},
        ),
        patch.object(
            Message,
            "reply_text",
            new_callable=AsyncMock,
        ) as mock_reply,
    ):
        result = await authorize_user(update, None)

    assert result is False

    mock_reply.assert_awaited_once_with(
        "No tienes autorización para utilizar este asistente."
    )
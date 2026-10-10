from telegram import Update
from telegram.ext import ContextTypes

from app.telegram_bot.config import get_allowed_user_ids


async def authorize_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    user = update.effective_user

    if user is None:
        return False

    allowed_ids = get_allowed_user_ids()

    if user.id not in allowed_ids:
        if update.effective_message:
            await update.effective_message.reply_text(
                "No tienes autorización para utilizar este asistente."
            )

        return False

    return True

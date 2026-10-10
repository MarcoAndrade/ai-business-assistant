import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.telegram_bot.config import get_telegram_token
from app.telegram_bot.handlers import (
    start_command,
    help_command,
    id_command,
    handle_text_message,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# Reduce la verbosidad de las librerías HTTP.
logging.getLogger("httpx").setLevel(logging.WARNING)

async def post_init(application):
    from telegram import BotCommand

    await application.bot.set_my_commands([
        BotCommand("start", "Iniciar el asistente"),
        BotCommand("help", "Ver ayuda"),
        BotCommand("id", "Consultar tu ID de Telegram"),
    ])


def main() -> None:
    token = get_telegram_token()

    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start_command)
    )
    application.add_handler(
        CommandHandler("help", help_command)
    )
    application.add_handler(
        CommandHandler("id", id_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message,
        )
    )

    logging.info("Iniciando AI Business Assistant en Telegram.")

    application.run_polling()


if __name__ == "__main__":
    main()

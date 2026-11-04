import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.ai.memory import open_memory_graph
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


def main() -> None:
    token = get_telegram_token()

    with open_memory_graph() as graph:
        application = (
            Application.builder()
            .token(token)
            .build()
        )

        application.bot_data["assistant_graph"] = graph

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

        logging.info(
            "Iniciando AI Business Assistant con memoria Redis."
        )

        application.run_polling()


if __name__ == "__main__":
    main()

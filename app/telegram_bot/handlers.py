import asyncio
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from app.ai.graph import assistant_graph
from app.telegram_bot.security import authorize_user


logger = logging.getLogger(__name__)

MAX_TELEGRAM_MESSAGE_LENGTH = 4000


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not await authorize_user(update, context):
        return

    await update.effective_message.reply_text(
        "¡Hola! Soy AI Business Assistant.\n\n"
        "Puedo ayudarte a:\n"
        "• Consultar productos\n"
        "• Revisar inventario\n"
        "• Consultar reportes de ventas\n"
        "• Preparar cotizaciones\n\n"
        "Las solicitudes de venta no se ejecutarán "
        "sin una confirmación válida.\n\n"
        "Escribe /help para ver los comandos disponibles."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not await authorize_user(update, context):
        return

    await update.effective_message.reply_text(
        "Comandos disponibles:\n\n"
        "/start - Iniciar el asistente\n"
        "/help - Ver ayuda\n"
        "/id - Consultar tu ID de Telegram\n\n"
        "También puedes escribir una consulta en lenguaje natural."
    )


async def id_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    # Este comando solo revela el ID del propio remitente.
    user = update.effective_user

    if user is None or update.effective_message is None:
        return

    await update.effective_message.reply_text(
        f"Tu Telegram user ID es: {user.id}\n"
        "Agrégalo a TELEGRAM_ALLOWED_USER_IDS en tu .env."
    )


async def handle_text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not await authorize_user(update, context):
        return

    message = update.effective_message

    if message is None or not message.text:
        return

    user_message = message.text.strip()

    if not user_message:
        await message.reply_text("Escribe una consulta para continuar.")
        return

    try:
        await context.bot.send_chat_action(
            chat_id=message.chat_id,
            action=ChatAction.TYPING,
        )

        # LangGraph y sus tools son síncronos en esta implementación.
        # Ejecutarlos en un hilo evita bloquear el event loop de Telegram.
        result = await asyncio.to_thread(
            assistant_graph.invoke,
            {"user_message": user_message},
        )

        response = result.get(
            "response",
            "No pude generar una respuesta para esa solicitud.",
        )

        for start in range(0, len(response), MAX_TELEGRAM_MESSAGE_LENGTH):
            await message.reply_text(
                response[start:start + MAX_TELEGRAM_MESSAGE_LENGTH]
            )

    except Exception:
        logger.exception(
            "Error procesando una solicitud de Telegram"
        )

        await message.reply_text(
            "Ocurrió un problema al procesar tu solicitud. "
            "Inténtalo nuevamente más tarde."
        )

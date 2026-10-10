import os

from dotenv import load_dotenv


load_dotenv()

def get_telegram_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Falta la variable TELEGRAM_BOT_TOKEN."
        )

    return token

def get_allowed_user_ids() -> set[int]:
    raw_ids = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")

    if not raw_ids.strip():
        raise RuntimeError(
            "Debes configurar TELEGRAM_ALLOWED_USER_IDS."
        )

    try:
        return {
            int(value.strip())
            for value in raw_ids.split(",")
            if value.strip()
        }
    except ValueError as exc:
        raise RuntimeError(
            "TELEGRAM_ALLOWED_USER_IDS debe contener IDs numéricos."
        ) from exc

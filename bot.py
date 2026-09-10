import logging
import os
import random
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
PLAYERS = [
    "Marc-Andre ter Stegen",
    "Wojciech Szczesny",
    "Joan Garcia",
    "Ronald Araujo",
    "Pau Cubarsi",
    "Andreas Christensen",
    "Jules Kounde",
    "Alejandro Balde",
    "Eric Garcia",
    "Gerard Martin",
    "Pedri",
    "Gavi",
    "Frenkie de Jong",
    "Marc Casado",
    "Fermin Lopez",
    "Dani Olmo",
    "Lamine Yamal",
    "Raphinha",
    "Ferran Torres",
    "Robert Lewandowski",
    "Marcus Rashford",
]


def get_today_msk_str() -> str:
    """Возвращает дату по МСК в формате YYYY-MM-DD (сутки 00:00-00:00 МСК)."""
    return datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")


def get_player_for_user(user_id: int) -> str:
    today = get_today_msk_str()
    seed = f"{user_id}-{today}"
    rng = random.Random(seed)
    return rng.choice(PLAYERS)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.inline_query.from_user.id
    player = get_player_for_user(user_id)

    text = f"Сегодня я {player} 🔵🔴"

    result = InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="Кто ты из Барселоны сегодня?",
        description="Нажми, чтобы узнать",
        input_message_content=InputTextMessageContent(text),
        thumbnail_url="https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.png",
    )

    await update.inline_query.answer([result], cache_time=1, is_personal=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот \"Кто ты из Барселоны сегодня?\".\n\n"
        "Чтобы воспользоваться мной, в ЛЮБОМ чате (в том числе в этом) "
        "начни вводить @ИмяЭтогоБота — снизу появится подсказка, "
        "нажми на неё, и я скажу, кем ты сегодня являешься из состава Барсы. "
        "Результат сохраняется за тобой на все сутки (до 00:00 по Москве)."
    )


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден токен бота. Установи переменную окружения BOT_TOKEN "
            "(токен выдаёт @BotFather)."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))

    logger.info("Бот запущен, жду инлайн-запросы...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

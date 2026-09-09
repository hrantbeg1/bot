"""
Барселона-бот: инлайн-бот для Telegram.

Как это работает:
- Когда пользователь в ЛЮБОМ чате набирает "@ИмяБота " (тегает бота инлайн-режимом),
  Telegram показывает всплывающую подсказку снизу (как на скриншоте) — это
  стандартное поведение инлайн-ботов, ничего дополнительно верстать не нужно.
- Пользователь нажимает на подсказку, и бот отправляет сообщение вида
  "Сегодня я <Игрок>".
- Игрок выбирается детерминированно на основе user_id и текущей даты по
  московскому времени (МСК), поэтому один и тот же пользователь весь день
  (с 00:00 до 00:00 МСК) получает одного и того же игрока, сколько бы раз
  он ни вызывал бота. На следующий день (после 00:00 МСК) игрок обновится.

Запуск:
    1. pip install -r requirements.txt
    2. export BOT_TOKEN="твой_токен_от_BotFather"
    3. python bot.py

Настройка бота в BotFather (обязательно!):
    /setinline   -> включить инлайн-режим (задать placeholder, например
                    "Узнать, кто я сегодня из Барселоны")
    /setinlinefeedback -> можно поставить "Enabled", необязательно

Подробности — в README.md рядом с этим файлом.
"""

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

# Список игроков "Барселоны" (имена на английском). Отредактируй под
# актуальный состав — составы меняются каждое трансферное окно, поэтому
# список стоит проверять и обновлять самостоятельно (например, раз в сезон).
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
    """
    Детерминированно выбирает игрока для пользователя на текущие сутки МСК.
    Один user_id + одна дата всегда дают один и тот же результат.
    """
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

    # cache_time=1 — результат обновится максимум через секунду, но фактическая
    # "заморозка" игрока на сутки обеспечивается get_player_for_user, а не кэшем.
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

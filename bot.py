import asyncio
import logging
import signal

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile
)

from config import BOT_TOKEN
from services.screenshot import (
    make_progress_screenshot,
    make_balance_screenshot,
    make_success_screenshot
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

USER_STATE = {}

stop_event = asyncio.Event()


# ---------- КНОПКИ ----------
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Создать скриншот")],
        [KeyboardButton(text="💰 Баланс")],
        [KeyboardButton(text="✅ Успешный вывод")]
    ],
    resize_keyboard=True
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)


# ---------- START ----------
@dp.message(F.text == "/start")
async def start(message: Message):
    USER_STATE.pop(message.from_user.id, None)
    await message.answer(
        "🟢 Бот готов\n\nФОРМАТ ВСЕГДА ЧЕРЕЗ ЗАПЯТУЮ",
        reply_markup=main_kb
    )


# ---------- КНОПКИ ----------
@dp.message(F.text == "📊 Создать скриншот")
async def progress_btn(message: Message):
    USER_STATE[message.from_user.id] = "progress"
    await message.answer(
        "Введи одной строкой:\n"
        "Имя, Возраст, Процент\n\n"
        "Пример:\n"
        "John, 32, 78",
        reply_markup=back_kb
    )


@dp.message(F.text == "💰 Баланс")
async def balance_btn(message: Message):
    USER_STATE[message.from_user.id] = "balance"
    await message.answer(
        "Введи одной строкой:\n"
        "Имя, Баланс, Неудачная_сумма, Последняя_успешная\n\n"
        "Пример:\n"
        "Alex, 12500, 15000, 2300",
        reply_markup=back_kb
    )


@dp.message(F.text == "✅ Успешный вывод")
async def success_btn(message: Message):
    USER_STATE[message.from_user.id] = "success"
    await message.answer(
        "Введи одной строкой:\n"
        "Username, Баланс, Сумма, Карта, ФИО\n\n"
        "Пример:\n"
        "Dima, 12000, 5400, 4444333322221111, Ivan Ivanov",
        reply_markup=back_kb
    )


@dp.message(F.text == "⬅️ Назад")
async def back(message: Message):
    USER_STATE.pop(message.from_user.id, None)
    await message.answer("Меню", reply_markup=main_kb)


# ---------- ОБРАБОТКА ----------
@dp.message(F.text)
async def handle_input(message: Message):
    user_id = message.from_user.id
    state = USER_STATE.get(user_id)

    if not state:
        return

    text = message.text.replace(";", ",").strip()
    parts = [p.strip() for p in text.split(",") if p.strip()]

    try:
        if state == "progress":
            if len(parts) != 3:
                raise ValueError

            path = await make_progress_screenshot(
                parts[0],
                int(parts[1]),
                int(parts[2])
            )

        elif state == "balance":
    if len(parts) != 4:
        raise ValueError

    path = await make_balance_screenshot(
        parts[0],           # name
        int(parts[1]),      # balance
        int(parts[2]),      # failed_amount
        int(parts[3])       # last_success
    )

        elif state == "success":
            if len(parts) != 5:
                raise ValueError

            path = await make_success_screenshot(
                parts[0],
                int(parts[1]),
                int(parts[2]),
                parts[3],
                parts[4]
            )

        await message.answer_photo(
            FSInputFile(path),
            reply_markup=main_kb
        )

        USER_STATE.pop(user_id, None)

    except Exception as e:
        logging.exception(e)
        await message.answer(
            "❌ Ошибка генерации скриншота.\n"
            "Проблема НЕ в формате.\n"
            "Смотри логи сервера.",
            reply_markup=back_kb
        )


# ---------- RUN ----------
async def main():
    # 🔥 УБИРАЕТ старые вебхуки и прошлые сессии
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        handle_signals=False,     # 🔥 Railway-safe
        close_bot_session=True
    )


def shutdown():
    stop_event.set()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda s, f: shutdown())
    signal.signal(signal.SIGINT, lambda s, f: shutdown())

    async def runner():
        task = asyncio.create_task(main())
        await stop_event.wait()
        task.cancel()

    asyncio.run(runner())



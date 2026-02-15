from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📸 Создать скриншот", callback_data="screen")],
    [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
    [InlineKeyboardButton(text="✅ Успешный вывод", callback_data="success")],
    [InlineKeyboardButton(text="📱 Скрин ТГ", callback_data="tg")]  # ← ДОБАВИЛИ
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
])

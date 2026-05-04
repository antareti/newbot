import asyncio
import re
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM"
CHANNEL_ID = "@hackpackposter" 
MY_ADMIN_ID = 7917303098  # Ваш ID установлен

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- ФУНКЦИИ УТИЛИТЫ ---

def clean_and_style(text: str) -> str:
    if not text: return ""
    # Удаляем чужие ссылки и юзернеймы
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    # Добавляем вашу подпись
    signature = "\n\n<b>💀 Доступ открыт в: @hackpackposter</b>"
    return text.strip() + signature

def get_post_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👍", callback_data="like"),
        types.InlineKeyboardButton(text="👎", callback_data="dislike")
    )
    builder.row(types.InlineKeyboardButton(text="📡 Поделиться", url="https://t.me/share/url?url=https://t.me/hackpackposter"))
    return builder.as_markup()

# --- ОБРАБОТЧИКИ ---

# СЛЕЖКА: Срабатывает на новых пользователей
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    # Отправляем отчет вам в личку
    report = (
        f"🚨 <b>ОБЪЕКТ ЗАФИКСИРОВАН</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"<b>Имя:</b> {message.from_user.full_name}\n"
        f"<b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"<b>Username:</b> @{message.from_user.username or 'скрыт'}\n"
        f"<b>Язык:</b> {message.from_user.language_code}\n"
        f"━━━━━━━━━━━━━━"
    )
    await bot.send_message(MY_ADMIN_ID, report)
    
    # Ответ пользователю
    await message.answer("🦾 <b>Система верификации BITSNIFFER.</b>\nВаш узел связи проверен. Доступ разрешен.")

# ПОСТИНГ: Срабатывает, когда вы пересылаете контент боту
@dp.message()
async def posting_handler(message: types.Message):
    # Проверка, что пишет именно Хозяин
    if message.from_user.id == MY_ADMIN_ID:
        try:
            text = clean_and_style(message.text or message.caption or "")
            kb = get_post_kb()

            if message.text:
                await bot.send_message(CHANNEL_ID, text, reply_markup=kb)
            elif message.photo:
                await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=text, reply_markup=kb)
            elif message.video:
                await bot.send_video(CHANNEL_ID, message.video.file_id, caption=text, reply_markup=kb)
            elif message.document:
                await bot.send_document(CHANNEL_ID, message.document.file_id, caption=text, reply_markup=kb)

            await message.answer("🚀 <b>Пост уникализирован и отправлен!</b>")
        except Exception as e:
            await message.answer(f"❌ Ошибка публикации: {e}")
    else:
        # Если пишет кто-то другой, бот тихо докладывает вам
        await bot.send_message(MY_ADMIN_ID, f"📩 <b>Перехват сообщения от @{message.from_user.username}:</b>\n{message.text or 'Медиафайл'}")

@dp.callback_query()
async def reactions(callback: types.CallbackQuery):
    await callback.answer("Голос принят!")

async def main():
    print(f"--- СИСТЕМА BITSNIFFER ONLINE ---")
    print(f"HOST ID: {MY_ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

